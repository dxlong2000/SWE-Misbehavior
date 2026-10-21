import re

from benedict.core import traverse
from benedict.utils import type_util

KEY_INDEX_RE = r"(?:\[[\'\"]*(\-?[\d]+)[\'\"]*\]){1}$"


def check_keys(d, separator):
    """
    Check if dict keys contain keypath separator.
    """
    if not type_util.is_dict(d) or not separator:
        return

    def check_key(parent, key, value):
        if key and type_util.is_string(key) and separator in key:
            raise ValueError(
                f"Key should not contain keypath separator {separator!r}, found: {key!r}."
            )

    traverse(d, check_key)


def parse_keys(keypath, separator):
    """
    Parse keys from keylist or keypath using the given separator.
    """
    if type_util.is_list_or_tuple(keypath):
        keys = []
        for key in keypath:
            keys += parse_keys(key, separator)
        return keys
    return _split_keys_and_indexes(keypath, separator)


def _split_key_indexes(key):
    """This function splits key indexes in a string and returns a list of the split indexes. It checks if the key contains square brackets and ends with a closing bracket. If it does, it extracts the indexes and adds them to the list. If not, it simply returns the key as a list with a single element.
    Input-Output Arguments
    :param key: String. The key containing indexes to be split.
    :return: List. A list of split indexes.
    """


def _split_keys(keypath, separator):
    """
    Splits keys using the given separator:
    eg. 'item.subitem[1]' -> ['item', 'subitem[1]'].
    """
    if separator:
        return keypath.split(separator)
    return [keypath]


def _split_keys_and_indexes(keypath, separator):
    """
    Splits keys and indexes using the given separator:
    eg. 'item[0].subitem[1]' -> ['item', 0, 'subitem', 1].
    """
    if type_util.is_string(keypath):
        keys1 = _split_keys(keypath, separator)
        keys2 = []
        for key in keys1:
            keys2 += _split_key_indexes(key)
        return keys2
    return [keypath]