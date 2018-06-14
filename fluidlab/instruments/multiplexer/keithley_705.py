"""keithley_705
===============

.. autoclass:: Keithley705
   :members:
   :private-members:

"""

__all__ = ['Keithley705']

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import SuperValue, BoolValue

class Keithley705(IEC60488):
    """Driver for the multiplexer Keithley 705*

    """

    def query_identification(self):
        self.open_all_channels()
        return self.interface.read().strip()

    def close_channel(self, chan, display=True):
        self.interface.write("C{chan:03d} X".format(chan=chan))
        if display:
            self.interface.write("B{chan:03d} X".format(chan=chan))
             
    def open_channel(self, chan, display=True):
        self.interface.write("N{chan:03d} X".format(chan=chan))
        if display:
            self.interface.write("B{chan:03d} X".format(chan=chan))

    def open_all_channels(self):
        self.interface.write("R X")

    def display(self, string=None):
        if string is not None:
            self.interface.write("D4 {:} X".format(string))
        else:
            self.interface.write("D0 X")

if __name__ == '__main__':
    from fluidlab.instruments.interfaces.linuxgpib import GPIBInterface
    import time

    with Keithley705(GPIBInterface(0, 17)) as k:
        k.close_channel(1)
        k.close_channel(4)
        time.sleep(2)
        k.open_channel(1)
        k.open_channel(4)
