from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class DefaultStorage(models.TextChoices):
    """Enum for all possible storage options."""

    DROPBOX = "DX", _("Dropbox")

    __empty__ = _("(Not selected)")


class CustomConfig(models.Model):
    user = models.OneToOneField(
        User,
        related_name="custom_config",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    encryption_key = models.TextField(blank=False, null=False)
    dropbox_token = models.TextField(
        blank=True,
        null=True,
        help_text="Dropbox refresh token",
    )

    default_storage = models.CharField(
        max_length=2,
        choices=DefaultStorage.choices,
    )
