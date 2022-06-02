from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from addresses_service.apps.addresses import models


class AddressSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = (
            "id",
            "type",
            "full_name",
            "line_1",
            "line_2",
            "line_3",
            "city",
            "county",
            "district",
            "state_or_region",
            "postal_code",
            "country",
            "phone",
        )
