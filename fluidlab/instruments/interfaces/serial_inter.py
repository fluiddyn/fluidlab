"""Interfaces with serial (:mod:`fluidlab.instruments.interfaces.serial_inter`)
===============================================================================

Provides:

.. autoclass:: SerialInterface
   :members:
   :private-members:

"""

import serial

from time import sleep

from fluidlab.instruments.interfaces import QueryInterface


class SerialInterface(QueryInterface):
    def __init__(self, port, baudrate=9600, bytesize=8,
                 parity='N', stopbits=1, timeout=1, xonxoff=False,
                 rtscts=False, dsrdtr=False):

        # open serial port
        sp = serial.Serial(
            port=port, baudrate=baudrate, bytesize=bytesize,
            parity=parity, stopbits=stopbits, timeout=timeout,
            xonxoff=xonxoff, rtscts=rtscts, dsrdtr=dsrdtr)
        self._lowlevel = self.serial_port = sp
        self.write = sp.write
        self.read = sp.read
        self.readline = sp.readline
        self.close = sp.close

        self.query('*IDN?\r\n')

    def query(self, command, latence=0., method='line'):
        self.write(command)
        sleep(latence)
        if method == 'line':
            result = self.serial_port.readline()
        elif method == 'all':
            result = self.serial_port.readall()
        else:
            raise ValueError()
        return '\n'.join(result.splitlines())


if __name__ == '__main__':
    interface = SerialInterface('/dev/ttyUSB0')

    print(interface.query('*IDN?\r\n', 1))
    print(interface.query('*IDN?\r\n'))
    print(interface.query('ISET1?\r\n'))
    print(interface.query('HELP?\r\n', latence=0))

