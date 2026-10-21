# Copyright (c) 2022, Menno Smits
# Released subject to the New BSD License
# Please see http://en.wikipedia.org/wiki/BSD_licenses

from typing import Tuple

version_info = (3, 0, 0, "final")


def _imapclient_version_string(vinfo: Tuple[int, int, int, str]) -> str:
    """It creates a version string based on the given version information. It first extracts the major, minor, micro, and release level from the version information and then creates a version string based on the extracted information.
    Input-Output Arguments
    :param vinfo: Tuple. A tuple containing version information in the format (major, minor, micro, releaselevel).
    :return: String. The version string created based on the version information.
    """


version = _imapclient_version_string(version_info)

maintainer = "IMAPClient Maintainers"
maintainer_email = "imapclient@groups.io"

author = "Menno Finlay-Smits"
author_email = "inbox@menno.io"