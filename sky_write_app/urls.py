from django.urls import path

from sky_write_app import views
from sky_write_django.settings import DBX_RESOLUTION_PATH_NAME

urlpatterns = [
    path("me/", views.MeView.as_view(), name="me"),
    path(
        "storage_objects/",
        views.StorageObjectView.as_view(),
        name="storage-object-view",
    ),
    path(
        "storage_objects/<int:pk>/",
        views.StorageObjectDetailView.as_view(),
        name="storage-object-detail-view",
    ),
    path(
        "encryption_key/",
        views.KeyCreationView.as_view(),
        name="key-creation-view",
    ),
    path(
        "dropbox_auth/",
        views.DropboxAuthStartView.as_view(),
        name="dropbox-auth-start",
    ),
    path(
        "dropbox_resolution/",
        views.DropboxResolutionView.as_view(),
        name=DBX_RESOLUTION_PATH_NAME,
    ),
]
