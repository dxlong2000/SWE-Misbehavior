"""
Handling of media types, as found in HTTP Content-Type and Accept headers.

See https://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.7
"""
from rest_framework.compat import parse_header_parameters


def media_type_matches(lhs, rhs):
    """
    Returns ``True`` if the media type in the first argument <= the
    media type in the second argument.  The media types are strings
    as described by the HTTP spec.

    Valid media type strings include:

    'application/json; indent=4'
    'application/json'
    'text/*'
    '*/*'
    """
    lhs = _MediaType(lhs)
    rhs = _MediaType(rhs)
    return lhs.match(rhs)


def order_by_precedence(media_type_lst):
    """
    Returns a list of sets of media type strings, ordered by precedence.
    Precedence is determined by how specific a media type is:

    3. 'type/subtype; param=val'
    2. 'type/subtype'
    1. 'type/*'
    0. '*/*'
    """
    ret = [set(), set(), set(), set()]
    for media_type in media_type_lst:
        precedence = _MediaType(media_type).precedence
        ret[3 - precedence].add(media_type)
    return [media_types for media_types in ret if media_types]


class _MediaType:
    def __init__(self, media_type_str):
        self.orig = '' if (media_type_str is None) else media_type_str
        self.full_type, self.params = parse_header_parameters(self.orig)
        self.main_type, sep, self.sub_type = self.full_type.partition('/')

    def match(self, other):
        """This function checks if a given MediaType object satisfies another MediaType object. It compares the parameters, subtypes, and main types of the two objects and returns True if they match.
        Input-Output Arguments
        :param self: _MediaType. An instance of the _MediaType class.
        :param other: _MediaType. The MediaType object to compare with.
        :return: bool. True if the self MediaType satisfies the other MediaType, False otherwise.
        """

    @property
    def precedence(self):
        """
        Return a precedence level from 0-3 for the media type given how specific it is.
        """
        if self.main_type == '*':
            return 0
        elif self.sub_type == '*':
            return 1
        elif not self.params or list(self.params) == ['q']:
            return 2
        return 3

    def __str__(self):
        ret = "%s/%s" % (self.main_type, self.sub_type)
        for key, val in self.params.items():
            ret += "; %s=%s" % (key, val)
        return ret