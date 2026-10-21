# -*- coding: utf-8 -*-
import datetime
import math
import re

DTM_TZ_RE = re.compile(r"(\d+(?:\.\d+)?)(?:([+-]\d{2})(\d{2}))?")


class _UTCOffset(datetime.tzinfo):
    """Fixed offset timezone from UTC."""

    def __init__(self, minutes):
        """``minutes`` is a offset from UTC, negative for west of UTC"""
        self.minutes = minutes

    def utcoffset(self, dt):
        return datetime.timedelta(minutes=self.minutes)

    def tzname(self, dt):
        minutes = abs(self.minutes)
        return "{0}{1:02}{2:02}".format(
            "-" if self.minutes < 0 else "+", minutes // 60, minutes % 60
        )

    def dst(self, dt):
        return datetime.timedelta(0)


def parse_datetime(value):
    """This function parses a string in the HL7 DTM format and returns a datetime object. The HL7 DTM format is of the form "YYYY[MM[DD[HH[MM[SS[.S[S[S[S]]]]]]]]][+/-HHMM]". If the input string is empty, it returns None.
    Input-Output Arguments
    :param value: String. The HL7 DTM string to be parsed.
    :return: datetime.datetime. The parsed datetime object.
    """