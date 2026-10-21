import itertools
from typing import Iterable


def pairwise(iterable: Iterable):
    """Iterate over elements two by two.

    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def iter_slice(iterable: bytes, n: int):
    """This function yields slices of the given size from the input iterable and indicates if each slice is the last one.
    Input-Output Arguments
    :param iterable: bytes. The input iterable to be sliced.
    :param n: int. The size of each slice.
    :return: Yields a tuple containing the slice and a boolean indicating if it is the last slice.
    """