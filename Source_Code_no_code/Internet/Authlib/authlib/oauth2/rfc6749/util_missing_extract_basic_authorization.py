import base64
import binascii
from authlib.common.encoding import to_unicode


def list_to_scope(scope):
    """Convert a list of scopes to a space separated string."""
    if isinstance(scope, (set, tuple, list)):
        return " ".join([to_unicode(s) for s in scope])
    if scope is None:
        return scope
    return to_unicode(scope)


def scope_to_list(scope):
    """Convert a space separated string to a list of scopes."""
    if isinstance(scope, (tuple, list, set)):
        return [to_unicode(s) for s in scope]
    elif scope is None:
        return None
    return scope.strip().split()


def extract_basic_authorization(headers):
    """This function extracts the username and password from the Authorization header in the given headers dictionary. It first checks if the Authorization header exists and contains a space. If not, it returns None for both username and password. If the Authorization header exists and is of type 'basic', it decodes the auth_token and splits it into username and password. If the auth_token does not contain a colon, it returns the auth_token as the username and None for the password.
    Input-Output Arguments
    :param headers: Dictionary. The headers dictionary containing the Authorization header.
    :return: Tuple. The extracted username and password from the Authorization header.
    """