import binascii
from authlib.common.encoding import urlsafe_b64decode, json_loads, to_unicode
from authlib.jose.errors import DecodeError


def extract_header(header_segment, error_cls):
    """This function extracts the header from a given header segment. It first extracts the header segment. Then, it decodes the extracted header data using UTF-8 encoding and loads it as a JSON object. If the loaded header is not a dictionary, it raises an error. Finally, it returns the extracted header.
    Input-Output Arguments
    :param header_segment: The header segment to extract the header from.
    :param error_cls: The error class to raise if there is an error during the extraction process.
    :return: The extracted header as a dictionary.
    """


def extract_segment(segment, error_cls, name='payload'):
    try:
        return urlsafe_b64decode(segment)
    except (TypeError, binascii.Error):
        msg = 'Invalid {} padding'.format(name)
        raise error_cls(msg)


def ensure_dict(s, structure_name):
    if not isinstance(s, dict):
        try:
            s = json_loads(to_unicode(s))
        except (ValueError, TypeError):
            raise DecodeError('Invalid {}'.format(structure_name))

    if not isinstance(s, dict):
        raise DecodeError('Invalid {}'.format(structure_name))

    return s