from django.contrib.auth.models import User
from django.db import models


class StorageObject(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
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
