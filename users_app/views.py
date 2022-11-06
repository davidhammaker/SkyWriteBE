from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sky_write_app.utils import get_dropbox_auth_flow
from sky_write_django.settings import DBX_APP_KEY, DEV, SECRET_KEY, UI_URI
from users_app.models import CustomConfig, DefaultStorage
from users_app.serializers import ConfigForUISerializer, KeySerializer, UserSerializer


class UserCreationView(generics.CreateAPIView):
    """A class for creating a new user."""

    serializer_class = UserSerializer

    def perform_create(self, serializer):
        """
        Hash password and create user.
        """
        new_user = serializer.save()
        new_user.set_password(new_user.password)
        new_user.save()


class KeyCreationView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = KeySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user_id=request.user.id,
                encryption_key=request.data.get("encryption_key"),
            )
            return Response(serializer.data, 201)
        return Response({"detail": serializer.errors}, 400)


class ConfigRetrieveView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ConfigForUISerializer

    def get_queryset(self):
        return CustomConfig.objects.filter(user=self.request.user).all()

    def get_object(self):
        return CustomConfig.objects.filter(user=self.request.user).first()

    @staticmethod
    def get(request, *args, **kwargs):
        config = CustomConfig.objects.filter(user=request.user).first()
        if config is None:
            Response(
                {"detail": "Configuration doesn't exist; try logging in again."},
                400,
            )
        return Response(
            {
                "dropbox_auth_url": (
                    # We pass the ``url_state`` kwarg to ``start()`` to
                    # persist the user ID through the auth flow. The
                    # Dropbox API attaches this to the ``state``,
                    # preceded by a ``|`` pipe.
                    get_dropbox_auth_flow(request).start(url_state=str(request.user.id))
                    if DBX_APP_KEY is not None else None
                ),
                **ConfigForUISerializer(config).data,
            }
        )


class StorageOptionsView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def get(_request):
        storage_options = {}
        for item in list(DefaultStorage):
            if DEV or item.value != "LS":
                storage_options[str(item.label)] = item.value
        return Response(storage_options)


class DropboxResolutionView(views.APIView):
    @staticmethod
    def get(request):
        code = request.GET.get("code")

        if code is not None:
            # In case the user cancels...

            # The ``state`` query param holds the user ID; the two are
            # separated by a ``|`` pipe.
            state, user_id = request.GET.get("state").split("|")
            result = get_dropbox_auth_flow(request, {SECRET_KEY: state}).finish(
                {"code": code, "state": state}
            )

            user = User.objects.filter(id=user_id).first()
            config = user.custom_config

            # Automatically set the default storage if there isn't one.
            if not config.default_storage:
                config.default_storage = "DX"

            config.dropbox_token = result.refresh_token
            config.save()

        response = HttpResponseRedirect(UI_URI)
        response.status_code = 303

        return response
