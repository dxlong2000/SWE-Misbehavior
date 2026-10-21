
def crack_secret_exponent_from_k(generator, signed_value, sig, k):
    """
    Given a signature of a signed_value and a known k, return the secret exponent.
    """
    r, s = sig
    return ((s * k - signed_value) * generator.inverse(r)) % generator.order()


def crack_k_from_sigs(generator, sig1, val1, sig2, val2):
    """This function calculates the value of k from the given signatures and values in RSA domain.
    Input-Output Arguments
    :param generator: The generator value.
    :param sig1: The first signature.
    :param val1: The first value.
    :param sig2: The second signature.
    :param val2: The second value.
    :return: The value of k.
    """