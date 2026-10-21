import pkgutil
import sys

from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List


def get_path(module: ModuleType) -> str:
    if getattr(sys, "frozen", False):
        # frozen

        if getattr(sys, "_MEIPASS", False):
            # PyInstaller
            lib_dir = Path(getattr(sys, "_MEIPASS"))
        else:
            # others
            lib_dir = Path(sys.executable).parent / "lib"

        path = lib_dir.joinpath(*module.__package__.split("."))  # type: ignore
    else:
        # unfrozen
        if module.__file__ is not None:
            path = Path(module.__file__).parent
        else:
            raise RuntimeError(f"Can't find path from module `{module}.")
    return str(path)


def list_module(module: ModuleType) -> List[str]:
    path = get_path(module)

    if getattr(sys, "_MEIPASS", False):
        # PyInstaller
        return [file.parent.name for file in Path(path).glob("*/__init__.py")]
    else:
        return [name for _, name, is_pkg in pkgutil.iter_modules([str(path)]) if is_pkg]


def find_available_locales(providers: List[str]) -> List[str]:
    available_locales = set()

    for provider_path in providers:
        provider_module = import_module(provider_path)
        if getattr(provider_module, "localized", False):
            langs = list_module(provider_module)
            available_locales.update(langs)
    return sorted(available_locales)


def find_available_providers(modules: List[ModuleType]) -> List[str]:
    """This function takes a list of modules as input and finds the available providers. It iterates over each module in the input list, checks if the module has a package, and then creates a list of providers by joining the package name with each module name (excluding "__pycache__"). The function then updates a set of available providers with the newly created list and returns the sorted list of available providers.
    Input-Output Arguments
    :param modules: List of ModuleType. A list of modules to search for available providers.
    :return: List of str. The sorted list of available providers.
    """