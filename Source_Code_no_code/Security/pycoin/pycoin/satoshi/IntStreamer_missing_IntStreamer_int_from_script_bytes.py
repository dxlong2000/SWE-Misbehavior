




class IntStreamer(object):

    @classmethod
    def int_from_script_bytes(class_, s, require_minimal=False):
        """This function converts a byte array into an integer value. It first checks if the byte array is empty, and if so, returns 0. Then it reverses the byte array and extracts the first byte. It extracts the value from the first byte by performing a bitwise AND operation with 0x7f. If the "require_minimal" parameter is set to True, it checks if the value is 0 and if the byte array is non-minimally encoded. If so, it raises a ScriptError. It then checks if the first byte has the sign bit set, indicating a negative value. It iterates over the remaining bytes in the byte array, left-shifting the value by 8 bits and adding the current byte. If the value is negative, it negates it. Finally, it returns the resulting integer value.
        Input-Output Arguments
        :param class_: The class object. It is not used in the function.
        :param s: The byte array to convert into an integer.
        :param require_minimal: Bool. Whether to check for minimal encoding. Defaults to False.
        :return: The converted integer value.
        """

    @classmethod
    def int_to_script_bytes(class_, v):
        if v == 0:
            return b''
        is_negative = (v < 0)
        if is_negative:
            v = -v
        ba = bytearray()
        while v >= 256:
            ba.append(v & 0xff)
            v >>= 8
        ba.append(v & 0xff)
        if ba[-1] >= 128:
            ba.append(0x80 if is_negative else 0)
        elif is_negative:
            ba[-1] |= 0x80
        return bytes(ba)