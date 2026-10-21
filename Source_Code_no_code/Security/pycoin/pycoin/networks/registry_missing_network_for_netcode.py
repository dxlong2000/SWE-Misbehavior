import importlib
import os
import pkgutil


def search_prefixes():
    prefixes = ["pycoin.symbols"]
    try:
        prefixes = os.getenv("PYCOIN_NETWORK_PATHS", "").split() + prefixes
    except Exception:
        pass
    return prefixes


def network_for_netcode(symbol):
    """This function searches for a network module based on the given symbol. It iterates through a list of search prefixes and tries to import the module with the corresponding netcode. If the imported module has a network symbol that matches the given symbol, it sets the symbol attribute of the module and returns the network object. If no matching network is found, it raises a ValueError.
    Input-Output Arguments
    :param symbol: String. The symbol of the network to search for.
    :return: Network. The network object that matches the given symbol.
    """


def iterate_symbols():
    """
    Return an iterator yielding registered netcodes.
    """
    for prefix in search_prefixes():
        package = importlib.import_module(prefix)
        for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__, onerror=lambda x: None):
            network = network_for_netcode(modname)
            if network:
                yield network.symbol.upper()


def network_codes():
    return list(iterate_symbols())