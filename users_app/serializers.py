from rest_framework import serializers

from users_app.models import DropboxAccess, EncryptionKey


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["key", "user_id"]
        model = EncryptionKey


class DropboxAccessSerializer(serializers.ModelSerializer):
    connected = serializers.SerializerMethodField()

    class Meta:
        fields = ["use_dropbox", "connected"]
        model = DropboxAccess

    @staticmethod
    def get_connected(obj):
        if obj.token is not None:
            return True
        return False
