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
        "folder/",
        views.RootContentsView.as_view(),
        name="root-contents-view",
    ),
    path(
        "folder/<int:pk>/",
        views.FolderContentsView.as_view(),
        name="folder-contents-view",
    ),
    path(
        "re_order/",
        views.StorageObjectReOrderView.as_view(),
        name="storage-object-re-order-view",
    ),
    path(
        "re_organize/",
        views.StorageObjectReOrganizeView.as_view(),
        name="storage-object-re-organize-view",
    ),
]
