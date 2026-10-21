




class IntStreamer(object):

    @classmethod
    def int_from_script_bytes(class_, s, require_minimal=False):
        from pycoin.coins.SolutionChecker import ScriptError
        from . import errno
        if len(s) == 0:
            return 0
        s = bytearray(s)
        s.reverse()
        i = s[0]
        v = i & 0x7f
        if require_minimal:
            if v == 0:
                if len(s) <= 1 or ((s[1] & 0x80) == 0):
                    raise ScriptError("non-minimally encoded", errno.UNKNOWN_ERROR)
        is_negative = ((i & 0x80) > 0)
        for b in s[1:]:
            v <<= 8
            v += b
        if is_negative:
            v = -v
        return v

    @classmethod
    def int_to_script_bytes(class_, v):
        """Convert an integer to a script byte. It first checks if the integer is 0 and returns an empty byte if true. Then, it checks if the integer is negative and converts it to a positive value. It then converts the integer to a bytearray and cast it to bytes.
        Input-Output Arguments
        :param class_: A class.
        :param v: int. The integer to be converted to a script byte.
        :return: bytes. The bytes corresponding to the input integer.
        """