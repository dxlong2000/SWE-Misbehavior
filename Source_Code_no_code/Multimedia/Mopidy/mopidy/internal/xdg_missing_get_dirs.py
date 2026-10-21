import configparser
import os
import pathlib


def get_dirs():
    """This function returns a dictionary containing all the known XDG Base Directories for the current user. It retrieves the values of the environment variables related to XDG Base Directories and expands the paths using `pathlib.Path.expanduser()`. It also updates the dictionary with additional directories if the `user-dirs.dirs` file exists and is parseable.
    Input-Output Arguments
    :param: No input parameters.
    :return: dict. A dictionary containing the XDG Base Directories for the current user. The keys are the names of the directories (e.g., "XDG_CACHE_DIR", "XDG_CONFIG_DIR") and the values are `pathlib.Path` objects representing the expanded paths.
    """


def _get_user_dirs(xdg_config_dir):
    """Returns a dict of XDG dirs read from
    ``$XDG_CONFIG_HOME/user-dirs.dirs``.

    This is used at import time for most users of :mod:`mopidy`. By rolling our
    own implementation instead of using :meth:`glib.get_user_special_dir` we
    make it possible for many extensions to run their test suites, which are
    importing parts of :mod:`mopidy`, in a virtualenv with global site-packages
    disabled, and thus no :mod:`glib` available.
    """

    dirs_file = xdg_config_dir / "user-dirs.dirs"

    if not dirs_file.exists():
        return {}

    data = dirs_file.read_bytes()
    data = b"[XDG_USER_DIRS]\n" + data
    data = data.replace(b"$HOME", bytes(pathlib.Path.home()))
    data = data.replace(b'"', b"")

    config = configparser.RawConfigParser()
    config.read_string(data.decode())

    result = {}
    for k, v in config.items("XDG_USER_DIRS"):
        if v is None:
            continue
        if isinstance(k, bytes):
            k = k.decode()
        result[k.upper()] = pathlib.Path(v).resolve()

    return result