"""mmr3
============

.. autoclass:: MMR3
   :members:
   :private-members:

This class implements the MMR3 from the Institut Néel - VERSION 2.4

"""

from ipaddress import ip_address

from fluidlab.interfaces import PhysicalInterfaceType
from fluidlab.instruments.drivers import Driver
from fluidlab.instruments.features import (
    QueryCommand,
    WriteCommand,
    FloatValue,
    StringValue,
)

__all__ = ["MMR3"]


def out_port(ip):
    """
    Out port is 12000 + last number of ip address
    """
    ip = ip_address(ip)
    return 12000 + (int(ip) & 0xFF)


class MMR3(Driver):
    default_physical_interface = PhysicalInterfaceType.Ethernet
    default_inter_params = {
        "out_port": out_port,
        "in_port": 12000,
        "ethernet_protocol": "udp",
    }


features = [
    # Identification Query
    QueryCommand("query_identification", "Identification Query", "*IDN?"),
    # # # # # # # # # # # #
    # Read-only commands  #
    # # # # # # # # # # # #
    FloatValue(
        "temperature", doc="MMR3 internal temperature", command_get="MMR3GET 2"
    ),
    # CH1 commands
    FloatValue(
        "r1_meas", doc="MMR3 R1 measurement result", command_get="MMR3GET 3"
    ),
    FloatValue(
        "r1_range", doc="MMR3 R1 range computation", command_get="MMR3GET 4"
    ),
    FloatValue(
        "r1_convert", doc="MMR3 R1 converted value", command_get="MMR3GET 5"
    ),
    FloatValue(
        "r1_status", doc="MMR3 R1 measurement status", command_get="MMR3GET 6"
    ),
    FloatValue(
        "r1_offset", doc="MMR3 R1 offset measurement", command_get="MMR3GET 13"
    ),
    # CH2 commands
    FloatValue(
        "r2_meas", doc="MMR3 R2 measurement result", command_get="MMR3GET 14"
    ),
    FloatValue(
        "r2_range", doc="MMR3 R2 range computation", command_get="MMR3GET 15"
    ),
    FloatValue(
        "r2_convert", doc="MMR3 R2 converted value", command_get="MMR3GET 16"
    ),
    FloatValue(
        "r2_status", doc="MMR3 R2 measurement status", command_get="MMR3GET 17"
    ),
    FloatValue(
        "r2_offset", doc="MMR3 R2 offset measurement", command_get="MMR3GET 24"
    ),
    # CH3 commands
    FloatValue(
        "r3_meas", doc="MMR3 R3 measurement result", command_get="MMR3GET 25"
    ),
    FloatValue(
        "r3_range", doc="MMR3 R3 range computation", command_get="MMR3GET 26"
    ),
    FloatValue(
        "r3_convert", doc="MMR3 MMR3 R3 converted value", command_get="MMR3GET 27"
    ),
    FloatValue(
        "r3_status", doc="MMR3 R3 measurement status", command_get="MMR3GET 28"
    ),
    FloatValue(
        "r3_offset", doc="MMR3 R3 offset measurement", command_get="MMR3GET 35"
    ),
    # # # # # # # # # #
    #  R+W commands   #
    # # # # # # # # # #
    FloatValue(
        "periode",
        doc="MMR3 Modulation period",
        command_get="MMR3GET 0",
        command_set="MMR3SET 0",
        pause_instrument=0.5,
    ),
    FloatValue(
        "dtadc",
        doc="MMR3 ADC delay",
        command_get="MMR3GET 1",
        command_set="MMR3SET 1",
        pause_instrument=0.5,
    ),
    # CH1 commands
    FloatValue(
        "r1_average",
        doc="MMR3 R1 Amount of points in each measurement",
        command_get="MMR3GET 7",
        command_set="MMR3SET 7",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r1_rangemode",
        doc="MMR3 R1 change mode",
        command_get="MMR3GET 8",
        command_set="MMR3SET 8",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r1_rangemode_i",
        doc="MMR3 R1 change mode auto/manual",
        command_get="MMR3GET 9",
        command_set="MMR3SET 9",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r1_range_i",
        doc="MMR3 R1 change flux range",
        command_get="MMR3GET 10",
        command_set="MMR3SET 10",
        pause_instrument=1,
    ),
    FloatValue(
        "r1_range_u",
        doc="MMR3 R1 change voltage range",
        command_get="MMR3GET 11",
        command_set="MMR3SET 11",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r1_i",
        doc="MMR3 R1 change polarization",
        command_get="MMR3GET 12",
        command_set="MMR3SET 12",
        pause_instrument=1,
    ),
    # CH2 commands
    FloatValue(
        "r2_average",
        doc="MMR3 R2 Amount of points in each measurement",
        command_get="MMR3GET 18",
        command_set="MMR3SET 18",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r2_rangemode",
        doc="MMR3 R2 change mode",
        command_get="MMR3GET 19",
        command_set="MMR3SET 19",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r2_rangemode_i",
        doc="MMR3 R2 change mode auto/manual",
        command_get="MMR3GET 20",
        command_set="MMR3SET 20",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r2_range_i",
        doc="MMR3 R2 change flux range",
        command_get="MMR3GET 21",
        command_set="MMR3SET 21",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r2_range_u",
        doc="MMR3 R2 change voltage range",
        command_get="MMR3GET 22",
        command_set="MMR3SET 22",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r2_i",
        doc="MMR3 R2 change polarization",
        command_get="MMR3GET 23",
        command_set="MMR3SET 23",
        pause_instrument=0.5,
    ),
    # CH3 commands
    FloatValue(
        "r3_average",
        doc="MMR3 R3 Amount of points in each measurement",
        command_get="MMR3GET 29",
        command_set="MMR3SET 29",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r3_rangemode",
        doc="MMR3 R3 change mode",
        command_get="MMR3GET 30",
        command_set="MMR3SET 30",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r3_rangemode_i",
        doc="MMR3 R3 change mode auto/manual",
        command_get="MMR3GET 31",
        command_set="MMR3SET 31",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r3_range_i",
        doc="MMR3 R3 change flux range",
        command_get="MMR3GET 32",
        command_set="MMR3SET 32",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r3_range_u",
        doc="MMR3 R3 change voltage range",
        command_get="MMR3GET 33",
        command_set="MMR3SET 33",
        pause_instrument=0.5,
    ),
    FloatValue(
        "r3_i",
        doc="MMR3 R3 change polarization",
        command_get="MMR3GET 34",
        command_set="MMR3SET 34",
        pause_instrument=0.5,
    ),
]

MMR3._build_class_with_features(features)
