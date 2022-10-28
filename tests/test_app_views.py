import json
from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from sky_write_app.models import StorageObject
from sky_write_app.views import MeView, StorageObjectView
from sky_write_django.settings import ORDERING_MAX
from users_app.models import CustomConfig


class TestAppViews(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Set up request factor
        cls.factory = APIRequestFactory()

        # Create some test users
        user_1 = User.objects.create_user("user 1")
        cls.user_1 = user_1
        user_2 = User.objects.create_user("user 2")
        cls.user_2 = user_2
        user_3 = User.objects.create_user("user 3")
        cls.user_3 = user_3

        # Create custom configs as needed
        CustomConfig.objects.create(user=user_1)
        CustomConfig.objects.create(user=user_2)
        CustomConfig.objects.create(user=user_3)

        # Create a few test objects
        obj_1 = StorageObject.objects.create(
            name="obj 1.1",
            user=user_1,
            is_file=False,
            ordering_parameter=10,
        )
        StorageObject.objects.create(
            name="obj 1.2",
            user=user_1,
            folder=obj_1,
            ordering_parameter=20,
        )
        StorageObject.objects.create(
            name="obj 2.1",
            user=user_2,
            ordering_parameter=30,
        )
        cls.obj_1 = obj_1

    def test_me_view(self):
        """Test getting user data from ``/me/``"""
        # Create a request for which user_1 is authenticated
        request = self.factory.get("/me/")
        force_authenticate(request, self.user_1)

        # Get the response
        response = MeView.as_view()(request)

        # Check that the basic content of the response is good
        assert response.status_code == 200
        assert response.data["username"] == self.user_1.username

        # Check that the storage objects look accurate; i.e. the folder
        # and the file it contains are in their proper places
        assert len(response.data["storage_objects"]) == 1
        folder = response.data["storage_objects"][0]
        assert folder["name"] == "obj 1.1"
        assert len(folder["files"]) == 1
        file = folder["files"][0]
        assert file["name"] == "obj 1.2"

        # Check that a file belonging to another user doesn't show up
        assert "obj 2.1" not in json.dumps(response.data)

    def test_storage_object_list_view(self):
        """Test getting storage objects from ``/storage_objects/``"""
        # Create a request for which user_1 is authenticated
        request = self.factory.get("/storage_objects/")
        force_authenticate(request, self.user_1)

        # Get the response
        response = StorageObjectView.as_view()(request)

        # Check the response content
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert {obj["name"] for obj in response.data} == {"obj 1.1", "obj 1.2"}

    def test_storage_object_create_view_existing_objects(self):
        """Test creating storage objects at ``/storage_objects/`` when
        other objects exist"""
        # Create a request for which user_1 is authenticated
        request = self.factory.post(
            "/storage_objects/",
            data={"name": "obj 1.3", "folder_id": self.obj_1.id},
        )
        force_authenticate(request, self.user_1)

        # Get the response
        response = StorageObjectView.as_view()(request)

        # Check the response content
        assert response.status_code == 201
        assert response.data["name"] == "obj 1.3"
        assert response.data["user_id"] == self.user_1.id

        # Check that the object was created
        obj = StorageObject.objects.filter(name="obj 1.3").first()
        assert obj is not None
        assert obj.user == self.user_1

        # Check that the ordering parameter is accurate; 20 is the order
        # param of "obj 2".
        expected_order_param = Decimal(ORDERING_MAX + 20) / 2
        assert obj.ordering_parameter == expected_order_param

    def test_storage_object_create_view_no_existing_objects(self):
        """Test creating storage objects at ``/storage_objects/`` when
        no other objects exist"""
        # Create a request for which user_3 is authenticated
        request = self.factory.post(
            "/storage_objects/",
            data={"name": "obj 3.1"},
        )
        force_authenticate(request, self.user_3)

        # Get the response
        response = StorageObjectView.as_view()(request)

        # Check the response content
        assert response.status_code == 201
        assert response.data["name"] == "obj 3.1"
        assert response.data["user_id"] == self.user_3.id

        # Check that the object was created
        obj = StorageObject.objects.filter(name="obj 3.1").first()
        assert obj is not None
        assert obj.user == self.user_3

        # Check that the ordering parameter is accurate
        expected_order_param = Decimal(ORDERING_MAX / 2)
        assert obj.ordering_parameter == expected_order_param

    def test_storage_object_create_view_error(self):
        """Test creating storage objects at ``/storage_objects/`` when
        bad data is sent"""
        # Create a request for which user_1 is authenticated
        request = self.factory.post(
            "/storage_objects/",
        )
        force_authenticate(request, self.user_1)

        # Get the response
        response = StorageObjectView.as_view()(request)

        # Check the response content
        assert response.status_code == 400
        assert "detail" in response.data
