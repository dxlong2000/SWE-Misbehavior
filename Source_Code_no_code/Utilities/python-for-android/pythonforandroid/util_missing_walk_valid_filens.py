import contextlib
from fnmatch import fnmatch
import logging
from os.path import exists, join
from os import getcwd, chdir, makedirs, walk
from pathlib import Path
from platform import uname
import shutil
from tempfile import mkdtemp

from pythonforandroid.logger import logger, Err_Fore

LOGGER = logging.getLogger("p4a.util")

build_platform = "{system}-{machine}".format(
    system=uname().system, machine=uname().machine
).lower()
"""the build platform in the format `system-machine`. We use
this string to define the right build system when compiling some recipes or
to get the right path for clang compiler"""


@contextlib.contextmanager
def current_directory(new_dir):
    cur_dir = getcwd()
    logger.info(''.join((Err_Fore.CYAN, '-> directory context ', new_dir,
                         Err_Fore.RESET)))
    chdir(new_dir)
    yield
    logger.info(''.join((Err_Fore.CYAN, '<- directory context ', cur_dir,
                         Err_Fore.RESET)))
    chdir(cur_dir)


@contextlib.contextmanager
def temp_directory():
    temp_dir = mkdtemp()
    try:
        logger.debug(''.join((Err_Fore.CYAN, ' + temp directory used ',
                              temp_dir, Err_Fore.RESET)))
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)
        logger.debug(''.join((Err_Fore.CYAN, ' - temp directory deleted ',
                              temp_dir, Err_Fore.RESET)))


def walk_valid_filens(base_dir, invalid_dir_names, invalid_file_patterns):
    """This function walks through all the files and directories in the base directory, ignoring the directories and files that match the specified patterns. It yields the full path of the valid files.
    Input-Output Arguments
    :param base_dir: String. The base directory to start walking from.
    :param invalid_dir_names: List of strings. A list of invalid directory names to be ignored.
    :param invalid_file_patterns: List of strings. A list of glob patterns to be compared against the full file path.
    :return: Yield the full path of the valid files.
    """


def load_source(module, filename):
    # Python 3.5+
    import importlib.util
    if hasattr(importlib.util, 'module_from_spec'):
        spec = importlib.util.spec_from_file_location(module, filename)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    else:
        # Python 3.3 and 3.4:
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(module, filename).load_module()


class BuildInterruptingException(Exception):
    def __init__(self, message, instructions=None):
        super().__init__(message, instructions)
        self.message = message
        self.instructions = instructions


def handle_build_exception(exception):
    """
    Handles a raised BuildInterruptingException by printing its error
    message and associated instructions, if any, then exiting.
    """
    from pythonforandroid.logger import info
    from pythonforandroid.logger import error
    error('Build failed: {}'.format(exception.message))
    if exception.instructions is not None:
        info('Instructions: {}'.format(exception.instructions))
    exit(1)


def rmdir(dn, ignore_errors=False):
    if not exists(dn):
        return
    LOGGER.debug("Remove directory and subdirectory {}".format(dn))
    shutil.rmtree(dn, ignore_errors)


def ensure_dir(dn):
    if exists(dn):
        return
    LOGGER.debug("Create directory {0}".format(dn))
    makedirs(dn)


def move(source, destination):
    LOGGER.debug("Moving {} to {}".format(source, destination))
    shutil.move(source, destination)


def touch(filename):
    Path(filename).touch()