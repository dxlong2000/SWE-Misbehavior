# Copyright (c) 2015, Menno Smits
# Released subject to the New BSD License
# Please see http://en.wikipedia.org/wiki/BSD_licenses

import logging
from typing import Iterator, Optional, Tuple, Union



logger = logging.getLogger(__name__)


def to_unicode(s: Union[bytes, str]) -> str:
    if isinstance(s, bytes):
        try:
            return s.decode("ascii")
        except UnicodeDecodeError:
            logger.warning(
                "An error occurred while decoding %s in ASCII 'strict' mode. Fallback to "
                "'ignore' errors handling, some characters might have been stripped",
                s,
            )
            return s.decode("ascii", "ignore")
    return s


def to_bytes(s: Union[bytes, str], charset: str = "ascii") -> bytes:
    if isinstance(s, str):
        return s.encode(charset)
    return s


def assert_imap_protocol(condition: bool, message: Optional[bytes] = None) -> None:
    """This function is used to assert whether a condition is true. If the condition is false, it raises the corresponding exception with a specific error message "Server replied with a response that violates the IMAP protocol".
    Input-Output Arguments
    :param condition: Bool. The condition to be checked.
    :param message: Optional bytes. An optional message to be included in the error message. Defaults to None.
    :return: No return values. Or raises a protocol error.
    """


_TupleAtomPart = Union[None, int, bytes]
_TupleAtom = Tuple[Union[_TupleAtomPart, "_TupleAtom"], ...]


def chunk(lst: _TupleAtom, size: int) -> Iterator[_TupleAtom]:
    for i in range(0, len(lst), size):
        yield lst[i : i + size]