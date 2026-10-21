import pkgutil
import sys

from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List


def get_path(module: ModuleType) -> str:
    """Get the path of the given module. It first checks if the system is frozen. If it is, it checks if it is frozen by PyInstaller or others and then returns the path accordingly. If the system is not frozen, it returns the path of the module. If the file is None, it raises RuntimeError(f"Can't find path from module `{module}.").
    Input-Output Arguments
    :param module: ModuleType. The module for which the path is to be found.
    :return: str. The path of the given module.
    """


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
    available_providers = set()
    for providers_mod in modules:
        if providers_mod.__package__:
            providers = [
                ".".join([providers_mod.__package__, mod]) for mod in list_module(providers_mod) if mod != "__pycache__"
            ]
            available_providers.update(providers)
    return sorted(available_providers)