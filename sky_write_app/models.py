from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models


class StorageObject(models.Model):
    name = models.TextField(blank=False, null=False)
    name_iv = models.TextField(blank=True, null=True)
    content_iv = models.TextField(blank=True, null=True)
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
    file_uuid = models.UUIDField(default=uuid4)
    ordering_parameter = models.DecimalField(
        max_digits=26,
        decimal_places=11,
        blank=True,
        null=False,
    )
