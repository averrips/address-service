import json

import pytest
from django.db import models
from django.test.client import RequestFactory
from rest_framework import reverse

from addresses_service.apps.base.serializers import HalModelSerializer


class Parent(models.Model):
    name = models.CharField()

    class Meta:
        app_label = "tests"


class Child(models.Model):
    name = models.CharField()
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)

    class Meta:
        app_label = "tests"


@pytest.fixture
def fake_reverse(monkeypatch):
    def fake(viewname, args=None, kwargs=None, request=None, format=None, **extra):
        return f"http://localhost/{viewname}/{kwargs.get('pk')}"

    monkeypatch.setattr(reverse, "_reverse", fake)


def test_hal_serializer(fake_reverse):
    class TestModelSerializer(HalModelSerializer):
        class Meta:
            model = Child
            fields = ("name", "parent")

    request = RequestFactory().request()
    data = TestModelSerializer(context={"request": request}).to_representation(
        Child(pk=1, name="Henry", parent=Parent(id=2, name="James"))
    )

    assert data == {
        "name": "Henry",
        "parent": 2,
        "_links": {"self": {"href": "http://localhost/child-detail/1"}},
    }


def test_hal_serializer_with_embedded(fake_reverse):
    class TestModelSerializer(HalModelSerializer):
        class Meta:
            model = Child
            fields = ("name", "parent")
            depth = 2

    request = RequestFactory().request()
    data = TestModelSerializer(context={"request": request}).to_representation(
        Child(pk=1, name="Henry", parent=Parent(id=2, name="James"))
    )

    assert data == {
        "name": "Henry",
        "parent": 2,
        "_links": {"self": {"href": "http://localhost/child-detail/1"}},
        "_embedded": {
            "parent": {
                "id": 2,
                "name": "James",
                "_links": {"self": {"href": "http://localhost/parent-detail/2"}},
            }
        },
    }, json.dumps(data, indent=4)
