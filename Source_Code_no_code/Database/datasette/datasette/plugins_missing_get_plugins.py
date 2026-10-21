import importlib
import pluggy
import pkg_resources
import sys
from . import hookspecs

DEFAULT_PLUGINS = (
    "datasette.publish.heroku",
    "datasette.publish.cloudrun",
    "datasette.facets",
    "datasette.filters",
    "datasette.sql_functions",
    "datasette.actor_auth_cookie",
    "datasette.default_permissions",
    "datasette.default_magic_parameters",
    "datasette.blob_renderer",
    "datasette.default_menu_links",
    "datasette.handle_exception",
    "datasette.forbidden",
)

pm = pluggy.PluginManager("datasette")
pm.add_hookspecs(hookspecs)

if not hasattr(sys, "_called_from_test"):
    # Only load plugins if not running tests
    pm.load_setuptools_entrypoints("datasette")

# Load default plugins
for plugin in DEFAULT_PLUGINS:
    mod = importlib.import_module(plugin)
    pm.register(mod, plugin)


def get_plugins():
    """This function retrieves information about the installed plugins. It iterates over the plugins obtained and collects information such as the plugin name, static path, templates path, and hooks. It also retrieves the version and project name if available. The collected information is stored in a list of dictionaries and returned.
    Input-Output Arguments
    :param: No input parameters.
    :return: List of dictionaries. Each dictionary contains information about a plugin, including the plugin name, static path, templates path, hooks, version, and project name (if available).
    """