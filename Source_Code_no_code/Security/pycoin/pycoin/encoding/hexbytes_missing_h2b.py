import binascii


def h2b(h):
    """This function converts a hexadecimal string to a binary string using the binascii.unhexlify method. It accepts a unicode string and raises a ValueError on failure.
    Input-Output Arguments
    :param h: String. The hexadecimal string to be converted to binary.
    :return: Binary string. The converted binary string.
    """


def h2b_rev(h):
    return h2b(h)[::-1]


def b2h(the_bytes):
    return binascii.hexlify(the_bytes).decode("utf8")


def b2h_rev(the_bytes):
    return b2h(bytearray(reversed(the_bytes)))


class bytes_as_revhex(bytes):
    def __str__(self):
        return b2h_rev(self)

    def __repr__(self):
        return b2h_rev(self)


class bytes_as_hex(bytes):
    def __str__(self):
        return b2h(self)

    def __repr__(self):
        return b2h(self)