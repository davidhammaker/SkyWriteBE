from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sky_write_app.models import StorageObject
from sky_write_app.serializers import MeSerializer, StorageObjectSerializer
from sky_write_app.utils import format_path, get_storage_name


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
