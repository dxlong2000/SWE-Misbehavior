from functools import wraps
from typing import Callable, Dict, Tuple, TypeVar

from ..utils import text

T = TypeVar("T")


def slugify(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args: Tuple[T, ...], **kwargs: Dict[str, T]) -> str:
        return text.slugify(fn(*args, **kwargs))

    return wrapper


def slugify_domain(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args: Tuple[T, ...], **kwargs: Dict[str, T]) -> str:
        return text.slugify(fn(*args, **kwargs), allow_dots=True)

    return wrapper


def slugify_unicode(fn: Callable) -> Callable:
    """This function is a decorator that wraps the input function and returns a new function. The new function slugifies the output of the input function and returns the slugified string.
    Input-Output Arguments
    :param fn: Callable. The input function to be wrapped and modified.
    :return: Callable. The wrapper function that slugifies the output of the input function.
    """


def lowercase(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args: Tuple[T, ...], **kwargs: Dict[str, T]) -> str:
        return fn(*args, **kwargs).lower()

    return wrapper