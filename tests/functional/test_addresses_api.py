import datetime

import factory.random
import faker
import pytest
from oauth2_provider.models import Application
from pytz import utc
from rest_framework.test import APIClient

from addresses_service.apps.addresses.models import Address
from tests.factories import AddressFactory, UserFactory

fake = faker.Faker()


@pytest.fixture()
def user(db):
    user = UserFactory.create()
    user.set_password("secret")
    user.save()
    return user


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def auth_code_token(db, user):
    app = Application.objects.create(
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        redirect_uris="",
        name="test-token",
        user=user,
    )
    return user.oauth2_provider_accesstoken.create(
        application=app,
        expires=(datetime.datetime.now() + datetime.timedelta(minutes=15)).replace(
            tzinfo=utc
        ),
        token="token",
    )


@pytest.fixture()
def authenticated_client(api_client, auth_code_token):
    def set_scope(*scopes: str):
        auth_code_token.scope = " ".join(scopes)
        auth_code_token.save()

    client = APIClient()
    client.credentials(Authorization=f"Bearer {auth_code_token.token}")

    # Test helpers
    client.token = auth_code_token
    client.token.set_scope = set_scope
    return client


class TestAuthRequired:
    def test__get_addresses__unauthorized(self, api_client):
        resp = api_client.get("/api/addresses")
        assert resp.status_code == 401

    def test__get_address__unauthorized(self, api_client):
        resp = api_client.get("/api/addresses/1")
        assert resp.status_code == 401

    def test__post_address__unauthorized(self, api_client):
        resp = api_client.post("/api/addresses")
        assert resp.status_code == 401

    def test__put_address__unauthorized(self, api_client):
        resp = api_client.put("/api/addresses/1")
        assert resp.status_code == 401

    def test__delete_address__unauthorized(self, api_client):
        resp = api_client.delete("/api/addresses/1")
        assert resp.status_code == 401


class TestScopesRequired:
    def test__get_addresses__forbidden(self, authenticated_client):
        resp = authenticated_client.get("/api/addresses")
        assert resp.status_code == 403

    def test__get_address__forbidden(self, authenticated_client):
        resp = authenticated_client.get("/api/addresses/1")
        assert resp.status_code == 403

    def test__post_address__forbidden(self, authenticated_client):
        resp = authenticated_client.post("/api/addresses")
        assert resp.status_code == 403

    def test__put_address__forbidden(self, authenticated_client):
        resp = authenticated_client.put("/api/addresses/1")
        assert resp.status_code == 403

    def test__delete_address__forbidden(self, authenticated_client):
        resp = authenticated_client.delete("/api/addresses/1")
        assert resp.status_code == 403


class TestGetAddressesEndpoint:
    @pytest.fixture(autouse=True)
    def set_scope(self, authenticated_client):
        authenticated_client.token.set_scope("read", "addresses")

    def test_get_addresses(self, authenticated_client):
        AddressFactory.create_batch(10, user=authenticated_client.token.user)
        resp = authenticated_client.get("/api/addresses")
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert len(data["_embedded"]) == 10

    def test__get_addresses__only_own_addresses(self, authenticated_client):
        own_address = AddressFactory(user=authenticated_client.token.user)
        AddressFactory()  # Other address, from another user
        resp = authenticated_client.get("/api/addresses")
        assert resp.status_code == 200, resp.json()
        assert [address["id"] for address in resp.json()["_embedded"]] == [
            str(own_address.pk)
        ]


