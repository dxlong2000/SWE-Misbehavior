import logging
import os

import mopidy
from mopidy import config as config_lib
from mopidy import exceptions, ext

logger = logging.getLogger(__name__)


class Extension(ext.Extension):
    dist_name = "Mopidy-HTTP"
    ext_name = "http"
    version = mopidy.__version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), "ext.conf")
        return config_lib.read(conf_file)

    def get_config_schema(self):
        """This function returns the configuration schema for the Extension class. It first calls the parent class's method to get the base schema, and then adds additional configuration options specific to the Extension class.
        Input-Output Arguments
        :param self: Extension. An instance of the Extension class.
        :return: dict. The configuration schema for the Extension class, including the base schema and additional options.
        """

    def validate_environment(self):
        try:
            import tornado.web  # noqa
        except ImportError as e:
            raise exceptions.ExtensionError("tornado library not found", e)

    def setup(self, registry):
        from .actor import HttpFrontend
        from .handlers import make_mopidy_app_factory

        HttpFrontend.apps = registry["http:app"]
        HttpFrontend.statics = registry["http:static"]

        registry.add("frontend", HttpFrontend)
        registry.add(
            "http:app",
            {
                "name": "mopidy",
                "factory": make_mopidy_app_factory(
                    registry["http:app"], registry["http:static"]
                ),
            },
        )