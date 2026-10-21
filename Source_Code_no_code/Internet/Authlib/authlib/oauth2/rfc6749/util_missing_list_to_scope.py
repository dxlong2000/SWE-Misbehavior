import base64
import binascii
from authlib.common.encoding import to_unicode


def list_to_scope(scope):
    """This function converts a list of scopes into a space-separated string. It checks if the input scope is of type set, tuple, or list, and then joins the elements of the scope with a space separator. If the scope is None, it returns None. Otherwise, it converts the scope to Unicode and returns it.
    Input-Output Arguments
    :param scope: The input scope to be converted.
    :return: str. The converted space-separated string representation of the scope.
    """


def scope_to_list(scope):
    """Convert a space separated string to a list of scopes."""
    if isinstance(scope, (tuple, list, set)):
        return [to_unicode(s) for s in scope]
    elif scope is None:
        return None
    return scope.strip().split()


def extract_basic_authorization(headers):
    auth = headers.get('Authorization')
    if not auth or ' ' not in auth:
        return None, None

    auth_type, auth_token = auth.split(None, 1)
    if auth_type.lower() != 'basic':
        return None, None

    try:
        query = to_unicode(base64.b64decode(auth_token))
    except (binascii.Error, TypeError):
        return None, None
    if ':' in query:
        username, password = query.split(':', 1)
        return username, password
    return query, None