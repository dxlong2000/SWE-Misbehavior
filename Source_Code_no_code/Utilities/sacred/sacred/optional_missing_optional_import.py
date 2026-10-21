#!/usr/bin/env python
# coding=utf-8

import importlib
from sacred.utils import modules_exist
from sacred.utils import get_package_version, parse_version


def optional_import(*package_names):
    """This function tries to import the given package names and returns the first successfully imported package. If none of the packages can be imported, it returns False and None.
    Input-Output Arguments
    :param package_names: Tuple of strings. The names of the packages to be imported.
    :return: Tuple. The first element is a boolean indicating whether the import is successful. The second element is the first successfully imported package.
    ```
    """


def get_tensorflow():
    # Ensures backward and forward compatibility with TensorFlow 1 and 2.
    if get_package_version("tensorflow") < parse_version("1.13.1"):
        import warnings

        warnings.warn(
            "Use of TensorFlow 1.12 and older is deprecated. "
            "Use Tensorflow 1.13 or newer instead.",
            DeprecationWarning,
        )
        import tensorflow as tf
    else:
        import tensorflow.compat.v1 as tf
    return tf


# Get libc in a cross-platform way and use it to also flush the c stdio buffers
# credit to J.F. Sebastians SO answer from here:
# http://stackoverflow.com/a/22434262/1388435
try:
    import ctypes
    from ctypes.util import find_library
except ImportError:
    libc = None
else:
    try:
        libc = ctypes.cdll.msvcrt  # Windows
    except OSError:
        libc = ctypes.cdll.LoadLibrary(find_library("c"))


has_numpy, np = optional_import("numpy")
has_yaml, yaml = optional_import("yaml")
has_pandas, pandas = optional_import("pandas")

has_sqlalchemy = modules_exist("sqlalchemy")
has_mako = modules_exist("mako")
has_tinydb = modules_exist("tinydb", "tinydb_serialization", "hashfs")
has_tensorflow = modules_exist("tensorflow")