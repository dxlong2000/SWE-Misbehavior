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
    """This function returns the absolute path of the given input path. It first expands the user path and then checks if the path is absolute. If not, it appends the current working directory to the path.
    Input-Output Arguments
    :param path: str. The input path.
    :return: str. The absolute path of the input path.
    """


def prepend_url(url, prefix):
    return '/' + prefix.strip('/') + url


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    if val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    raise ValueError(f"invalid truth value {val!r}")