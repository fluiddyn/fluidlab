"""Interfaces with socket (:mod:`fluidlab.interfaces.socket_inter`)
===================================================================

Provides:

.. autoclass:: SocketInterface
   :members:
   :private-members:

"""

import socket
from ipaddress import ip_address

from fluidlab.interfaces import QueryInterface


class SocketInterface(QueryInterface):
    """
    Abstract base class.
    Concrete classes are UDPSocketInterface and TCPSocketInterface
    """

    def __init__(self, ip_address, autoremove_eol):
        super().__init__()
        self.ip_address = ip_address
        self.autoremove_eol = autoremove_eol

    def __str__(self):
        return f'SocketInterface("{self.ip_address:}")'

    def __repr__(self):
        return str(self)

    def _write(self, data):
        if isinstance(data, str):
            data = data.encode("ascii")
        if self.autoremove_eol and not data.endswith(b"\r\n"):
            data = data + b"\r\n"
        self._send(data)

    def _read(self, timeout=10.0):
        data = self._recv(timeout)
        if self.autoremove_eol and data.endswith("\r\n"):
            data = data[:-2]
        return data


class UDPSocketInterface(SocketInterface):
    def __init__(self, ip_address, in_port, out_port, autoremove_eol=True):
        super().__init__(ip_address, autoremove_eol)
        if callable(in_port):
            self.in_port = in_port(ip_address)
        else:
            self.in_port = in_port
        if callable(out_port):
            self.out_port = out_port(ip_address)
        else:
            self.out_port = out_port

    def _open(self):
        self.in_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.in_sock.bind(
            (socket.gethostbyname(socket.gethostname()), self.in_port)
        )
        self.out_sock.connect((self.ip_address, self.out_port))

    def _close(self):
        self.out_sock.close()
        self.in_sock.close()

    def _send(self, data):
        self.out_sock.sendall(data)

    def _recv(self, timeout):
        self.in_sock.settimeout(timeout)
        chunks = []
        while True:
            try:
                data, server = self.in_sock.recvfrom(1024)
            except socket.timeout:
                if not chunks:
                    raise
            if ip_address(server[0]) == ip_address(self.ip_address):
                chunks.append(data)
            if len(data) < 1024:
                break
        data = b"".join(chunks).decode("ascii")
        return data


class TCPSocketInterface(SocketInterface):
    def __init__(self, ip_address, port, autoremove_eol=True):
        super().__init__(ip_address, autoremove_eol)
        self.port = port

    def _open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port))

    def _close(self):
        self.socket.close()

    def _send(self, data):
        self.socket.sendall(data)

    def _recv(self, timeout):
        self.socket.settimeout(timeout)
        chunks = []
        while True:
            try:
                chunk = self.socket.recv(1024)
            except socket.timeout:
                if not chunks:
                    raise
            if len(chunk) > 0:
                chunks.append(chunk)
            if len(chunks) < 1024:
                break
        data = b"".join(chunks).decode("ascii")
        return data
