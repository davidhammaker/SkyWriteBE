from rest_framework import serializers

from users_app.models import EncryptionKey


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["key", "user_id"]
        model = EncryptionKey
