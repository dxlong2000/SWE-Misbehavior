from itertools import chain

from faker.typing import OrderedDictType


def add_ordereddicts(*odicts: OrderedDictType) -> OrderedDictType:
    """This function takes multiple ordered dictionaries and combines them into a single ordered dictionary. It first extracts the items from each input ordered dictionary and then combines them into a single ordered dictionary.
    Input-Output Arguments
    :param odicts: OrderedDictType. Multiple ordered dictionaries to be combined.
    :return: OrderedDictType. The combined ordered dictionary.
    """