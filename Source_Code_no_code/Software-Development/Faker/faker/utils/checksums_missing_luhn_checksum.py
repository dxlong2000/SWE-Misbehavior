from typing import List


def luhn_checksum(number: float) -> int:
    """Calculate the Luhn checksum for the given number. The Luhn algorithm is used to validate a variety of identification numbers, such as credit card numbers, IMEI numbers, National Provider Identifier numbers in the United States, and Canadian Social Insurance Numbers.
    Input-Output Arguments
    :param number: float. The number for which the Luhn checksum needs to be calculated.
    :return: int. The Luhn checksum for the given number.
    """


def calculate_luhn(partial_number: float) -> int:
    """
    Generates the Checksum using Luhn's algorithm
    """
    check_digit = luhn_checksum(int(partial_number) * 10)
    return check_digit if check_digit == 0 else 10 - check_digit