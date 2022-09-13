from django.urls import path

from sky_write_django.settings import DBX_RESOLUTION_PATH_NAME
from users_app import views

urlpatterns = [
    path(
        "encryption_key/",
        views.KeyCreationView.as_view(),
        name="key-creation-view",
    ),
    path(
        "config/",
        views.ConfigRetrieveView.as_view(),
        name="dropbox-auth-start",
    ),
    path(
        "storage_options/",
        views.StorageOptionsView.as_view(),
        name="storage-options",
    ),
    path(
        "dropbox_resolution/",
        views.DropboxResolutionView.as_view(),
        name=DBX_RESOLUTION_PATH_NAME,
    ),
]
