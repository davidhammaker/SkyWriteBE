from django.contrib.auth.models import User
from django.db import models


class StorageObject(models.Model):
    name = models.TextField(blank=False, null=False)
    name_iv = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User,
        related_name="storage_objects",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    folder = models.ForeignKey(
        "StorageObject",
        related_name="contents",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    is_file = models.BooleanField(default=True)


class EncryptionKey(models.Model):
    user = models.OneToOneField(
        User,
        related_name="encryption_key",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    key = models.TextField(blank=False, null=False)
