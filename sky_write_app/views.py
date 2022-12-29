from decimal import Decimal

from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sky_write_app.models import StorageObject
from sky_write_app.serializers import (
    FileSerializer,
    MeSerializer,
    StorageObjectSerializer,
)
from sky_write_app.utils import load_file, save_file
from sky_write_django.settings import ORDERING_MAX


class MeView(views.APIView):
    """An APIView class that returns all of a user's relevant data,
    including username, encryption key, and storage objects."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def get(request):
        return Response(MeSerializer(request.user).data)


class StorageObjectView(generics.ListCreateAPIView):
    """A simple APIView class for Storage Objects. Currently, this is
    only used for creating new objects."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = StorageObjectSerializer

    def get_queryset(self):
        return StorageObject.objects.filter(user=self.request.user).all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            last_object = (
                StorageObject.objects.filter(
                    folder_id=request.data.get("folder_id"),
                    user=request.user,
                )
                .order_by("-ordering_parameter")
                .first()
            )
            if last_object:
                ordering_parameter = (
                    Decimal(ORDERING_MAX / 2) + last_object.ordering_parameter / 2
                )
            else:
                ordering_parameter = Decimal(ORDERING_MAX / 2)
            serializer.save(
                user_id=request.user.id,
                ordering_parameter=ordering_parameter,
            )
            save_file(request, serializer.data["id"])
            return Response(serializer.data, 201)
        return Response({"detail": serializer.errors}, 400)


class StorageObjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = StorageObjectSerializer

    def get_queryset(self):
        return StorageObject.objects.filter(user=self.request.user).all()

    def get(self, request, *args, **kwargs):
        response = super().get(self, request, *args, **kwargs)
        if response.status_code == 200:
            response.data["content"] = load_file(request, self.kwargs["pk"])
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            save_file(request, self.kwargs["pk"])
        return response


class RootContentsView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def get(request):
        files = (
            StorageObject.objects.filter(
                user=request.user,
                folder_id=None,
            )
            .order_by("ordering_parameter")
            .all()
        )
        return Response({"files": [FileSerializer(file).data for file in files]})


class FolderContentsView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def get(request, pk):
        folder = StorageObject.objects.filter(
            id=pk,
            user=request.user,
            is_file=False,
        ).first()
        if folder is None:
            return Response({"detail": "Folder Not Found"}, 404)
        files = (
            StorageObject.objects.filter(
                folder_id=pk,
                user=request.user,
            )
            .order_by("ordering_parameter")
            .all()
        )
        return Response({"files": [FileSerializer(file).data for file in files]})


class StorageObjectReOrderView(views.APIView):
    """An APIView class for re-ordering Storage Objects."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def post(request):
        objects = []
        for obj_id in request.data:
            obj = StorageObject.objects.filter(id=obj_id, user=request.user).first()
            if obj is None:
                return Response(
                    {"detail": f"An invalid object ID was sent ({obj_id})"}, 400
                )
            objects.append(obj)

        ordering_constant = ORDERING_MAX / (len(objects) + 2)
        for index, obj in enumerate(objects):
            obj.ordering_parameter = ordering_constant * (index + 1)
            obj.save()

        return Response("OK")


class StorageObjectReOrganizeView(views.APIView):
    """An APIView class for re-ordering Storage Objects."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def post(request):
        if {"files", "folder_id"} - set(request.data) != set():
            return Response(
                {"detail": "Request body must contain 'files' and 'folder_id'."},
                400,
            )

        objects = []
        for obj_id in request.data["files"]:
            obj = StorageObject.objects.filter(id=obj_id, user=request.user).first()
            if obj is None:
                return Response(
                    {"detail": f"An invalid object ID was sent ({obj_id})"}, 400
                )
            objects.append(obj)

        folder_id = request.data["folder_id"]
        folder = StorageObject.objects.filter(id=folder_id, user=request.user).first()
        if folder_id is not None and (folder is None or folder.is_file):
            return Response(
                {"detail": f"An invalid folder ID was sent ({folder_id})"}, 400
            )

        existing_object = (
            StorageObject.objects.filter(folder_id=folder_id, user=request.user)
            .order_by("-ordering_parameter")
            .first()
        )
        if existing_object is not None:
            ordering_base = existing_object.ordering_parameter
        else:
            ordering_base = 0
        ordering_constant = (ORDERING_MAX - ordering_base) / (len(objects) + 2)
        for index, obj in enumerate(objects):
            obj.ordering_parameter = ordering_base + ordering_constant * (index + 1)
            obj.folder_id = folder_id
            obj.save()

        return Response("OK")
