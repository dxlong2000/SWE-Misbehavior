# Copyright (c) 2014, Menno Smits
# Released subject to the New BSD License
# Please see http://en.wikipedia.org/wiki/BSD_licenses

import re
from datetime import datetime
from email.utils import parsedate_tz

from .fixed_offset import FixedOffset

_SHORT_MONTHS = " Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(" ")


def parse_to_datetime(timestamp: bytes, normalise: bool = True) -> datetime:
    """Convert an IMAP datetime string to a datetime.

    If normalise is True (the default), then the returned datetime
    will be timezone-naive but adjusted to the local time.

    If normalise is False, then the returned datetime will be
    unadjusted but will contain timezone information as per the input.
    """
    time_tuple = parsedate_tz(_munge(timestamp))
    if time_tuple is None:
        raise ValueError("couldn't parse datetime %r" % timestamp)

    tz_offset_seconds = time_tuple[-1]
    tz = None
    if tz_offset_seconds is not None:
        tz = FixedOffset(tz_offset_seconds / 60)

    dt = datetime(*time_tuple[:6], tzinfo=tz)
    if normalise and tz:
        dt = datetime_to_native(dt)

    return dt


def datetime_to_native(dt: datetime) -> datetime:
    return dt.astimezone(FixedOffset.for_system()).replace(tzinfo=None)


def datetime_to_INTERNALDATE(dt: datetime) -> str:
    """This function converts a datetime instance like "-%Y %H:%M:%S %z" to a string representation in the format required by IMAP INTERNALDATE. If the datetime instance does not have timezone information, the current system timezone is used.
    Input-Output Arguments
    :param dt: datetime. The datetime instance to be converted.
    :return: str. The string representation of the datetime instance in the IMAP INTERNALDATE format.
    """


# Matches timestamp strings where the time separator is a dot (see
# issue #154). For example: 'Sat, 8 May 2010 16.03.09 +0200'
_rfc822_dotted_time = re.compile(r"\w+, ?\d{1,2} \w+ \d\d(\d\d)? \d\d?\.\d\d?\.\d\d?.*")


def _munge(timestamp: bytes) -> str:
    s = timestamp.decode("latin-1")  # parsedate_tz only works with strings
    if _rfc822_dotted_time.match(s):
        return s.replace(".", ":")
    return s


def format_criteria_date(dt: datetime) -> bytes:
    """Format a date or datetime instance for use in IMAP search criteria."""
    out = "%02d-%s-%d" % (dt.day, _SHORT_MONTHS[dt.month], dt.year)
    return out.encode("ascii")