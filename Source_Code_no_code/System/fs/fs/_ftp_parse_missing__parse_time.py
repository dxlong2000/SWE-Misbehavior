from __future__ import absolute_import, print_function, unicode_literals

import re
import time
import unicodedata
from datetime import datetime

try:
    from datetime import timezone
except ImportError:
    from ._tzcompat import timezone  # type: ignore

from .enums import ResourceType
from .permissions import Permissions

EPOCH_DT = datetime.fromtimestamp(0, timezone.utc)


RE_LINUX = re.compile(
    r"""
    ^
    ([-dlpscbD])
    ([r-][w-][xsS-][r-][w-][xsS-][r-][w-][xtT-][\.\+]?)
    \s+?
    (\d+)
    \s+?
    ([A-Za-z0-9][A-Za-z0-9\-\.\_\@]*\$?)
    \s+?
    ([A-Za-z0-9][A-Za-z0-9\-\.\_\@]*\$?)
    \s+?
    (\d+)
    \s+?
    (\w{3}\s+\d{1,2}\s+[\w:]+)
    \s+
    (.*?)
    $
    """,
    re.VERBOSE,
)


RE_WINDOWSNT = re.compile(
    r"""
    ^
    (?P<modified_date>\S+)
    \s+
    (?P<modified_time>\S+(AM|PM)?)
    \s+
    (?P<size>(<DIR>|\d+))
    \s+
    (?P<name>.*)
    $
    """,
    re.VERBOSE,
)


def get_decoders():
    """Return all available FTP LIST line decoders with their matching regexes."""
    decoders = [
        (RE_LINUX, decode_linux),
        (RE_WINDOWSNT, decode_windowsnt),
    ]
    return decoders


def parse(lines):
    info = []
    for line in lines:
        if not line.strip():
            continue
        raw_info = parse_line(line)
        if raw_info is not None:
            info.append(raw_info)
    return info


def parse_line(line):
    for line_re, decode_callable in get_decoders():
        match = line_re.match(line)
        if match is not None:
            return decode_callable(line, match)
    return None


def _parse_time(t, formats):
    """This function parses a given time string using a list of specified formats. It tries each format until it successfully parses the time string or exhausts all formats. If the time string cannot be parsed using any of the formats, it returns None. If the time string is successfully parsed, it converts it to epoch time and returns the epoch time value.
    Input-Output Arguments
    :param t: String. The time string to be parsed.
    :param formats: List of strings. A list of formats to be used for parsing the time string.
    :return: Float. The epoch time value of the parsed time string. If the time string cannot be parsed, it returns None.
    """


def _decode_linux_time(mtime):
    return _parse_time(mtime, formats=["%b %d %Y", "%b %d %H:%M"])


def decode_linux(line, match):
    ty, perms, links, uid, gid, size, mtime, name = match.groups()
    is_link = ty == "l"
    is_dir = ty == "d" or is_link
    if is_link:
        name, _, _link_name = name.partition("->")
        name = name.strip()
        _link_name = _link_name.strip()
    permissions = Permissions.parse(perms)

    mtime_epoch = _decode_linux_time(mtime)

    name = unicodedata.normalize("NFC", name)

    raw_info = {
        "basic": {"name": name, "is_dir": is_dir},
        "details": {
            "size": int(size),
            "type": int(ResourceType.directory if is_dir else ResourceType.file),
        },
        "access": {"permissions": permissions.dump()},
        "ftp": {"ls": line},
    }
    access = raw_info["access"]
    details = raw_info["details"]
    if mtime_epoch is not None:
        details["modified"] = mtime_epoch

    access["user"] = uid
    access["group"] = gid

    return raw_info


def _decode_windowsnt_time(mtime):
    return _parse_time(mtime, formats=["%d-%m-%y %I:%M%p", "%d-%m-%y %H:%M"])


def decode_windowsnt(line, match):
    """Decode a Windows NT FTP LIST line.

    Examples:
        Decode a directory line::

            >>> line = "11-02-18  02:12PM       <DIR>          images"
            >>> match = RE_WINDOWSNT.match(line)
            >>> pprint(decode_windowsnt(line, match))
            {'basic': {'is_dir': True, 'name': 'images'},
             'details': {'modified': 1518358320.0, 'type': 1},
             'ftp': {'ls': '11-02-18  02:12PM       <DIR>          images'}}

        Decode a file line::

            >>> line = "11-02-18  03:33PM                 9276 logo.gif"
            >>> match = RE_WINDOWSNT.match(line)
            >>> pprint(decode_windowsnt(line, match))
            {'basic': {'is_dir': False, 'name': 'logo.gif'},
             'details': {'modified': 1518363180.0, 'size': 9276, 'type': 2},
             'ftp': {'ls': '11-02-18  03:33PM                 9276 logo.gif'}}

        Alternatively, the time might also be present in 24-hour format::

            >>> line = "11-02-18  15:33                   9276 logo.gif"
            >>> match = RE_WINDOWSNT.match(line)
            >>> decode_windowsnt(line, match)["details"]["modified"]
            1518363180.0

    """
    is_dir = match.group("size") == "<DIR>"

    raw_info = {
        "basic": {
            "name": match.group("name"),
            "is_dir": is_dir,
        },
        "details": {
            "type": int(ResourceType.directory if is_dir else ResourceType.file),
        },
        "ftp": {"ls": line},
    }

    if not is_dir:
        raw_info["details"]["size"] = int(match.group("size"))

    modified = _decode_windowsnt_time(
        match.group("modified_date") + " " + match.group("modified_time")
    )
    if modified is not None:
        raw_info["details"]["modified"] = modified

    return raw_info