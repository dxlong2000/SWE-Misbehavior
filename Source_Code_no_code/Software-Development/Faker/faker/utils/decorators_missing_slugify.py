from functools import wraps
from typing import Callable, Dict, Tuple, TypeVar

from ..utils import text

T = TypeVar("T")


def slugify(fn: Callable) -> Callable:
    """This function is a decorator that takes a function and returns a new function. The new function calls the original function and then slugifies the result.
    Input-Output Arguments
    :param fn: Callable. The original function to be decorated.
    :return: Callable. The decorated function.
    """


def slugify_domain(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args: Tuple[T, ...], **kwargs: Dict[str, T]) -> str:
        return text.slugify(fn(*args, **kwargs), allow_dots=True)

    return wrapper


def slugify_unicode(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args: Tuple[T, ...], **kwargs: Dict[str, T]) -> str:
        return text.slugify(fn(*args, **kwargs), allow_unicode=True)

    return wrapper


def lowercase(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args: Tuple[T, ...], **kwargs: Dict[str, T]) -> str:
        return fn(*args, **kwargs).lower()

    return wrapper