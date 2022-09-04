from django.contrib.auth.models import User
from rest_framework import serializers

from sky_write_app.models import EncryptionKey, StorageObject
from sky_write_app.utils import format_path


class StorageObjectSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "name", "name_iv", "is_file", "folder_id", "user_id"]
        model = StorageObject


class FileSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()
    folders = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "name", "name_iv", "is_file", "files", "folders", "path"]
        model = StorageObject

    @staticmethod
    def get_files(folder):
        return []

    @staticmethod
    def get_folders(folder):
        return []

    @staticmethod
    def get_path(file):
        return format_path(file)


class FolderSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()
    folders = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "name", "name_iv", "is_file", "files", "folders", "path"]
        model = StorageObject

    @staticmethod
    def get_files(folder):
        return [
            FileSerializer(file).data
            for file in folder.contents.filter(is_file=True).all()
        ]

    @staticmethod
    def get_folders(folder):
        return [
            FolderSerializer(sub_folder).data
            for sub_folder in folder.contents.filter(is_file=False).all()
        ]

    @staticmethod
    def get_path(folder):
        return format_path(folder)


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["key", "user_id"]
        model = EncryptionKey


class MeSerializer(serializers.ModelSerializer):
    storage_objects = serializers.SerializerMethodField()
    encryption_key = serializers.SerializerMethodField()

    class Meta:
        fields = ["username", "storage_objects", "encryption_key"]
        model = User

    @staticmethod
    def get_storage_objects(user):
        ret = []
        for storage_object in user.storage_objects.filter(folder_id=None).all():
            if storage_object.is_file:
                ret.append(FileSerializer(storage_object).data)
            else:
                ret.append(FolderSerializer(storage_object).data)
        return ret

    @staticmethod
    def get_encryption_key(user):
        if hasattr(user, "encryption_key"):
            return user.encryption_key.key
        return None
