from django.contrib import admin

from sky_write_app.models import StorageObject


@admin.register(StorageObject)
class StorageObjectAdmin(admin.ModelAdmin):
    model = StorageObject
    list_display = ["name", "user_id", "folder_id", "is_file"]
