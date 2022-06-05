# isort: skip_file
from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication,
    TokenMatchesOASRequirements,
)
from rest_framework import viewsets

from .models import Address
from .serializers import AddressSerializer
from ..base.pagination import HalPageNumberPagination


class AddressesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows addresses to be viewed or edited.
    """

    queryset = Address.objects.all()
    pagination_class = HalPageNumberPagination
    serializer_class = AddressSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["addresses", "read"]],
        "POST": [["addresses", "write"]],
        "PUT": [["addresses", "write"]],
        "DELETE": [["addresses", "delete"]],
    }

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
