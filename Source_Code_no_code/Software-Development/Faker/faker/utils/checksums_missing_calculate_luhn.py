from typing import List


def luhn_checksum(number: float) -> int:
    def digits_of(n: float) -> List[int]:
        return [int(d) for d in str(n)]

    digits = digits_of(number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10


def calculate_luhn(partial_number: float) -> int:
    """This function calculates the checksum using Luhn's algorithm for a given partial number. It multiplies the partial number by 10, calculates the checksum, and returns the check digit. If the check digit is 0, it returns the check digit itself. Otherwise, it returns 10 minus the check digit.
    Input-Output Arguments
    :param partial_number: float. The partial number for which the checksum needs to be calculated.
    :return: int. The calculated check digit using Luhn's algorithm.
    """