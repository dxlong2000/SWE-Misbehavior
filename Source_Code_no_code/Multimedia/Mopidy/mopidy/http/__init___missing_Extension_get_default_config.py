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
        """This function retrieves the default configuration for the Extension class. It reads the configuration file "ext.conf" located in the same directory as the script and returns the configuration data.
        Input-Output Arguments
        :param self: Extension. An instance of the Extension class.
        :return: dict. The default configuration data read from the "ext.conf" file.
        """

    def get_config_schema(self):
        schema = super().get_config_schema()
        schema["hostname"] = config_lib.Hostname()
        schema["port"] = config_lib.Port()
        schema["static_dir"] = config_lib.Deprecated()
        schema["zeroconf"] = config_lib.String(optional=True)
        schema["allowed_origins"] = config_lib.List(
            optional=True,
            unique=True,
            subtype=config_lib.String(transformer=lambda x: x.lower()),
        )
        schema["csrf_protection"] = config_lib.Boolean(optional=True)
        schema["default_app"] = config_lib.String(optional=True)
        return schema

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