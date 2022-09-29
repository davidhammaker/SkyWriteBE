from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sky_write_app.models import StorageObject
from sky_write_app.serializers import MeSerializer, StorageObjectSerializer
from sky_write_app.utils import save_file, load_file


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
            serializer.save(user_id=request.user.id)
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
            print(response, response.__dict__)
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            # TODO: Change to ``update_file`` ?
            #  Logic may be different; use PK to patch.
            save_file(request, self.kwargs["pk"])
        return response
