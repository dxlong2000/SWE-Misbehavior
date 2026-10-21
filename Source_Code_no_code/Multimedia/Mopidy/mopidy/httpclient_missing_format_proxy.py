import platform



"Helpers for configuring HTTP clients used in Mopidy extensions."


def format_proxy(proxy_config, auth=True):
    """This function converts a Mopidy proxy config to the commonly used proxy string format. It outputs "scheme://host:port", "scheme://user:pass@host:port" or None depending on the proxy config provided. You can also opt out of getting the basic auth by setting "auth" to False.
    Input-Output Arguments
    :param proxy_config: Dictionary. The Mopidy proxy config.
    :param auth: Bool. Whether to include basic authentication in the proxy string. Defaults to True.
    :return: String. The commonly used proxy string format.
    """


def format_user_agent(name=None):
    """Construct a User-Agent suitable for use in client code.

    This will identify use by the provided ``name`` (which should be on the
    format ``dist_name/version``), Mopidy version and Python version.

    .. versionadded:: 1.1
    """
    import mopidy
    parts = [
        f"Mopidy/{mopidy.__version__}",
        f"{platform.python_implementation()}/{platform.python_version()}",
    ]
    if name:
        parts.insert(0, name)
    return " ".join(parts)