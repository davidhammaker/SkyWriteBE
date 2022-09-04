from django.urls import path

from sky_write_app import views

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
    )
]
