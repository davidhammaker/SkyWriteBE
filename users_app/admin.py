from django.contrib import admin

from users_app.models import CustomConfig


@admin.register(CustomConfig)
class CustomConfigAdmin(admin.ModelAdmin):
    model = CustomConfig
    list_display = ["username", "user_id", "default_storage"]

    @staticmethod
    def username(obj):
        return obj.user.username
