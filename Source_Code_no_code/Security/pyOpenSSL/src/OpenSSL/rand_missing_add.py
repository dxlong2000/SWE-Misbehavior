"""
PRNG management routines, thin wrappers.
"""

from OpenSSL._util import lib as _lib


def add(buffer: bytes, entropy: int) -> None:
    """This function adds bytes from a buffer into the PRNG (Pseudo-Random Number Generator) state. It is used to mix additional randomness into the PRNG state.
    Input-Output Arguments
    :param buffer: bytes. The buffer containing random data to be mixed into the PRNG state.
    :param entropy: int. The lower bound estimate of how much randomness is contained in the buffer, measured in bytes.
    :return: None.
    """


def status() -> int:
    """
    Check whether the PRNG has been seeded with enough data.

    :return: 1 if the PRNG is seeded enough, 0 otherwise.
    """
    return _lib.RAND_status()