from django.contrib.auth.models import User
from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sky_write_app.models import DropboxAccess, StorageObject
from sky_write_app.serializers import (
    KeySerializer,
    MeSerializer,
    StorageObjectSerializer,
)
from sky_write_app.utils import format_path, get_dropbox_auth_flow, get_storage_name
from sky_write_django.settings import SECRET_KEY


class MeView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def get(request):
        return Response(MeSerializer(request.user).data)


class StorageObjectView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = StorageObjectSerializer

    def get_queryset(self):
        return StorageObject.objects.filter(user=self.request.user).all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            folder_id = self.request.data.get("folder_id")
            path = get_storage_name(self.request.data["name"])
            if folder_id is not None:
                folder = StorageObject.objects.filter(id=folder_id).first()
                if folder is None:
                    return Response(
                        {"detail": f"StorageObject {folder_id} does not exist."},
                        400,
                    )
                folder_path = format_path(folder)
                path = f"{folder_path}/{path}"
            similar_objects = StorageObject.objects.filter(
                user_id=self.request.user.id,
                folder_id=folder_id,
                name=self.request.data["name"],
            ).all()
            for obj in similar_objects:
                if format_path(obj) == path:
                    # This may be irrelevant... With encrypted file
                    # names, duplicates are super unlikely and wouldn't
                    # matter anyway. Besides, this only spots duplicate
                    # encrypted names, not duplicate real names.
                    return Response({"detail": "Duplicate file."}, 400)
            serializer.save(
                user_id=request.user.id,
                folder=StorageObject.objects.filter(id=folder_id).first(),
            )
            return Response(serializer.data, 201)
        return Response({"detail": serializer.errors}, 400)


class StorageObjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = StorageObjectSerializer

    def get_queryset(self):
        return StorageObject.objects.filter(user=self.request.user).all()


class KeyCreationView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = KeySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user_id=request.user.id,
                key=request.data.get("key"),
            )
            return Response(serializer.data, 201)
        return Response({"detail": serializer.errors}, 400)


class DropboxAuthStartView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def get(request):
        return Response(
            {
                "detail": (
                    # We pass the ``url_state`` kwarg to ``start()`` to
                    # persist the user ID through the auth flow. The
                    # Dropbox API attaches this to the ``state``,
                    # preceded by a ``|`` pipe.
                    get_dropbox_auth_flow(request).start(url_state=str(request.user.id))
                )
            }
        )


class DropboxResolutionView(views.APIView):
    @staticmethod
    def get(request):
        code = request.GET.get("code")
        # The ``state`` query param holds the user ID; the two are
        # separated by a ``|`` pipe.
        state, user_id = request.GET.get("state").split("|")
        result = get_dropbox_auth_flow(request, {SECRET_KEY: state}).finish(
            {"code": code, "state": state}
        )

        user = User.objects.filter(id=user_id).first()

        existing_dropbox_access = DropboxAccess.objects.filter(user=user).first()
        if existing_dropbox_access is not None:
            dropbox_access = existing_dropbox_access
        else:
            dropbox_access = DropboxAccess(user=user)

        dropbox_access.use_dropbox = True
        dropbox_access.token = result.access_token
        dropbox_access.save()

        return Response({"detail": "OK"})
