"""Interfaces with serial (:mod:`fluidlab.instruments.interfaces.serial_inter`)
===============================================================================

Provides:

.. autoclass:: SerialInterface
   :members:
   :private-members:

"""

import serial
import io

from time import sleep

from fluidlab.instruments.interfaces import QueryInterface

class SerialInterface(QueryInterface):
    def __init__(self, port, baudrate=9600, bytesize=8,
                 parity='N', stopbits=1, timeout=1, xonxoff=False,
                 rtscts=False, dsrdtr=False, eol=None, multilines=False):
        """
        if eol is not None, the serial port is wrapped into TextIOWrapper to
        allow readline to wait for an eol which is not \n
        """

        # open serial port
        sp = serial.Serial(
            port=port, baudrate=baudrate, bytesize=bytesize,
            parity=parity, stopbits=stopbits, timeout=timeout,
            xonxoff=xonxoff, rtscts=rtscts, dsrdtr=dsrdtr)
        self._lowlevel = self.serial_port = sp
        self.close = sp.close
        self.eol = eol
        self.multilines = multilines
        if eol is not None:
            self.ser_io = io.TextIOWrapper(io.BufferedRWPair(sp, sp, 1),
                                           newline = eol,
                                           line_buffering = True)
            
    def write(self, *args):
        if self.eol is not None:
            return self.ser_io.write(*args)
        return self.serial_port.write(*args)
        
    def readline(self, *args):
        if self.eol is not None:
            return self.ser_io.readline(*args)
        return self.serial_port.readline(*args)
    
    def readlines(self, *args):
        if self.eol is not None:
            return self.ser_io.readlines(*args)
        return self.serial_port.readlines(*args)
        
    def read(self):
        if self.multilines:
            result = self.readlines()
            return '\n'.join(result)
        else:
            result = self.readline()
            if isinstance(result, str):
                return result
            return b'\n'.join(result.splitlines())

    def query(self, command, latence=0.):
        self.write(command)
        sleep(latence)
        return self.read()


if __name__ == '__main__':
    interface = SerialInterface('/dev/ttyUSB0')

    print(interface.query(b'*IDN?\r\n', latence=1))
    print(interface.query(b'*IDN?\r\n'))
    print(interface.query(b'ISET1?\r\n'))
    print(interface.query(b'HELP?\r\n', latence=0))
