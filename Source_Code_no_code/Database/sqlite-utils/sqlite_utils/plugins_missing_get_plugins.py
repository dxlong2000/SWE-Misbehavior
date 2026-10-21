import pluggy
import sys
from . import hookspecs

pm = pluggy.PluginManager("sqlite_utils")
pm.add_hookspecs(hookspecs)

if not getattr(sys, "_called_from_test", False):
    # Only load plugins if not running tests
    pm.load_setuptools_entrypoints("sqlite_utils")


def get_plugins():
    """TThis function retrieves information about the installed plugins. It retrieves the plugins, iterates over them and creates a dictionary for each plugin containing its name and the names of the hooks it implements. It also checks if there is corresponding distribution information for the plugin and includes the version and project name in the dictionary if available. Finally, it appends each plugin dictionary to a list and returns the list.
    Input-Output Arguments
    :param: No input parameters.
    :return: List of dictionaries. Each dictionary contains information about a plugin, including its name, hooks, version (if available), and project name (if available).
    """