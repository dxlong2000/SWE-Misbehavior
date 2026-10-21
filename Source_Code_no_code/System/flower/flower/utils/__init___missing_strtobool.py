import base64
import os.path
import uuid




def gen_cookie_secret():
    return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)


def bugreport(app=None):
    from .. import __version__
    try:
        import celery
        import humanize
        import tornado

        app = app or celery.Celery()

		# pylint: disable=consider-using-f-string
        return 'flower   -> flower:%s tornado:%s humanize:%s%s' % (
            __version__,
            tornado.version,
            getattr(humanize, '__version__', None) or getattr(humanize, 'VERSION'),
            app.bugreport()
        )
    except (ImportError, AttributeError) as e:
        return f"Error when generating bug report: {e}. Have you installed correct versions of Flower's dependencies?"


def abs_path(path):
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        cwd = os.environ.get('PWD') or os.getcwd()
        path = os.path.join(cwd, path)
    return path


def prepend_url(url, prefix):
    return '/' + prefix.strip('/') + url


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0). It checks the input string and returns 1 if the input string is a true value and 0 if the input string is a false value. It raises a ValueError if the input string is neither a true value nor a false value.
    Input-Output Arguments
    :param val: str. The string representation of truth. True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values are 'n', 'no', 'f', 'false', 'off', and '0'. Raises ValueError if 'val' is anything else.
    :return: int. 1 if the input string is a true value, 0 if the input string is a false value.
    """