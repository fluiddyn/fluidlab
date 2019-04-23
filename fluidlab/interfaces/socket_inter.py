"""Interfaces with socket (:mod:`fluidlab.interfaces.socket_inter`)
===================================================================

Provides:

.. autoclass:: SocketInterface
   :members:
   :private-members:

"""

import socket


from fluidlab.interfaces import QueryInterface

class SocketInterface(QueryInterface):

    def __init__(self, ip_address, port, autoremove_eol=True):
        super(SocketInterface, self).__init__()
        self.ip_address = ip_address
        self.port = port
        self.autoremove_eol = autoremove_eol
        
    def __str__(self):
        return f'SocketInterface("{self.ip_address:}", {self.port:})'
        
    def __repr__(self):
        return str(self)
        
    def _open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port))
        
    def _close(self):
        self.socket.close()
        
    def _write(self, data):
        if isinstance(data, str):
            data = data.encode('ascii')
        if self.autoremove_eol and not data.endswith(b'\r\n'):
            data = data + b'\r\n'
        self.socket.sendall(data)
        
    def _read(self, timeout=10.0):
        self.socket.settimeout(timeout)
        chunks = []
        while True:
            chunk = self.socket.recv(1024)
            if len(chunk) > 0:
                chunks.append(chunk)
            if len(chunks) < 1024:
                break
        data = b"".join(chunks).decode("ascii")
        if self.autoremove_eol and data.endswith('\r\n'):
            data = data[:-2]
        return data
        
    
     