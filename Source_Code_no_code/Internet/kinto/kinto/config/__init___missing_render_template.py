import codecs
import logging
import os
from time import strftime

from kinto import __version__
from kinto.core import utils as core_utils

logger = logging.getLogger(__name__)

HERE = os.path.dirname(__file__)


def render_template(template, destination, **kwargs):
    """This function renders a template file by replacing placeholders with values from the provided keyword arguments and saves the rendered template to a destination file.
    Input-Output Arguments
    :param template: String. The path to the template file.
    :param destination: String. The path to the destination file where the rendered template will be saved.
    :param **kwargs: Keyword arguments. The values to replace the placeholders in the template.
    :return: No return values.
    """


postgresql_url = "postgresql://postgres:postgres@localhost/postgres"
redis_url = "redis://localhost:6379"

backend_to_values = {
    "postgresql": {
        "storage_backend": "kinto.core.storage.postgresql",
        "storage_url": postgresql_url,
        "permission_backend": "kinto.core.permission.postgresql",
        "permission_url": postgresql_url,
    },
    "redis": {
        "storage_backend": "kinto_redis.storage",
        "storage_url": redis_url + "/1",
        "permission_backend": "kinto_redis.permission",
        "permission_url": redis_url + "/3",
    },
    "memory": {
        "storage_backend": "kinto.core.storage.memory",
        "storage_url": "",
        "permission_backend": "kinto.core.permission.memory",
        "permission_url": "",
    },
}

cache_backend_to_values = {
    "postgresql": {"cache_backend": "kinto.core.cache.postgresql", "cache_url": postgresql_url},
    "redis": {"cache_backend": "kinto_redis.cache", "cache_url": redis_url + "/2"},
    "memcached": {
        "cache_backend": "kinto.core.cache.memcached",
        "cache_url": "127.0.0.1:11211 127.0.0.2:11211",
    },
    "memory": {"cache_backend": "kinto.core.cache.memory", "cache_url": ""},
}


def init(config_file, backend, cache_backend, host="127.0.0.1"):
    values = {}

    values["host"] = host
    values["secret"] = core_utils.random_bytes_hex(32)
    values["bucket_id_salt"] = core_utils.random_bytes_hex(32)

    values["kinto_version"] = __version__
    values["config_file_timestamp"] = str(strftime("%a, %d %b %Y %H:%M:%S %z"))

    values.update(backend_to_values[backend])
    values.update(cache_backend_to_values[cache_backend])

    render_template("kinto.tpl", config_file, **values)