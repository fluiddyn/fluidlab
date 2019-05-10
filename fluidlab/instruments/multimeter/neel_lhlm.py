"""neel_lhlm
============

.. autoclass:: NeelLHLM
   :members:
   :private-members:

This class implements the Liquid Helium Level Meter from Institut Néel

"""

from ipaddress import ip_address

from fluidlab.interfaces import PhysicalInterfaceType
from fluidlab.instruments.drivers import Driver
from fluidlab.instruments.features import QueryCommand, WriteCommand, FloatValue, StringValue

__all__ = ["NeelLHLM"]


def out_port(ip):
    """
    Out port is 12000 + last number of ip address
    """
    ip = ip_address(ip)
    return 12000 + (int(ip) & 0xFF) 
    

class NeelLHLM(Driver):
    default_physical_interface = PhysicalInterfaceType.Ethernet
    default_inter_params = {
        "out_port": out_port,
        "in_port": 12000,
        "ethernet_protocol": "udp",
    }

class PrefixValue(FloatValue):

    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix')
        self._fmt = self.prefix + ":{:.4f}"
        super().__init__(*args, **kwargs)

    def _convert_from_str(self, value):
        data = value.split(':')
        if data[0] != self.prefix:
            raise ValueError(f'Wrong value "{value:}"')
        try:
            return float(data[1])
        except ValueError:
            return 0.0
        

features = [
    QueryCommand("query_identification", "Identification query", "*IDN?"),
    WriteCommand("start_measurement", "Start a measurement", "MEAS"),
    PrefixValue("level",
               doc="Helium level in meters",
               command_get="LEVEL?",
               prefix="LEVEL"),
    PrefixValue("volume",
                doc="Helium volume in liters",
                command_get="VOLUME?",
                prefix="VOLUME"),
    WriteCommand("reboot", "Restart device", "REBOOT"),
    WriteCommand("automode", "Activate auto mode", "AUTOMODE"),
    WriteCommand("manualmode", "Activate manual mode", "MANUALMODE"),
    PrefixValue("ohm",
                doc="Resistance in ohms",
                command_get="RES?",
                prefix="RES"),
    StringValue("mode",
                doc="Measurement mode",
                command_get="MODE?"),
    PrefixValue("vdc",
                doc="Wire voltage",
                command_get="VOLTAGE?",
                prefix="VOLTAGE"),
    StringValue("datasource",
                doc="Source of probe parameters",
                command_get="DATASOURCE?")
    ]

NeelLHLM._build_class_with_features(features)

if __name__ == '__main__':
    with NeelLHLM('192.168.0.4') as lhlm:
        identification = lhlm.query_identification()
        print('ID:', identification)
        level = lhlm.level.get()
        volume = lhlm.volume.get()
        print('Level =', level, 'm')
        print('Volume =', volume, 'L')
