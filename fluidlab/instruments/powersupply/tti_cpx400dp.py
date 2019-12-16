"""tti_cpx400dp
===============

.. autoclass:: TtiCpx400dp
   :members:
   :private-members:


"""

__all__ = ["TtiCpx400dp"]

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue, BoolValue
from fluidlab.interfaces import PhysicalInterfaceType

class TtiCpx400dpUnitValue(FloatValue):
    def _convert_from_str(self, value):
        index_v = value.find("V")
        index_i = value.find("A")
        if index_v > index_i:
            index = index_v
        else:
            index = index_i
        return float(value[0:index])


class TtiCpx400dp(IEC60488):
    """Driver for the power supply TTI CPX400DP
    ===========================================

	Dual 420 watt DC Power Supply.

    Default interface is GPIB, but the device can work also
    with LAN, RS-232 and USB connection.
    USB connection is actually a USB-Serial converter.

    e.g. on linux with USB connection:

    .. code-block:: python

       with TtiCpx400dp('/dev/ttyACM0') as tti:
           tti.onoffall.set(True)
           v = tti.vdc.get(channel=1)
           print(v)

    On Windows or Linux with GPIB connection:

    .. code-block:: python

       with TtiCpx400dp('/dev/ttyACM0') as tti:
           tti.onoffall.set(True)
           v = tti.vdc.get(channel=1)
           print(v)
    """
    # the default params below are for use with Serial connection (RS-232 or USB)
    # they are ignored by the GPIBInterface, VISAInterface and SocketInterface
    # classes.
    default_inter_params = {
        "baudrate": 9600,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1,
        "timeout": 1,
        "xonxoff": True,
        "rtscts": False,
        "dsrdtr": False,
        "eol": "\r\n",
        "use_readlines": False,
    }

features = [
    TtiCpx400dpUnitValue(
        "vdc",
        doc="Get actual voltage/Set voltage setpoint on specified channel. Channel is 1 or 2.",
        command_set="V{channel:d} {value}",
        command_get="V{channel:d}O?",
        channel_argument=True,
        check_instrument_value=False,
    ),
    TtiCpx400dpUnitValue(
        "idc",
        doc="Get actual current/Set current setpoint on specified channel. Channel is 1 or 2.",
        command_set="I{channel:d} {value}",
        command_get="I{channel:d}O?",
        channel_argument=True,
        check_instrument_value=False,
    ),
    BoolValue(
        "onoff",
        doc="Toogle output ON/OFF for specified channel. Channel is 1 or 2.",
        command_set="OP{channel:d} {value}",
        command_get="OP{channel:d}?",
        channel_argument=True,
        check_instrument_value=False,
        true_string="1",
        false_string="0",
    ),
    BoolValue(
        "onoffall",
        doc="Toogle output ON/OFF for both channels simultaneously.",
        command_set="OPALL ",
        channel_argument=False,
        check_instrument_value=False,
        true_string="1",
        false_string="0",
    ),
]

TtiCpx400dp._build_class_with_features(features)
