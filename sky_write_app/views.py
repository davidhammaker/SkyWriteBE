from decimal import Decimal

from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sky_write_app.models import StorageObject
from sky_write_app.serializers import MeSerializer, StorageObjectSerializer
from sky_write_app.utils import load_file, save_file
from sky_write_django.settings import ORDERING_MAX


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
            last_object = (
                StorageObject.objects.filter(
                    folder_id=request.data.get("folder_id"),
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


class StorageObjectReOrderView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def patch(request):
        if ({"from_id", "to_id"} - set(request.data)) != set():
            return Response(
                {"detail": "Request body must contain 'to_id' and 'from_id'."},
                400,
            )
        from_id = request.data["from_id"]
        from_obj = StorageObject.objects.filter(
            user=request.user,
            id=request.data["from_id"],
        ).first()
        if from_obj is None:
            return Response(
                {"detail": f"The requested object does not exist. ({from_id})"},
                400,
            )

        to_id = request.data["to_id"]
        if to_id is None:
            current_max_order_param = (
                StorageObject.objects.filter(user=request.user)
                .order_by("-ordering_parameter")
                .first()
                .ordering_parameter
            )
            new_order_param = (current_max_order_param + ORDERING_MAX) / 2
        else:
            to_obj = StorageObject.objects.filter(
                user=request.user,
                id=request.data["to_id"],
            ).first()
            if to_obj is None:
                return Response(
                    {"detail": f"The requested object does not exist. ({to_id})"},
                    400,
                )
            next_highest_obj = (
                StorageObject.objects.filter(
                    user=request.user,
                    ordering_parameter__lt=to_obj.ordering_parameter,
                )
                .order_by("-ordering_parameter")
                .first()
            )
            if next_highest_obj is None:
                next_highest_param = 0
            else:
                next_highest_param = next_highest_obj.ordering_parameter
            print(to_obj.ordering_parameter, next_highest_param)
            new_order_param = (to_obj.ordering_parameter + next_highest_param) / 2
        print(new_order_param)
        from_obj.ordering_parameter = new_order_param
        if "folder_id" in request.data:
            from_obj.folder_id = request.data["folder_id"]
        from_obj.save()
        return Response(StorageObjectSerializer(from_obj).data)
