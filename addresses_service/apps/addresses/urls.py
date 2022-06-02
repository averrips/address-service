from rest_framework import routers

from addresses_service.apps.addresses import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"addresses/?", views.AddressesViewSet)
