import importlib
import typing


class ImportFromStringError(Exception):
    pass


def import_from_string(import_str: str) -> typing.Any:
    """This function imports a module and retrieves an attribute from it based on the given import string. The import string should be in the format "<module>:<attribute>". It raises an exception if the module or attribute is not found.
    Input-Output Arguments
    :param import_str: String. The import string in the format "<module>:<attribute>".
    :return: Any. The retrieved attribute from the imported module.
    """