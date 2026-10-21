#!/usr/bin/env python3
# coding: utf-8
"""
Module `chatette.utils`
Contains utility functions and classes used everywhere in the project.
"""

from __future__ import print_function
import sys
from random import sample, choice
from copy import deepcopy

from string import ascii_letters

from enum import Enum


class UnitType(Enum):
    alias = "alias"
    slot = "slot"
    intent = "intent"


class Singleton(object):
    """
    The base class for all singleton objects.
    Every class that subclasses this class will have the behavior
    of a singleton: their constructor will always return the same instance.
    @pre: In order to work, a sub-class needs to have an `_instance` class
          variable.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_or_create(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    @classmethod
    def reset_instance(cls, *args, **kwargs):
        """
        Completely resets the instance of the class
        (representing the singleton), makes a new one and
        returns this instance.
        """
        cls._instance = None
        cls._instance = cls(*args, **kwargs)
        return cls._instance

    @classmethod
    def was_instantiated(cls):
        return (cls._instance is not None)


def cast_to_unicode(anything):
    """This function is used to cast any string in `anything` to unicode if executed with Python 2.7. If executed with Python 3, it returns `anything` as it is. The function can handle various data types such as strings, arrays, and dictionaries.
    Input-Output Arguments
    :param anything: Any data type. The input data that needs to be cast to unicode if executed with Python 2.7.
    :return: The input data casted to unicode if executed with Python 2.7, or the input data as it is if executed with Python 3.
    """


def sample_indulgent(array, nb_items):
    """
    Same as `random.sample` but doesn't raise an error if `nb_items`
    is larger than the length of `array`: in that case,
    simply returns (a copy of) the whole array.
    """
    if nb_items <= len(array):
        return sample(array, nb_items)
    return deepcopy(array)


def rchop(string, ending):
    """Removes a substring at the end of a string."""
    if string.endswith(ending):
        return string[:-len(ending)]
    return string


def str_to_bool(text):
    """
    Transforms the strings 'True' and 'False' to their boolean counterparts.
    Raises a `ValueError` if `text` is neither of them.
    """
    text = text.lower()
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError("Cannot convert '" + str(text) + "' into a boolean")


def remove_duplicates(dict_of_lists):
    """Removes duplicates from a dictionary containing lists."""
    return {key: list(set(value)) for (key, value) in dict_of_lists.items()}

def min_if_exist(n1, n2):
    """
    Returns the minimum between two numbers, or the only defined number
    (in case the other is `None`) or `None` if none of the numbers are defined.
    """
    if n1 is None and n2 is None:
        return None
    elif n1 is None:
        return n2
    elif n2 is None:
        return n1
    return min(n1, n2)


def random_string(length=6):
    """
    Returns a random string of length `length` containing only ASCII letters.
    """
    return ''.join([choice(ascii_letters) for _ in range(length)])


def append_to_list_in_dict(dict_of_lists, key, value):
    """
    Given the dict of key->lists `dict_of_lists`, appends the value `value` to
    the list at key `key` if this list exist. Otherwise, creates a list
    containing `value` and puts it at key `key`.
    """
    if key not in dict_of_lists:
        dict_of_lists[key] = [value]
    else:
        dict_of_lists[key].append(value)

def extend_list_in_dict(dict_of_lists, key, values):
    """
    Given the dict of key->lists `dict_of_lists`, extends the list at key `key`
    with the values `values` if this list exist. Otherwise, puts the list
    `values` at key `key`.
    """
    if key not in dict_of_lists:
        dict_of_lists[key] = values
    else:
        dict_of_lists[key].extend(values)


if __name__ == "__main__":
    # pylint: disable=wrong-import-position
    import warnings

    warnings.warn(
        "You are running the wrong file ('utils.py')." +
        "The file that should be run is 'run.py'."
    )