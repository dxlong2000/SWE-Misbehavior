import json
import base64
import struct


def to_bytes(x, charset='utf-8', errors='strict'):
    """Convert the input to bytes based on the given charset and error handling. It first checks if the input is None, bytes, string, int, or float and then converts it to bytes accordingly.
    Input-Output Arguments
    :param x: Any. The input to be converted to bytes.
    :param charset: String. The character set to be used for encoding. Defaults to 'utf-8'.
    :param errors: String. The error handling scheme to be used. Defaults to 'strict'.
    :return: Bytes. The converted bytes. Or None if the input is None.
    """


def to_unicode(x, charset='utf-8', errors='strict'):
    if x is None or isinstance(x, str):
        return x
    if isinstance(x, bytes):
        return x.decode(charset, errors)
    return str(x)


def to_native(x, encoding='ascii'):
    if isinstance(x, str):
        return x
    return x.decode(encoding)


def json_loads(s):
    return json.loads(s)


def json_dumps(data, ensure_ascii=False):
    return json.dumps(data, ensure_ascii=ensure_ascii, separators=(',', ':'))


def urlsafe_b64decode(s):
    s += b'=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)


def urlsafe_b64encode(s):
    return base64.urlsafe_b64encode(s).rstrip(b'=')


def base64_to_int(s):
    data = urlsafe_b64decode(to_bytes(s, charset='ascii'))
    buf = struct.unpack('%sB' % len(data), data)
    return int(''.join(["%02x" % byte for byte in buf]), 16)


def int_to_base64(num):
    if num < 0:
        raise ValueError('Must be a positive integer')

    s = num.to_bytes((num.bit_length() + 7) // 8, 'big', signed=False)
    return to_unicode(urlsafe_b64encode(s))


def json_b64encode(text):
    if isinstance(text, dict):
        text = json_dumps(text)
    return urlsafe_b64encode(to_bytes(text))