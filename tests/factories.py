import factory.fuzzy
from django.contrib.auth import models as auth_models
from django.db.models.signals import post_save
from django_countries import countries

from addresses_service.apps.addresses import models as addresses_models


@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = auth_models.User

    username = factory.Sequence(lambda n: "user_%d" % n)


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = addresses_models.Address

    user = factory.SubFactory(UserFactory)
    full_name = factory.Faker("name")
    line_1 = factory.Faker("street_address")
    city = factory.Faker("city")
    state_or_region = factory.Faker("state")
    postal_code = factory.Faker("zipcode")
    country = factory.fuzzy.FuzzyChoice(
        countries.countries.items(), lambda choice: choice[0]
    )
