"""jc - JSON Convert `/etc/os-release` file parser

This parser is an alias to the Key/Value parser (`--kv`).

Usage (cli):

    $ cat /etc/os-release | jc --os-release

Usage (module):

    import jc
    result = jc.parse('os_release', os_release_output)

Schema:

    {
        "<key>":     string
    }

Examples:

    $ cat /etc/os-release | jc --os-release -p
    {
      "NAME": "CentOS Linux",
      "VERSION": "7 (Core)",
      "ID": "centos",
      "ID_LIKE": "rhel fedora",
      "VERSION_ID": "7",
      "PRETTY_NAME": "CentOS Linux 7 (Core)",
      "ANSI_COLOR": "0;31",
      "CPE_NAME": "cpe:/o:centos:centos:7",
      "HOME_URL": "https://www.centos.org/",
      "BUG_REPORT_URL": "https://bugs.centos.org/",
      "CENTOS_MANTISBT_PROJECT": "CentOS-7",
      "CENTOS_MANTISBT_PROJECT_VERSION": "7",
      "REDHAT_SUPPORT_PRODUCT": "centos",
      "REDHAT_SUPPORT_PRODUCT_VERSION": "7"
    }

    $ cat /etc/os-release | jc --os-release -p -r
    {
      "NAME": "\\"CentOS Linux\\"",
      "VERSION": "\\"7 (Core)\\"",
      "ID": "\\"centos\\"",
      "ID_LIKE": "\\"rhel fedora\\"",
      "VERSION_ID": "\\"7\\"",
      "PRETTY_NAME": "\\"CentOS Linux 7 (Core)\\"",
      "ANSI_COLOR": "\\"0;31\\"",
      "CPE_NAME": "\\"cpe:/o:centos:centos:7\\"",
      "HOME_URL": "\\"https://www.centos.org/\\"",
      "BUG_REPORT_URL": "\\"https://bugs.centos.org/\\"",
      "CENTOS_MANTISBT_PROJECT": "\\"CentOS-7\\"",
      "CENTOS_MANTISBT_PROJECT_VERSION": "\\"7\\"",
      "REDHAT_SUPPORT_PRODUCT": "\\"centos\\"",
      "REDHAT_SUPPORT_PRODUCT_VERSION": "\\"7\\""
    }
"""
from jc.jc_types import JSONDictType
import jc.parsers.kv
import jc.utils


class info():
    """Provides parser metadata (version, author, etc.)"""
    version = '1.0'
    description = '`/etc/os-release` file parser'
    author = 'Kelly Brazil'
    author_email = 'kellyjonbrazil@gmail.com'
    details = 'Using the Key/Value parser'
    compatible = ['linux', 'darwin', 'cygwin', 'win32', 'aix', 'freebsd']
    tags = ['file', 'standard', 'string']


__version__ = info.version


def _process(proc_data: JSONDictType) -> JSONDictType:
    """
    Final processing to conform to the schema.

    Parameters:

        proc_data:   (Dictionary) raw structured data to process

    Returns:

        Dictionary. Structured to conform to the schema.
    """
    return jc.parsers.kv._process(proc_data)


def parse(
    data: str,
    raw: bool = False,
    quiet: bool = False
) -> JSONDictType:
    """This function is the main text parsing function. It takes in a string of text data and parses it into structured data. It can return either the raw unprocessed output or the processed output.
    Input-Output Arguments
    :param data: str. The text data to be parsed.
    :param raw: bool. Whether to return unprocessed output. Defaults to False.
    :param quiet: bool. Whether to suppress warning messages. Defaults to False.
    :return: JSONDictType. The parsed structured data, either raw or processed.
    """