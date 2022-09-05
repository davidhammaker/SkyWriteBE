from django.contrib import admin

from sky_write_app.models import DropboxAccess, EncryptionKey, StorageObject


@admin.register(StorageObject)
class StorageObjectAdmin(admin.ModelAdmin):
    model = StorageObject
    list_display = ["name", "user_id", "folder_id", "is_file"]


@admin.register(EncryptionKey)
class EncryptionKeyAdmin(admin.ModelAdmin):
    model = EncryptionKey
    list_display = ["user_id"]


@admin.register(DropboxAccess)
class DropboxAccessAdmin(admin.ModelAdmin):
    model = DropboxAccess
    list_display = ["username", "user_id", "use_dropbox"]

    @staticmethod
    def username(obj):
        return obj.user.username
