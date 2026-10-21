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
        if size is not None and not isinstance(size, int):
            raise TypeError("size parameter must be an int or long.")

        if size is not None:
            if size == 0:
                return b""
            if size < 0:
                size = None

        self.buf.seek(0, os.SEEK_END)

        if size is None and self.buf.tell():
            ret = self.buf.getvalue()
            self.buf = io.BytesIO()
            return ret
        if size is None:
            d = self.chunk()
            return d

        while self.buf.tell() < size:
            chunk = self.chunk()
            if not chunk:
                ret = self.buf.getvalue()
                self.buf = io.BytesIO()
                return ret
            self.buf.write(chunk)
        data = self.buf.getvalue()
        self.buf = io.BytesIO()
        self.buf.write(data[size:])
        return data[:size]

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
        """This function returns the next chunk of data from the iterator. If the iterator is empty, it returns an empty byte string. If the iterator is exhausted, it sets the iterator to None and returns an empty byte string.
        Input-Output Arguments
        :param self: IterUnreader. An instance of the IterUnreader class.
        :return: bytes. The next chunk of data from the iterator.
        """