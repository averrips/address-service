from rest_framework.fields import URLField, empty
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.utils.field_mapping import get_nested_relation_kwargs


class HalLinkSerializer(Serializer):
    href = URLField()


class HalModelSerializer(ModelSerializer):
    """
    Serializer that represents resources in Hypertext Application Language (HAL).
    This allows resources to have _links and nested models to appear under an _embedded key.
    See https://datatracker.ietf.org/doc/html/draft-kelly-json-hal-00.

    Implement `get_hal_links(self, instance)` method to return a dictionary of _links to embed for each instance.
    """

    url_field_name = "__url__"

    def __init__(self, instance=None, data=empty, **kwargs):
        self._embedded = {}
        super().__init__(instance, data, **kwargs)

    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)
        if self.url_field_name not in list(fields):
            fields += (self.url_field_name,)
        return fields

    def get_hal_links(self, instance):
        return {}

    def to_representation(self, instance):
        result = super().to_representation(instance)
        self_url = result.pop(self.url_field_name)

        result["_links"] = {
            "self": HalLinkSerializer().to_representation({"href": self_url})
        } | self.get_hal_links(instance)

        embedded = {}
        for key in self._embedded:
            nested = result.pop(key)
            embedded[key] = nested
            result[key] = nested["id"]

        if embedded:
            result["_embedded"] = embedded

        return result

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """Ensure all nested fields are also based on the HalModelSerializer"""

        class NestedSerializer(HalModelSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = "__all__"

        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)
        # We will want to embed this field later (see to_representation).
        # For now, just add/register it to the _embedded key, we'll pick it up last moment.
        self._embedded[field_name] = None
        return field_class, field_kwargs
