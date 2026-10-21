import logging
import re
import socket

logger = logging.getLogger(__name__)


def try_ipv6_socket() -> bool:
    """This function checks if the system supports IPv6 by attempting to create a socket with the AF_INET6 address family. If the socket creation is successful, it returns True. Otherwise, it returns False after logging a debug message.
    Input-Output Arguments
    :param: No input parameters.
    :return: Bool. True if the system supports IPv6, False otherwise.
    """


#: Boolean value that indicates if creating an IPv6 socket will succeed.
has_ipv6 = try_ipv6_socket()


def format_hostname(hostname: str) -> str:
    """Format hostname for display."""
    if has_ipv6 and re.match(r"\d+.\d+.\d+.\d+", hostname) is not None:
        hostname = f"::ffff:{hostname}"
    return hostname