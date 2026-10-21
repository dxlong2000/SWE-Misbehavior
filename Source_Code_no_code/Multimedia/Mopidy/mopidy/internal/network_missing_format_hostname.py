import logging
import re
import socket

logger = logging.getLogger(__name__)


def try_ipv6_socket() -> bool:
    """Determine if system really supports IPv6"""
    if not socket.has_ipv6:
        return False
    try:
        socket.socket(socket.AF_INET6).close()
        return True
    except OSError as exc:
        logger.debug(
            f"Platform supports IPv6, but socket creation failed, "
            f"disabling: {exc}"
        )
    return False


#: Boolean value that indicates if creating an IPv6 socket will succeed.
has_ipv6 = try_ipv6_socket()


def format_hostname(hostname: str) -> str:
    """This function formats a hostname for display. If the hostname is an IPv6 address in the form of "x:x:x:x:x:x:x:x", it is converted to the IPv4-mapped IPv6 address format "::ffff:x.x.x.x".
    Input-Output Arguments
    :param hostname: String. The hostname to be formatted.
    :return: String. The formatted hostname.
    """