"""mgc3
============

.. autoclass:: MGC3
   :members:
   :private-members:

This class implements the MGC3 from the Institut Néel - VERSION 2.4

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

__all__ = ["MGC3"]


def out_port(ip):
    """
    Out port is 12000 + last number of ip address
    """
    ip = ip_address(ip)
    return 12000 + (int(ip) & 0xFF)


class MGC3(Driver):
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
        "temperature", doc="MGC3 internal temperature", command_get="MGC3GET 0"
    ),
    # PID0 commands
    FloatValue(
        "pid0_meas",
        doc="MGC3 PID_0 last measurement - in Kelvin",
        command_get="MGC3GET 3",
    ),
    FloatValue(
        "pid0_s", doc="MGC3 PID_0 last watt measurement", command_get="MGC3GET 9"
    ),
    FloatValue("pid0_status", doc="MGC3 PID_0 Status", command_get="MGC3GET 10"),
    # PID1 commands
    FloatValue(
        "pid1_meas",
        doc="MGC3 PID_1 last measurement - in Kelvin",
        command_get="MGC3GET 15",
    ),
    FloatValue(
        "pid1_s", doc="MGC3 PID_1 last watt measurement", command_get="MGC3GET 21"
    ),
    FloatValue("pid1_status", doc="MGC3 PID_1 Status", command_get="MGC3GET 22"),
    # PID2 commands
    FloatValue(
        "pid2_meas",
        doc="MGC3 PID_1 last measurement - in Kelvin",
        command_get="MGC3GET 27",
    ),
    FloatValue(
        "pid2_s", doc="MGC3 PID_1 last watt measurement", command_get="MGC3GET 33"
    ),
    FloatValue("pid2_status", doc="MGC3 PID_1 Status", command_get="MGC3GET 34"),
    # Misc commands
    FloatValue("i0_status", doc="MGC3 CH_0 Status", command_get="MGC3GET 38"),
    FloatValue("i1_status", doc="MGC3 CH_1 Status", command_get="MGC3GET 40"),
    FloatValue("i2_status", doc="MGC3 CH_2 Status", command_get="MGC3GET 42"),
    FloatValue(
        "user_voltage", doc="MGC3 Current user voltage", command_get="MGC3GET 43"
    ),
    # # # # # # # # # #
    #  R+W commands   #
    # # # # # # # # # #
    # PID0 commands
    FloatValue(
        "pid0_onoff",
        doc="MGC3 PID 0, on (1) - off (0)",
        command_get="MGC3GET 1",
        command_set="MGC3SET 1",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid0_setpoint",
        doc="MGC3 PID 0, set wanted temperature (Kelvin)",
        command_get="MGC3GET 2",
        command_set="MGC3SET 2",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid0_prop",
        doc="MGC3 PID 0, proportional term",
        command_get="MGC3GET 4",
        command_set="MGC3SET 4",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid0_integral",
        doc="MGC3 PID 0, integral term",
        command_get="MGC3GET 5",
        command_set="MGC3SET 5",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid0_deriv",
        doc="MGC3 PID 0, derivative term",
        command_get="MGC3GET 6",
        command_set="MGC3SET 6",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid0_maxpow",
        doc="MGC3 PID 0, maximum power (W)",
        command_get="MGC3GET 7",
        command_set="MGC3SET 7",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid0_res",
        doc="MGC3 PID 0, Heat resistance value (Ohm)",
        command_get="MGC3GET 8",
        command_set="MGC3SET 8",
        pause_instrument=0.5,
    ),
    StringValue(
        "pid0_name",
        doc="MGC3 PID 0, measurement model name",
        command_get="MGC3GET 11",
        command_set="MGC3SET 11",
        pause_instrument=1,
        check_instrument_value=False,
    ),
    FloatValue(
        "pid0_channel",
        doc="MGC3 PID 0, measurement channel",
        command_get="MGC3GET 12",
        command_set="MGC3SET 12",
        pause_instrument=0.5,
    ),
    # PID1 commands
    FloatValue(
        "pid1_onoff",
        doc="MGC3 PID 1, on (1) - off (0)",
        command_get="MGC3GET 13",
        command_set="MGC3SET 13",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid1_setpoint",
        doc="MGC3 PID 1, set wanted temperature (Kelvin)",
        command_get="MGC3GET 14",
        command_set="MGC3SET 14",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid1_prop",
        doc="MGC3 PID 1, proportional term",
        command_get="MGC3GET 16",
        command_set="MGC3SET 16",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid1_integral",
        doc="MGC3 PID 1, integral term",
        command_get="MGC3GET 17",
        command_set="MGC3SET 17",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid1_deriv",
        doc="MGC3 PID 1, derivative term",
        command_get="MGC3GET 18",
        command_set="MGC3SET 18",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid1_maxpow",
        doc="MGC3 PID 1, maximum power (W)",
        command_get="MGC3GET 19",
        command_set="MGC3SET 19",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid1_res",
        doc="MGC3 PID 1, Heat resistance value (Ohm)",
        command_get="MGC3GET 20",
        command_set="MGC3SET 20",
        pause_instrument=0.5,
    ),
    StringValue(
        "pid1_name",
        doc="MGC3 PID 1, measurement model name",
        command_get="MGC3GET 23",
        command_set="MGC3SET 23",
        pause_instrument=2,
    ),
    FloatValue(
        "pid1_channel",
        doc="MGC3 PID 1, measurement channel",
        command_get="MGC3GET 24",
        command_set="MGC3SET 24",
        pause_instrument=0.5,
    ),
    # PID2 commands
    FloatValue(
        "pid2_onoff",
        doc="MGC3 PID 2, on (1) - off (0)",
        command_get="MGC3GET 25",
        command_set="MGC3SET 25",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid2_setpoint",
        doc="MGC3 PID 2, set wanted temperature (Kelvin)",
        command_get="MGC3GET 26",
        command_set="MGC3SET 26",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid2_prop",
        doc="MGC3 PID 2, proportional term",
        command_get="MGC3GET 28",
        command_set="MGC3SET 28",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid2_integral",
        doc="MGC3 PID 2, integral term",
        command_get="MGC3GET 29",
        command_set="MGC3SET 29",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid2_deriv",
        doc="MGC3 PID 2, derivative term",
        command_get="MGC3GET 30",
        command_set="MGC3SET 30",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid2_maxpow",
        doc="MGC3 PID 2, maximum power (W)",
        command_get="MGC3GET 31",
        command_set="MGC3SET 31",
        pause_instrument=0.5,
    ),
    FloatValue(
        "pid2_res",
        doc="MGC3 PID 2, Heat resistance value (Ohm)",
        command_get="MGC3GET 32",
        command_set="MGC3SET 32",
        pause_instrument=0.5,
    ),
    StringValue(
        "pid2_name",
        doc="MGC3 PID 2, measurement model name",
        command_get="MGC3GET 35",
        command_set="MGC3SET 35",
        pause_instrument=2,
    ),
    FloatValue(
        "pid2_channel",
        doc="MGC3 PID 2, measurement channel",
        command_get="MGC3GET 36",
        command_set="MGC3SET 36",
        pause_instrument=0.5,
    ),
    # I commands
    FloatValue(
        "ch0_i",
        doc="MGC3 CH0 change or get current",
        command_get="MGC3GET 37",
        command_set="MGC3SET 37",
        pause_instrument=0.5,
    ),
    FloatValue(
        "ch1_i",
        doc="MGC3 CH1 change or get current",
        command_get="MGC3GET 39",
        command_set="MGC3SET 39",
        pause_instrument=0.5,
    ),
    FloatValue(
        "ch2_i",
        doc="MGC3 CH2 change or get current",
        command_get="MGC3GET 41",
        command_set="MGC3SET 41",
        pause_instrument=0.5,
    ),
    # TTL commands
    FloatValue(
        "ttl_o1",
        doc="MGC3 TTL output 1",
        command_get="MGC3GET 44",
        command_set="MGC3SET 44",
        pause_instrument=0.5,
    ),
    FloatValue(
        "ttl_o2",
        doc="MGC3 TTL output 2",
        command_get="MGC3GET 45",
        command_set="MGC3SET 45",
        pause_instrument=0.5,
    ),
]

MGC3._build_class_with_features(features)
