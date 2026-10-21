# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.

import errno
import os
import socket
import ssl
import stat
import sys
import time

from gunicorn import util


class BaseSocket(object):

    def __init__(self, address, conf, log, fd=None):
        self.log = log
        self.conf = conf

        self.cfg_addr = address
        if fd is None:
            sock = socket.socket(self.FAMILY, socket.SOCK_STREAM)
            bound = False
        else:
            sock = socket.fromfd(fd, self.FAMILY, socket.SOCK_STREAM)
            os.close(fd)
            bound = True

        self.sock = self.set_options(sock, bound=bound)

    def __str__(self):
        return "<socket %d>" % self.sock.fileno()

    def __getattr__(self, name):
        return getattr(self.sock, name)

    def set_options(self, sock, bound=False):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if (self.conf.reuse_port
                and hasattr(socket, 'SO_REUSEPORT')):  # pragma: no cover
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except socket.error as err:
                if err.errno not in (errno.ENOPROTOOPT, errno.EINVAL):
                    raise
        if not bound:
            self.bind(sock)
        sock.setblocking(0)

        # make sure that the socket can be inherited
        if hasattr(sock, "set_inheritable"):
            sock.set_inheritable(True)

        sock.listen(self.conf.backlog)
        return sock

    def bind(self, sock):
        sock.bind(self.cfg_addr)

    def close(self):
        if self.sock is None:
            return

        try:
            self.sock.close()
        except socket.error as e:
            self.log.info("Error while closing socket %s", str(e))

        self.sock = None


class TCPSocket(BaseSocket):

    FAMILY = socket.AF_INET

    def __str__(self):
        if self.conf.is_ssl:
            scheme = "https"
        else:
            scheme = "http"

        addr = self.sock.getsockname()
        return "%s://%s:%d" % (scheme, addr[0], addr[1])

    def set_options(self, sock, bound=False):
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return super().set_options(sock, bound=bound)


class TCP6Socket(TCPSocket):

    FAMILY = socket.AF_INET6

    def __str__(self):
        (host, port, _, _) = self.sock.getsockname()
        return "http://[%s]:%d" % (host, port)


class UnixSocket(BaseSocket):

    FAMILY = socket.AF_UNIX

    def __init__(self, addr, conf, log, fd=None):
        if fd is None:
            try:
                st = os.stat(addr)
            except OSError as e:
                if e.args[0] != errno.ENOENT:
                    raise
            else:
                if stat.S_ISSOCK(st.st_mode):
                    os.remove(addr)
                else:
                    raise ValueError("%r is not a socket" % addr)
        super().__init__(addr, conf, log, fd=fd)

    def __str__(self):
        return "unix:%s" % self.cfg_addr

    def bind(self, sock):
        old_umask = os.umask(self.conf.umask)
        sock.bind(self.cfg_addr)
        util.chown(self.cfg_addr, self.conf.uid, self.conf.gid)
        os.umask(old_umask)


def _sock_type(addr):
    if isinstance(addr, tuple):
        if util.is_ipv6(addr[0]):
            sock_type = TCP6Socket
        else:
            sock_type = TCPSocket
    elif isinstance(addr, (str, bytes)):
        sock_type = UnixSocket
    else:
        raise TypeError("Unable to create socket from: %r" % addr)
    return sock_type


def create_sockets(conf, log, fds=None):
    """This function creates new sockets based on the configured addresses or file descriptors. It checks the type of address and creates either a TCP socket or a Unix socket accordingly. It also performs some error checking on the SSL configuration.
    Input-Output Arguments
    :param conf: The configuration object.
    :param log: The logging object.
    :param fds: List of file descriptors. Optional. Default is None.
    :return: List of socket objects. The created sockets.
    """


def close_sockets(listeners, unlink=True):
    for sock in listeners:
        sock_name = sock.getsockname()
        sock.close()
        if unlink and _sock_type(sock_name) is UnixSocket:
            os.unlink(sock_name)


def ssl_context(conf):
    def default_ssl_context_factory():
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile=conf.ca_certs)
        context.load_cert_chain(certfile=conf.certfile, keyfile=conf.keyfile)
        context.verify_mode = conf.cert_reqs
        if conf.ciphers:
            context.set_ciphers(conf.ciphers)
        return context

    return conf.ssl_context(conf, default_ssl_context_factory)


def ssl_wrap_socket(sock, conf):
    return ssl_context(conf).wrap_socket(sock,
                                         server_side=True,
                                         suppress_ragged_eofs=conf.suppress_ragged_eofs,
                                         do_handshake_on_connect=conf.do_handshake_on_connect)