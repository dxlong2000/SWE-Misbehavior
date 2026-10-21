import types
from urllib.parse import urlparse

from pyramid.exceptions import ConfigurationError

from kinto.core import utils

try:
    import statsd as statsd_module
except ImportError:  # pragma: no cover
    statsd_module = None


class Client:
    def __init__(self, host, port, prefix):
        self._client = statsd_module.StatsClient(host, port, prefix=prefix)

    def watch_execution_time(self, obj, prefix="", classname=None):
        classname = classname or utils.classname(obj)
        members = dir(obj)
        for name in members:
            value = getattr(obj, name)
            is_method = isinstance(value, types.MethodType)
            if not name.startswith("_") and is_method:
                statsd_key = f"{prefix}.{classname}.{name}"
                decorated_method = self.timer(statsd_key)(value)
                setattr(obj, name, decorated_method)

    def timer(self, key):
        return self._client.timer(key)

    def count(self, key, count=1, unique=None):
        if unique is None:
            return self._client.incr(key, count=count)
        else:
            return self._client.set(key, unique)


def statsd_count(request, count_key):
    statsd = request.registry.statsd
    if statsd:
        statsd.count(count_key)


def load_from_config(config):
    # If this is called, it means that a ``statsd_url`` was specified in settings.
    # (see ``kinto.core.initialization``)
    # Raise a proper error if the ``statsd`` module is not installed.
    """Load the configuration settings and create a StatsD client based on the specified settings. It checks if the statsd module is installed and raises an error if it is not. Then, it retrieves the statsd URL from the settings and parses it. Finally, it creates a StatsD client with the hostname, port, and prefix specified in the settings.
    Input-Output Arguments
    :param config: The configuration object.
    :return: Client. The created StatsD client.
    """