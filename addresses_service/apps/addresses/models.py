import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _
from django_countries.fields import CountryField

from addresses_service.apps.base.models import BaseModel


class Address(BaseModel):
    """
    The hard part with addresses is that international standards are very diverse.

    Although some validation and data mapping is necessary too keep our data somewhat clean, proper validation
    strategies need to be implemented per country and will rarely suffice.

    This database model therefore makes sure that we can store all the different attributes of addresses, including
    the more free-form properties (based on the combination of these fields) about how they should best be displayed
    (something customers usually know best, or can alternatively be implemented relying on a specialized third-party
     service / API).

    The amount of validation you will want to do will be depending on your product and whether customers are entering
    their own addresses, since they will likely find it more difficult to enter addresses correctly for other countries
    where formatting standards differ.

    Note: the country selection relies on the ISO 3166-1 standard. Addresses in historical and non-recognized countries
    are not available.
    """

    ADDRESS_TYPE_MAILING = "M"
    ADDRESS_TYPE_BILLING = "B"
    ADDRESS_TYPE_CHOICES = (
        (ADDRESS_TYPE_MAILING, _("Mailing address")),
        (ADDRESS_TYPE_BILLING, _("Billing address")),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    type = models.CharField(
        choices=ADDRESS_TYPE_CHOICES,
        max_length=1,
        db_index=True,
        default=ADDRESS_TYPE_MAILING,
    )
    full_name = models.CharField(max_length=120)
    line_1 = models.CharField(max_length=120)
    line_2 = models.CharField(null=True, blank=True, max_length=60)
    line_3 = models.CharField(null=True, blank=True, max_length=60)
    city = models.CharField(max_length=100)
    county = models.CharField(blank=True, max_length=50)
    district = models.CharField(blank=True, max_length=50)
    state_or_region = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = CountryField()
    phone = models.CharField(blank=False, max_length=20)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "addresses"
        # Addresses should be unique per user
        unique_together = (
            "user",
            "full_name",
            "line_1",
            "city",
            "postal_code",
            "country",
        )
