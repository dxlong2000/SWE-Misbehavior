import typing

import platform
import re
import six

if typing.TYPE_CHECKING:
    from typing import Text

_WINDOWS_PLATFORM = platform.system() == "Windows"


def url_quote(path_snippet):
    # type: (Text) -> Text
    """This function quotes a URL, excluding the Windows drive letter if present. On Windows, it separates the drive letter and quotes the Windows path separately. On Unix-like systems, it uses the `~urllib.request.pathname2url` function.
    Input-Output Arguments
    :param path_snippet: Text. A file path, either relative or absolute.
    :return: Text. The quoted URL.
    """


def _has_drive_letter(path_snippet):
    # type: (Text) -> bool
    """Check whether a path contains a drive letter.

    Arguments:
       path_snippet (str): a file path, relative or absolute.

    Example:
        >>> _has_drive_letter("D:/Data")
        True
        >>> _has_drive_letter(r"C:\\System32\\ test")
        True
        >>> _has_drive_letter("/tmp/abc:test")
        False

    """
    windows_drive_pattern = ".:[/\\\\].*$"
    return re.match(windows_drive_pattern, path_snippet) is not None