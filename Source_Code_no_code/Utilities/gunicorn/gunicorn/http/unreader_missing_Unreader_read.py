# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.

import io
import os

# Classes that can undo reading data from
# a given type of data source.


class Unreader(object):
    def __init__(self):
        self.buf = io.BytesIO()

    def chunk(self):
        raise NotImplementedError()

    def read(self, size=None):
        """This function is used to read a specific size of data from a buffer. The function first checks if the size parameter is an integer or long. If it is not, it raises a TypeError "size parameter must be an int or long.". Then it checks if the size is zero, in which case it returns an empty byte string. If the size is negative, it sets the size to None.
        Next, the function seeks to the end of the buffer. If the size is None and there is data in the buffer, it reads the data from the buffer, resets the buffer, and returns the data. If the size is None and there is no data in the buffer, it get chunk data and returns it.
        If the size is not None, the function enters a loop that continues until the amount of data in the buffer is more than the specified size. In each iteration, it get chunk data and writes it to the buffer if there is any data. If there is no data in the chunk, it reads the data from the buffer, resets the buffer, and returns the data. Finally, it reads the data from the buffer, writes the remaining data to a new buffer, and returns the desired amount of data.
        Input-Output Arguments
        :param self: Unreader. An instance of the Unreader class.
        :param size: Integer. The number of bytes to read from the buffer. If not provided, it reads all the remaining bytes.
        :return: Bytes. The read bytes from the buffer.
        """

    def unread(self, data):
        self.buf.seek(0, os.SEEK_END)
        self.buf.write(data)


class SocketUnreader(Unreader):
    def __init__(self, sock, max_chunk=8192):
        super().__init__()
        self.sock = sock
        self.mxchunk = max_chunk

    def chunk(self):
        return self.sock.recv(self.mxchunk)


class IterUnreader(Unreader):
    def __init__(self, iterable):
        super().__init__()
        self.iter = iter(iterable)

    def chunk(self):
        if not self.iter:
            return b""
        try:
            return next(self.iter)
        except StopIteration:
            self.iter = None
            return b""