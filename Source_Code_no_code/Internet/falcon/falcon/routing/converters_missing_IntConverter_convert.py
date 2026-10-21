# Copyright 2017 by Rackspace Hosting, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc
from datetime import datetime
import uuid

__all__ = (
    'BaseConverter',
    'IntConverter',
    'DateTimeConverter',
    'UUIDConverter',
)


# PERF(kgriffs): Avoid an extra namespace lookup when using this function
strptime = datetime.strptime


class BaseConverter(metaclass=abc.ABCMeta):
    """Abstract base class for URI template field converters."""

    @abc.abstractmethod  # pragma: no cover
    def convert(self, value):
        """Convert a URI template field value to another format or type.

        Args:
            value (str): Original string to convert.

        Returns:
            object: Converted field value, or ``None`` if the field
                can not be converted.
        """


class IntConverter(BaseConverter):
    """Converts a field value to an int.

    Identifier: `int`

    Keyword Args:
        num_digits (int): Require the value to have the given
            number of digits.
        min (int): Reject the value if it is less than this number.
        max (int): Reject the value if it is greater than this number.
    """

    __slots__ = ('_num_digits', '_min', '_max')

    def __init__(self, num_digits=None, min=None, max=None):
        if num_digits is not None and num_digits < 1:
            raise ValueError('num_digits must be at least 1')

        self._num_digits = num_digits
        self._min = min
        self._max = max

    def convert(self, value):
        """This function converts a given value to an integer based on certain conditions. It checks if the number of digits in the value matches the specified number of digits. It also checks if the value contains any whitespace characters before or after the number. If any of these conditions are not met, it returns None. It then tries to convert the value to an integer. If the conversion fails, it returns None. Finally, it checks if the converted value is within the specified minimum and maximum range. If it is not, it returns None. If all conditions are met, it returns the converted integer value.
        Input-Output Arguments
        :param self: IntConverter. An instance of the IntConverter class.
        :param value: The value to be converted to an integer.
        :return: int. The converted integer value.
        """


class DateTimeConverter(BaseConverter):
    """Converts a field value to a datetime.

    Identifier: `dt`

    Keyword Args:
        format_string (str): String used to parse the field value
            into a datetime. Any format recognized by strptime() is
            supported (default ``'%Y-%m-%dT%H:%M:%SZ'``).
    """

    __slots__ = ('_format_string',)

    def __init__(self, format_string='%Y-%m-%dT%H:%M:%SZ'):
        self._format_string = format_string

    def convert(self, value):
        try:
            return strptime(value, self._format_string)
        except ValueError:
            return None


class UUIDConverter(BaseConverter):
    """Converts a field value to a uuid.UUID.

    Identifier: `uuid`

    In order to be converted, the field value must consist of a
    string of 32 hexadecimal digits, as defined in RFC 4122, Section 3.
    Note, however, that hyphens and the URN prefix are optional.
    """

    def convert(self, value):
        try:
            return uuid.UUID(value)
        except ValueError:
            return None


BUILTIN = (
    ('int', IntConverter),
    ('dt', DateTimeConverter),
    ('uuid', UUIDConverter),
)