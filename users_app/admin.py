from django.contrib import admin

from users_app.models import DropboxAccess, EncryptionKey


@admin.register(EncryptionKey)
class EncryptionKeyAdmin(admin.ModelAdmin):
    model = EncryptionKey
    list_display = ["username", "user_id"]

    @staticmethod
    def username(obj):
        return obj.user.username


@admin.register(DropboxAccess)
class DropboxAccessAdmin(admin.ModelAdmin):
    model = DropboxAccess
    list_display = ["username", "user_id", "use_dropbox"]

    @staticmethod
    def username(obj):
        return obj.user.username
