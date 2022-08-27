from urllib.parse import quote


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
    focus_object = storage_object
    path = quote(focus_object.name, safe="")
    while focus_object.folder is not None:
        focus_object = focus_object.folder
        path = f"{quote(focus_object.name, safe='')}/{path}"
    return path
