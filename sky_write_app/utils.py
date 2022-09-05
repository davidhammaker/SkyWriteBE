from urllib.parse import quote

from django.urls import reverse
from dropbox import DropboxOAuth2Flow
from rest_framework.request import Request

from sky_write_django.settings import (
    DBX_APP_KEY,
    DBX_APP_SECRET,
    DBX_RESOLUTION_PATH_NAME,
    SECRET_KEY,
)


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
    )
    return auth_flow
