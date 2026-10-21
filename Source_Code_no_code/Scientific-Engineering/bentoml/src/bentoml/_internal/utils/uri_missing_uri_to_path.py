import os
import pathlib
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlparse
from urllib.request import url2pathname

import psutil


def path_to_uri(path: str) -> str:
    """
    Convert a path to a URI.

    Args:
        path: Path to convert to URI.

    Returns:
        URI string. (quoted, absolute)
    """
    path = os.path.abspath(path)
    if psutil.WINDOWS:
        return pathlib.PureWindowsPath(path).as_uri()
    if psutil.POSIX:
        return pathlib.PurePosixPath(path).as_uri()
    raise ValueError("Unsupported OS")


def uri_to_path(uri: str) -> str:
    """Convert a file URI to a path. It first parses the input URI and then checks if the scheme is supported. Then, it constructs the path string and returns it.
    Input-Output Arguments
    :param uri: String. The URI to convert to a path.
    :return: String. The path string (unquoted).
    """


def encode_path_for_uri(path: str) -> str:
    """Percent-encode non-URL characters in a path."""
    return quote(path.replace(os.sep, "/"))