class TestGetAddressEndpoint:
    @pytest.fixture(autouse=True)
    def set_scope(self, authenticated_client):
        authenticated_client.token.set_scope("read", "addresses")

    def test__get_address(self, authenticated_client):
        factory.random.reseed_random(0)  # Ensure we have a reproducible test

        own_address = AddressFactory(
            user=authenticated_client.token.user,
        )
        resp = authenticated_client.get(f"/api/addresses/{own_address.pk}")
        assert resp.status_code == 200, resp.json()
        data = resp.json()
        assert data == {
            "_links": {
                "self": {"href": f'http://testserver/api/addresses/{data["id"]}'}
            },
            "id": data["id"],
            "type": "M",
            "city": "Vanessaside",
            "country": "SY",
            "county": "",
            "district": "",
            "full_name": "Norma Fisher",
            "line_1": "764 Howard Forge Apt. 421",
            "line_2": None,
            "line_3": None,
            "phone": "",
            "postal_code": "79393",
            "state_or_region": "Virginia",
        }

    def test__get_address__only_own_addresses(self, authenticated_client):
        own_address = AddressFactory(user=authenticated_client.token.user)
        other_address = AddressFactory()

        assert (
            authenticated_client.get(f"/api/addresses/{own_address.pk}").status_code
            == 200
        )
        assert (
            authenticated_client.get(f"/api/addresses/{other_address.pk}").status_code
            == 404
        )


class TestPostAddressEndpoint:
    @pytest.fixture(autouse=True)
    def set_scope(self, authenticated_client):
        authenticated_client.token.set_scope("write", "addresses")

    def test__post_address(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/addresses",
            data={
                "full_name": fake.name(),
                "line_1": fake.street_address(),
                "postal_code": fake.postalcode(),
                "city": fake.city(),
                "state_or_region": fake.state(),
                "country": fake.country_code(),
                "phone": fake.phone_number()[:20],
            },
        )
        assert resp.status_code == 201, resp.json()
        # No user was explicitly provided, it was set automatically
        assert Address.objects.filter(user=authenticated_client.token.user).count() == 1

    def test__post_address__validation_error(self, authenticated_client):
        resp = authenticated_client.post("/api/addresses", data={})
        assert resp.status_code == 400, resp.json()
        assert resp.json() == {
            "city": ["This field is required."],
            "country": ["This field is required."],
            "full_name": ["This field is required."],
            "line_1": ["This field is required."],
            "phone": ["This field is required."],
            "postal_code": ["This field is required."],
            "state_or_region": ["This field is required."],
        }


class TestPutAddressEndpoint:
    @pytest.fixture(autouse=True)
    def set_scope(self, authenticated_client):
        authenticated_client.token.set_scope("write", "addresses")

    def test__put_address(self, authenticated_client):
        address = AddressFactory(user=authenticated_client.token.user)
        resp = authenticated_client.put(
            f"/api/addresses/{address.pk}",
            data={
                "full_name": fake.name(),
                "line_1": fake.street_address(),
                "postal_code": fake.postalcode(),
                "city": fake.city(),
                "state_or_region": fake.state(),
                "country": fake.country_code(),
                "phone": fake.phone_number()[:20],
            },
        )
        assert resp.status_code == 200, resp.json()
        updated_address = Address.objects.get(pk=address.pk)
        assert address.updated_at != updated_address.updated_at

    def test__put_address_only_own(self, authenticated_client):
        address = AddressFactory()  # User not set: will be someone else

        assert (
            authenticated_client.put(f"/api/addresses/{address.pk}").status_code == 404
        )
        not_updated_address = Address.objects.get(pk=address.pk)
        assert not_updated_address.updated_at == address.updated_at


class TestDeleteAddress:
    @pytest.fixture(autouse=True)
    def set_scope(self, authenticated_client):
        authenticated_client.token.set_scope("delete", "addresses")

    def test__delete_address(self, authenticated_client):
        # Create multiple, as to ensure we delete only one
        [address_1, address_2] = AddressFactory.create_batch(
            2, user=authenticated_client.token.user
        )

        assert (
            authenticated_client.delete(f"/api/addresses/{address_1.pk}").status_code
            == 204
        )
        # Ensure only the first was really deleted
        with pytest.raises(Address.DoesNotExist):
            address_1.refresh_from_db()
        address_2.refresh_from_db()

    def test__delete_address__only_own_addresses(self, authenticated_client):
        other_address = AddressFactory()  # User not set: will be someone else

        assert (
            authenticated_client.delete(
                f"/api/addresses/{other_address.pk}"
            ).status_code
            == 404
        )
        other_address.refresh_from_db()  # Be sure it is still present in the database
