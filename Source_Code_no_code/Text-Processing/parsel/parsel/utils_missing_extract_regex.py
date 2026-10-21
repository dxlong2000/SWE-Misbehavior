import re
from typing import Any, Iterable, Iterator, List, Match, Pattern, Union, cast
from w3lib.html import replace_entities as w3lib_replace_entities


def flatten(x: Iterable[Any]) -> List[Any]:
    """flatten(sequence) -> list
    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).
    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, (8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]
    >>> flatten(["foo", "bar"])
    ['foo', 'bar']
    >>> flatten(["foo", ["baz", 42], "bar"])
    ['foo', 'baz', 42, 'bar']
    """
    return list(iflatten(x))


def iflatten(x: Iterable[Any]) -> Iterator[Any]:
    """iflatten(sequence) -> Iterator
    Similar to ``.flatten()``, but returns iterator instead"""
    for el in x:
        if _is_listlike(el):
            yield from flatten(el)
        else:
            yield el


def _is_listlike(x: Any) -> bool:
    """
    >>> _is_listlike("foo")
    False
    >>> _is_listlike(5)
    False
    >>> _is_listlike(b"foo")
    False
    >>> _is_listlike([b"foo"])
    True
    >>> _is_listlike((b"foo",))
    True
    >>> _is_listlike({})
    True
    >>> _is_listlike(set())
    True
    >>> _is_listlike((x for x in range(3)))
    True
    >>> _is_listlike(range(5))
    True
    """
    return hasattr(x, "__iter__") and not isinstance(x, (str, bytes))


def extract_regex(
    regex: Union[str, Pattern[str]], text: str, replace_entities: bool = True
) -> List[str]:
    """This function extracts a list of strings from the given text using a regular expression. It follows certain policies to determine which strings to extract:
    - If the regular expression contains a named group called "extract", the value of that group will be returned.
    - If the regular expression contains multiple numbered groups, all those groups will be returned as a flattened list.
    - If the regular expression doesn't contain any groups, the entire matching string will be returned.
    Input-Output Arguments
    :param regex: Union[str, Pattern[str]]. The regular expression pattern to match against the text. It can be either a string or a compiled regular expression pattern.
    :param text: str. The text to search for matches.
    :param replace_entities: bool. Optional. Whether to replace HTML entities in the extracted strings. Defaults to True.
    :return: List[str]. A list of extracted strings from the text.
    """


def shorten(text: str, width: int, suffix: str = "...") -> str:
    """Truncate the given text to fit in the given width."""
    if len(text) <= width:
        return text
    if width > len(suffix):
        return text[: width - len(suffix)] + suffix
    if width >= 0:
        return suffix[len(suffix) - width :]
    raise ValueError("width must be equal or greater than 0")