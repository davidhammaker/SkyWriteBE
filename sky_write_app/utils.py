import os
import typing as t
from urllib.parse import quote

import requests
from django.urls import reverse
from dropbox import Dropbox, DropboxOAuth2Flow
from dropbox.files import WriteMode
from rest_framework.request import Request

from sky_write_app.models import StorageObject
from sky_write_django.settings import (
    DBX_APP_KEY,
    DBX_APP_SECRET,
    DBX_RESOLUTION_PATH_NAME,
    SECRET_KEY,
)
from users_app.models import CustomConfig


def get_storage_name(filename):
    """Convert slashes to double-slashes, so that all single-slashes in
    a string can represent the division between names in a file path."""
    ret = ""
    for c in filename:
        if c == "/":
            ret += "//"
        else:
            ret += c
    return ret


def get_original_name(filename):
    """Revert a single- to double-slash conversion."""
    ret = ""
    skip_next = False
    for index, c in enumerate(filename):
        next_c = ""
        if index + 1 < len(filename):
            next_c = filename[index + 1]
        if skip_next:
            skip_next = False
            continue
        if c == "/" and next_c == "/" and not skip_next:
            skip_next = True
        ret += c
    return ret


def format_path(storage_object):
    """Return an encoded path for a storage object."""
    focus_object = storage_object
    path = quote(focus_object.name, safe="")
    while focus_object.folder is not None:
        focus_object = focus_object.folder
        path = f"{quote(focus_object.name, safe='')}/{path}"
    return path


def get_calculated_path_ids(obj: StorageObject):
    """Get a list of IDs for folders containing a given object."""
    calculated_path_reversed = []
    parent_folder = obj.folder
    while parent_folder is not None:
        calculated_path_reversed.append(parent_folder.id)
        parent_folder = parent_folder.folder
    return reversed(calculated_path_reversed)


def get_dropbox_auth_flow(request: Request, session: dict = None):
    """
    Get the Auth flow object for accessing a user's Dropbox account.

    The object uses ``.start()`` and ``.finish()`` to proceed through
    the auth flow.

    To start the flow, only pass the current ``request`` object, then
    ``.start()`` returns the URL for enabling Dropbox.

    To complete the flow, pass ``request`` AND the session. The session
    is formatted as follows: ``{SECRET_KEY: STATE}``, where
    ``SECRET_KEY`` is the Django project's secret key, and ``STATE`` is
    derived from the ``state`` query parameter.

    - Note that the resolution view will be passed two query parameters:
        ``code`` and ``state``.

    Use ``.finish()`` to fully complete the flow. Pass ``code`` and
    ``state`` in a dict: ``{"code": CODE, "state": STATE}``
    """
    host = request.get_host()
    scheme = "http" if "localhost" in host else "https"
    redirect_uri = f"{scheme}://{host}{reverse(DBX_RESOLUTION_PATH_NAME)}"
    auth_flow = DropboxOAuth2Flow(
        consumer_key=DBX_APP_KEY,
        redirect_uri=redirect_uri,
        session=session or {},
        csrf_token_session_key=SECRET_KEY,
        consumer_secret=DBX_APP_SECRET,
        token_access_type="offline",
    )
    return auth_flow


def save_file(request: Request, storage_object_id: int):

    # Cancel this operation if the storage object is a folder.
    if request.data.get("is_file") is False:
        return

    string_content = request.data.get("content", "")
    bytes_content = bytes(string_content, "utf-8")
    config: CustomConfig = request.user.custom_config
    storage_object = StorageObject.objects.filter(id=storage_object_id).first()

    filename = f"{str(storage_object.file_uuid)}.txt"

    if config.default_storage == "DX":
        dbx = Dropbox(
            oauth2_refresh_token=config.dropbox_token,
            app_key=DBX_APP_KEY,
            app_secret=DBX_APP_SECRET,
        )
        dbx.refresh_access_token()
        dbx.files_upload(bytes_content, f"/{filename}", mode=WriteMode.overwrite)

    elif config.default_storage == "LS":
        with open(f"/code/local_storage/{filename}", "w") as file:
            file.writelines([string_content])


def load_file(request: Request, storage_object_id: int) -> t.Optional[str]:

    if request.data.get("is_file") is False:
        return

    config: CustomConfig = request.user.custom_config
    storage_object = StorageObject.objects.filter(id=storage_object_id).first()

    filename = f"{str(storage_object.file_uuid)}.txt"

    if config.default_storage == "DX":
        dbx = Dropbox(
            oauth2_refresh_token=config.dropbox_token,
            app_key=DBX_APP_KEY,
            app_secret=DBX_APP_SECRET,
        )
        dbx.refresh_access_token()

        # Get file metadata and the Dropbox response, which holds the
        # POST request we'll use to retrieve file content.
        _metadata, dbx_response = dbx.files_download(f"/{filename}")
        post_request_obj = dbx_response.request

        # Send the POST request and receive file content.
        session = requests.Session()
        file_response = session.send(post_request_obj)
        return "".join([line.decode() for line in file_response.iter_lines()])

    elif config.default_storage == "LS":
        with open(f"/code/local_storage/{filename}", "r") as file:
            return "".join(list(file.readlines()))


def delete_object(request: Request, storage_object_id: int, recursive: bool = False):

    config: CustomConfig = request.user.custom_config
    storage_object = StorageObject.objects.filter(id=storage_object_id).first()

    filename = f"{str(storage_object.file_uuid)}.txt"

    if storage_object.is_file:
        if config.default_storage == "DX":
            dbx = Dropbox(
                oauth2_refresh_token=config.dropbox_token,
                app_key=DBX_APP_KEY,
                app_secret=DBX_APP_SECRET,
            )
            dbx.refresh_access_token()

            dbx.files_delete_v2(f"/{filename}")

        elif config.default_storage == "LS":
            os.remove(f"/code/local_storage/{filename}")

    else:
        for obj in storage_object.contents.all():
            if recursive:
                delete_object(request, obj.id, recursive=True)
            else:
                obj.folder_id = storage_object.folder_id
                obj.save()

    storage_object.delete()
