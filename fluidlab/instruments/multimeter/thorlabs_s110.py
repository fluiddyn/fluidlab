"""thorlabs_s110
================

.. autoclass:: ThorlabsS110
   :members:
   :private-members:

   This class implements the RS-232 remote control of the Thorlabs Optical Meter
   S110.
   
"""

from fluidlab.instruments.drivers import Driver
from fluidlab.instruments.interfaces.serial_inter import SerialInterface
from fluidlab.instruments.features import StringValue, FloatValue

__all__ = ["ThorlabsS110"]


class ThorlabsS110(Driver):
    def __init__(self, serialPort):
        interface = SerialInterface(
            serialPort,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=2,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
            eol="\r",
            multilines=True,
        )
        super(ThorlabsS110, self).__init__(interface)


features = [
    StringValue(
        "head", doc="Read head info", command_get="H\r", pause_instrument=0.5
    ),
    FloatValue(
        "power", doc="Read current power", command_get="P\r", pause_instrument=0.5
    ),
]

ThorlabsS110._build_class_with_features(features)

if __name__ == "__main__":
    meter = ThorlabsS110("COM2")
    head_info = meter.head.get()
    print(head_info)
    power = meter.power.get()
    print("Current power:", power / 1000, "mW")
