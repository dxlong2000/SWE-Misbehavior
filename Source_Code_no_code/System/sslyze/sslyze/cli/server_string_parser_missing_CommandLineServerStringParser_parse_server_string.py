import socket
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass(frozen=True)
class InvalidServerStringError(Exception):
    """Exception raised when SSLyze was unable to parse a hostname:port string supplied via the command line."""

    server_string: str
    error_message: str


class CommandLineServerStringParser:
    """Utility class to parse a 'host:port{ip}' string taken from the command line into a valid (host,ip, port) tuple.
    Supports IPV6 addresses.
    """

    SERVER_STRING_ERROR_BAD_PORT = "Not a valid host:port"

    @classmethod
    def parse_server_string(cls, server_str: str) -> Tuple[str, Optional[str], Optional[int]]:
        # Extract ip from target
        """This function parses a server string and extracts the host, ip, and port information from it. It first checks if the server string contains curly braces, indicating the presence of an ip address. If so, it extracts the ip address and removes it from the server string. Then, it checks if the server string contains square brackets, indicating the presence of an ipv6 hint. If so, it calls a helper function to parse the ipv6 server string. If not, it checks if the extracted ip address contains square brackets, indicating the presence of an ipv6 hint. If so, it calls the helper function to parse the ipv6 ip address. Finally, if none of the above conditions are met, it calls the helper function to parse the ipv4 server string. The function returns the host, ip, and port extracted from the server string.
        Input-Output Arguments
        :param cls: The class object.
        :param server_str: String. The server string to be parsed.
        :return: Tuple. The host, ip, and port extracted from the server string.
        """

    @classmethod
    def _parse_ipv4_server_string(cls, server_str: str) -> Tuple[str, Optional[int]]:
        host = server_str
        port = None
        if ":" in server_str:
            host = (server_str.split(":"))[0]  # hostname or ipv4 address
            try:
                port = int((server_str.split(":"))[1])
            except ValueError:  # Port is not an int
                raise InvalidServerStringError(server_string=server_str, error_message=cls.SERVER_STRING_ERROR_BAD_PORT)

        return host, port

    @classmethod
    def _parse_ipv6_server_string(cls, server_str: str) -> Tuple[str, Optional[int]]:
        if not socket.has_ipv6:
            raise InvalidServerStringError(
                server_string=server_str, error_message="IPv6 is not supported on this platform"
            )

        port = None
        target_split = server_str.split("]")
        ipv6_addr = target_split[0].split("[")[1]
        if ":" in target_split[1]:  # port was specified
            try:
                port = int(target_split[1].rsplit(":")[1])
            except ValueError:  # Port is not an int
                raise InvalidServerStringError(server_string=server_str, error_message=cls.SERVER_STRING_ERROR_BAD_PORT)
        return ipv6_addr, port