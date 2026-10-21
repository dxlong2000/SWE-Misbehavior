import platform



"Helpers for configuring HTTP clients used in Mopidy extensions."


def format_proxy(proxy_config, auth=True):
    """Convert a Mopidy proxy config to the commonly used proxy string format.

    Outputs ``scheme://host:port``, ``scheme://user:pass@host:port`` or
    :class:`None` depending on the proxy config provided.

    You can also opt out of getting the basic auth by setting ``auth`` to
    :class:`False`.

    .. versionadded:: 1.1
    """
    if not proxy_config.get("hostname"):
        return None

    scheme = proxy_config.get("scheme") or "http"
    username = proxy_config.get("username")
    password = proxy_config.get("password")
    hostname = proxy_config["hostname"]
    port = proxy_config.get("port")
    if not port or port < 0:
        port = 80

    if username and password and auth:
        return f"{scheme}://{username}:{password}@{hostname}:{port}"
    else:
        return f"{scheme}://{hostname}:{port}"


def format_user_agent(name=None):
    """This function constructs a User-Agent string that is suitable for use in client code. It includes the provided name, Mopidy version, and Python version.
    Input-Output Arguments
    :param name: String [optional]. The name to identify the use. It should be in the format "dist_name/version".
    :return: String. The constructed User-Agent string.
    """