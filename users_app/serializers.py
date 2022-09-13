from rest_framework import serializers

from users_app.models import CustomConfig


class KeySerializer(serializers.ModelSerializer):
    """Partial CustomConfig serializer. User's CustomConfig object is
    created on first login."""

    class Meta:
        fields = ["encryption_key", "user_id"]
        model = CustomConfig


class ConfigForUISerializer(serializers.ModelSerializer):
    """CustomConfig serialization that's safe for UI usage. No access
    tokens provided to UI."""

    dropbox_connected = serializers.SerializerMethodField()

    class Meta:
        fields = ["default_storage", "dropbox_connected"]
        model = CustomConfig

    @staticmethod
    def get_dropbox_connected(obj):
        if obj.dropbox_token is not None:
            return True
        return False
