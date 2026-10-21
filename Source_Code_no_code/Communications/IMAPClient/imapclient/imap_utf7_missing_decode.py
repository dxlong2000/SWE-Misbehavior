# This file contains two main methods used to encode and decode UTF-7
# string, described in the RFC 3501. There are some variations specific
# to IMAP4rev1, so the built-in Python UTF-7 codec can't be used instead.
#
# The main difference is the shift character (used to switch from ASCII to
# base64 encoding context), which is & in this modified UTF-7 convention,
# since + is considered as mainly used in mailbox names.
# Other variations and examples can be found in the RFC 3501, section 5.1.3.

import binascii
from typing import List, Union


def encode(s: Union[str, bytes]) -> bytes:
    """Encode a folder name using IMAP modified UTF-7 encoding.

    Input is unicode; output is bytes (Python 3) or str (Python 2). If
    non-unicode input is provided, the input is returned unchanged.
    """
    if not isinstance(s, str):
        return s

    res = bytearray()

    b64_buffer: List[str] = []

    def consume_b64_buffer(buf: List[str]) -> None:
        """
        Consume the buffer by encoding it into a modified base 64 representation
        and surround it with shift characters & and -
        """
        if buf:
            res.extend(b"&" + base64_utf7_encode(buf) + b"-")
            del buf[:]

    for c in s:
        # printable ascii case should not be modified
        o = ord(c)
        if 0x20 <= o <= 0x7E:
            consume_b64_buffer(b64_buffer)
            # Special case: & is used as shift character so we need to escape it in ASCII
            if o == 0x26:  # & = 0x26
                res.extend(b"&-")
            else:
                res.append(o)

        # Bufferize characters that will be encoded in base64 and append them later
        # in the result, when iterating over ASCII character or the end of string
        else:
            b64_buffer.append(c)

    # Consume the remaining buffer if the string finish with non-ASCII characters
    consume_b64_buffer(b64_buffer)

    return bytes(res)


AMPERSAND_ORD = ord("&")
DASH_ORD = ord("-")


def decode(s: Union[bytes, str]) -> str:
    """This function decodes a folder name from IMAP modified UTF-7 encoding to Unicode. It takes a string or bytes as input and always returns a Unicode string. If the input is not of type bytes or str, it is returned unchanged.
    Input-Output Arguments
    :param s: Union[bytes, str]. The input string or bytes to be decoded.
    :return: str. The decoded folder name in Unicode.
    """


def base64_utf7_encode(buffer: List[str]) -> bytes:
    s = "".join(buffer).encode("utf-16be")
    return binascii.b2a_base64(s).rstrip(b"\n=").replace(b"/", b",")


def base64_utf7_decode(s: bytearray) -> str:
    s_utf7 = b"+" + s.replace(b",", b"/") + b"-"
    return s_utf7.decode("utf-7")