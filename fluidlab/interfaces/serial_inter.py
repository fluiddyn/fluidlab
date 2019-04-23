"""Interfaces with serial (:mod:`fluidlab.interfaces.serial_inter`)
===================================================================

Provides:

.. autoclass:: SerialInterface
   :members:
   :private-members:

"""

import serial
import io

from time import sleep

from fluidlab.interfaces import QueryInterface


class SerialInterface(QueryInterface):
    def __init__(
        self,
        port,
        baudrate=9600,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
        eol=None,
        multilines=False,
        autoremove_eol=False,
    ):
        """
        if eol is not None, the serial port is wrapped into TextIOWrapper to
        allow readline to wait for an eol which is not \n

        Example: if eol='\r\n', '\n' on input is translated to '\r\n' before sending
                 to the device,
                 and read newlines are translated into '\r\n'

        To automatically add '\n' on writes, and remove '\r\n' on reads, set
        autoremove_eol to True
        """
        super(SerialInterface, self).__init__()
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.dsrdtr = dsrdtr
        self.eol = eol
        self.multilines = multilines
        self.autoremove_eol = autoremove_eol
        
    def _open(self):

        # open serial port
        sp = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
            timeout=self.timeout,
            xonxoff=self.xonxoff,
            rtscts=self.rtscts,
            dsrdtr=self.dsrdtr,
        )
        self._lowlevel = self.serial_port = sp
        self._close = sp.close
        if self.eol is not None:
            self.ser_io = io.TextIOWrapper(
                io.BufferedRWPair(sp, sp, 1), newline=self.eol, line_buffering=True
            )

    def _write(self, *args):
        if self.autoremove_eol:
            args = [a.strip() + "\n" for a in args]
        # print('->', repr(args[0]))
        if self.eol is not None:
            return self.ser_io.write(*args)

        # ensure no unicode strings sent to serial_port.write
        args = [a.encode("ascii") if isinstance(a, str) else a for a in args]
        return self.serial_port.write(*args)

    def readline(self, *args):
        if self.eol is not None:
            result = self.ser_io.readline(*args)
            if self.autoremove_eol:
                n = len(self.eol)
                return result[:-n]
            else:
                return result

        return self.serial_port.readline(*args)

    def readlines(self, *args):
        if self.eol is not None:
            result = self.ser_io.readlines(*args)
            if self.autoremove_eol:
                n = len(self.eol)
                return [r[:-n] for r in result]
            else:
                return result

        return self.serial_port.readlines(*args)

    def _read(self):
        if self.multilines:
            result = self.readlines()
            return "\n".join(result)

        else:
            result = self.readline()
            if isinstance(result, str):
                # print("<-", repr(result))
                return result
            # print("<-", repr(b"\n".join(result.splitlines())))
            return b"\n".join(result.splitlines())


if __name__ == "__main__":
    with SerialInterface("/dev/ttyUSB0") as interface:
        print(interface.query(b"*IDN?\r\n", time_delay=1))
        print(interface.query(b"*IDN?\r\n"))
        print(interface.query(b"ISET1?\r\n"))
        print(interface.query(b"HELP?\r\n", time_delay=0))
