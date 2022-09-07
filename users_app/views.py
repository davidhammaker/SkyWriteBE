from django.contrib.auth.models import User
from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sky_write_app.utils import get_dropbox_auth_flow
from sky_write_django.settings import SECRET_KEY
from users_app.models import DropboxAccess
from users_app.serializers import KeySerializer


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
