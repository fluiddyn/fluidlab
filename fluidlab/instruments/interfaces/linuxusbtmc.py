"""Interface with Linux USBTMC (:mod:`fluidlab.instruments.interface.linuxusbtmc.py`)
======================================================================================

This interface provides basic interface with USBTMC device. It uses the
linux devices at /dev/usbtmc[0-9], and thus makes use of the usbtmc
linux kernel support.
This is different from other modules, like python-usbtmc or pyvisa-py,
which disable the kernel usbtmc support and address the device directly.

This module is much simpler and merely rely on os.open and ioctl.

Provides:

.. autoclass:: LinuxUSBTMCInterface
   :members:
   :private-members:

"""

import os
from pathlib import Path
from time import sleep
from fluidlab.instruments.interfaces import QueryInterface


class LinuxUSBTMCInterface(QueryInterface):
    def __init__(self, device=0):
        """
        Create a new LinuxUSBTMCInterface.

        Input argument
        ==============

        device: Path('/dev/usbtmc0'), str or bytes '/dev/usbtmc0' or
                device number (e.g. 0)

        """
        if isinstance(device, bytes):
            device = device.decode("ascii")
        if isinstance(device, Path):
            device = device.as_posix()
        if isinstance(device, int):
            device = "/dev/usbtmc{:d}".format(device)

        self.devname = device
        self.dev = os.open(device, os.O_RDWR)
        self.write_termination = b"\n"
        self.read_termination = b"\n"

    def __del__(self):
        if self.dev:
            self.close()

    def write(self, message, tracing=False, verbose=False):
        # On prend a priori des bytes, mais si on nous donne un str
        # on convertit à condition que ce soit du pur ascii
        if isinstance(message, str):
            message = message.encode("ascii")
        if not message.endswith(self.write_termination):
            message += self.write_termination
        os.write(self.dev, message)

    def readline(self, maxbytes=1024):
        msg = os.read(self.dev, maxbytes)
        if msg.endswith(self.read_termination):
            N = len(msg) - len(self.read_termination) + 1
            msg = msg[:N]
        return msg

    def close(self):
        if self.dev:
            os.close(self.dev)
            self.dev = 0
            self.devname = None

    def read(self, maxbytes=1024, tracing=False, verbose=False):
        # Par compatibilité avec les autres interfaces, on renvoie
        # un str (à condition ascii).
        # Si c'est un appareil qui renvoie autre chose que de l'ascii
        # utiliser readline.
        return self.readline(maxbytes).decode("ascii")

    def query(self, command, time_delay=0.05, tracing=False, verbose=False):
        self.write(command)
        sleep(time_delay)
        return self.read()
