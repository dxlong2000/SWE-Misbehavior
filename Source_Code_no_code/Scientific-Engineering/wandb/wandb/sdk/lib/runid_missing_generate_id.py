"""runid util."""

import secrets
import string


def generate_id(length: int = 8) -> str:
    """Generate a random base-36 string of the specified length, the string is made up of lowercase letter and digits.
    Input-Output Arguments
    :param length: Integer. The length of the generated string. Defaults to 8.
    :return: String. The generated random base-36 string of the specified length.
    """