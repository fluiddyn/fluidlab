"""thermocube
=============

.. autoclass:: Thermocube
   :members:
   :private-members:

"""

from typing import NamedTuple
from time import sleep

from fluidlab.instruments.drivers import Driver
from fluidlab.instruments.interfaces.serial_inter import SerialInterface
from fluidlab.instruments.features import Value

__all__ = ["Thermocube"]


class ThermocubeControlParameter(NamedTuple):
    value: int
    description: str
    nbytes: int


ControlParameter_SP = ThermocubeControlParameter(
    description="Chiller set point 1 temperature", value=0b00001, nbytes=2
)
ControlParameter_FT = ThermocubeControlParameter(
    description="Current fluid temperature at chiller coolant output",
    value=0b01001,
    nbytes=2,
)
ControlParameter_FC = ThermocubeControlParameter(
    description="Faults from chiller (fan, pump, RTD failure, etc.)",
    value=0b01000,
    nbytes=1,
)

ControlParameter_NO = ThermocubeControlParameter(
    description="No-op", value=0, nbytes=0
)

ControlParameters = [
    ControlParameter_SP,
    ControlParameter_FT,
    ControlParameter_FC,
    ControlParameter_NO,
]


def thermocube_message(
    remote_control=True,
    on_off=True,
    dir_remote_to_chiller=True,
    control_parameter=0b00001,
    data=None,
):
    # Check input parameters
    if isinstance(control_parameter, int):
        for cp in ControlParameters:
            if cp.value == control_parameter:
                break

        else:
            raise ValueError("Wrong control_parameter value")

    elif control_parameter not in ControlParameters:
        raise ValueError("Wrong control_parameter value")

    else:
        cp = control_parameter
    assert cp in ControlParameters

    command_byte = bytes(
        [
            remote_control << 7
            | on_off << 6
            | dir_remote_to_chiller << 5
            | cp.value & 0x0F
        ]
    )
    if data:
        if len(data) != cp.nbytes:
            raise ValueError("Wrong number of bytes in data")

        return command_byte + data

    return command_byte


class ThermocubeValue(Value):
    def __init__(self, name, control_parameter=ControlParameter_NO):
        super(ThermocubeValue, self).__init__(
            name,
            doc=control_parameter.description,
            command_set=None,
            command_get=None,
            check_instrument_value=False,
            pause_instrument=False,
            channel_argument=False,
        )
        self.cp = control_parameter

    def get(self):
        self._interface.write(
            thermocube_message(
                control_parameter=self.cp, dir_remote_to_chiller=False
            )
        )
        sleep(1)
        answer = self._interface._lowlevel.read(size=self.cp.nbytes)
        if self.cp.nbytes == 2:
            return (answer[0] | answer[1] << 8) / 10

        else:
            return answer[0]

    def set(self, v):
        value = int(v * 10)
        low_byte = value & 0x00FF
        high_byte = value & 0xFF00
        data = bytes([low_byte, high_byte])
        msg = thermocube_message(
            control_parameter=ControlParameter_SP,
            dir_remote_to_chiller=True,
            data=data,
        )
        self._interface.write(msg)


class Thermocube(Driver):
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
        )
        super(Thermocube, self).__init__(interface)


features = [
    ThermocubeValue("setpoint", control_parameter=ControlParameter_SP),
    ThermocubeValue("temperature", control_parameter=ControlParameter_FT),
    ThermocubeValue("fault", control_parameter=ControlParameter_FC),
]

Thermocube._build_class_with_features(features)

if __name__ == "__main__":
    cube = Thermocube("COM1")
    setpoint = cube.setpoint.get()
    print("Temperature setpoint is", setpoint, "°C")
    T = cube.temperature.get()
    print("Current fluid temperature is", T, "°C")
    faults = cube.faults.get()
    print("Faults are:", faults)
