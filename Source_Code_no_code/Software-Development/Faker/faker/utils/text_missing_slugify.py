import re
import unicodedata

from typing import Pattern

_re_pattern: Pattern = re.compile(r"[^\w\s-]", flags=re.U)
_re_pattern_allow_dots: Pattern = re.compile(r"[^\.\w\s-]", flags=re.U)
_re_spaces: Pattern = re.compile(r"[-\s]+", flags=re.U)


def slugify(value: str, allow_dots: bool = False, allow_unicode: bool = False) -> str:
    """This function takes a string value and converts it into a slug format. It removes non-word characters, converts spaces to hyphens, and converts the string to lowercase. It can also optionally allow dots in the slug.
    Input-Output Arguments
    :param value: str. The string value to be converted into a slug format.
    :param allow_dots: bool. Whether to allow dots in the slug. Defaults to False.
    :param allow_unicode: bool. Whether to allow unicode characters in the slug. Defaults to False.
    :return: str. The converted slug string.
    """