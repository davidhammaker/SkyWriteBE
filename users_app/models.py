from django.contrib.auth.models import User
from django.db import models


class EncryptionKey(models.Model):
    user = models.OneToOneField(
        User,
        related_name="encryption_key",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    key = models.TextField(blank=False, null=False)


class DropboxAccess(models.Model):
    user = models.OneToOneField(
        User,
        related_name="dropbox_access",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    use_dropbox = models.BooleanField(default=False)
    token = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Dropbox Access Tokens"
