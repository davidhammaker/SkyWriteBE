from django.contrib import admin

from sky_write_app.models import EncryptionKey, StorageObject


@admin.register(StorageObject)
class StorageObjectAdmin(admin.ModelAdmin):
    model = StorageObject
    list_display = ["name", "user_id", "folder_id", "is_file"]


@admin.register(EncryptionKey)
class EncryptionKeyAdmin(admin.ModelAdmin):
    model = EncryptionKey
    list_display = ["user_id"]
