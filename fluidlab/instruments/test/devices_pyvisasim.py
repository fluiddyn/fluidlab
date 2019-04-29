"""Example with a device defined in pyvisa-sim
==============================================

"""

from fluidlab.interfaces import PhysicalInterfaceType, set_default_interface
from fluidlab.interfaces.visa_inter import set_default_pyvisa_backend

from fluidlab.instruments.drivers import Driver

from fluidlab.instruments.features import (
    QueryCommand,
    StringValue,
    FloatValue,
    BoolValue,
)

set_default_interface(PhysicalInterfaceType.Serial, "VISAInterface")
set_default_pyvisa_backend("@sim")


class Device2(Driver):
    """Simple instrument driver

    The instrument is defined in pyvisa-sim (as "device 2").

    """


Device2._build_class_with_features(
    [
        QueryCommand("get_idn", doc="Get identity", command_str="*IDN?"),
        StringValue(
            "rail",
            doc="A string rail",
            command_set="INST",
            valid_values=["P6V", "P25V", "N25V"],
        ),
        FloatValue(
            "voltage",
            doc="The voltage (in V)",
            command_set=":VOLT:IMM:AMPL",
            limits=[0, 6],
        ),
        FloatValue(
            "current",
            doc="The current (in A)",
            command_set=":CURR:IMM:AMPL",
            limits=[0, 6],
        ),
        BoolValue("output_enabled", doc="Output enabled", command_set="OUTP"),
    ]
)


if __name__ == "__main__":
    dev = Device2("ASRL2::INSTR")
