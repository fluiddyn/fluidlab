"""julabo
=========

.. autoclass:: Julabo
   :members:
   :private-members:


"""

__all__ = ["Julabo"]

from serial import PARITY_EVEN
from fluidlab.instruments.drivers import Driver
from fluidlab.interfaces import PhysicalInterfaceType
from fluidlab.instruments.features import Value, FloatValue, BoolValue, IntValue
from time import sleep


class Julabo(Driver):
    default_physical_interface = PhysicalInterfaceType.Serial
    default_inter_params = {
        "baudrate": 9600,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1,
        "timeout": 5.0,
        "xonxoff": True,
        "rtscts": False,
        "dsrdtr": False,
        "eol": "\r\n",
        "autoremove_eol": True,
    }

    def __enter__(self):
        super(Julabo, self).__enter__()
        identification = self.interface.query("version")
        print("identification =", repr(identification))
        return self


features = [
    FloatValue(
        "setpoint",
        channel_argument=True,
        check_instrument_value=False,
        pause_instrument=0.5,
        command_get="in_sp_{channel:02d}",
        command_set="out_sp_{channel:02d} {value:.1f}",
    ),
    BoolValue(
        "onoff",
        command_set="out_mode_05",
        pause_instrument=0.5,
        check_instrument_value=False,
    ),
    FloatValue("temperature", pause_instrument=0.75, command_get="in_pv_00"),
    IntValue(
        "setpoint_channel",
        check_instrument_value=False,
        pause_instrument=0.5,
        command_get="in_mode_01",
        command_set="out_mode_01",
    ),
    Value("status", pause_instrument=0.5, command_get="status"),
]

Julabo._build_class_with_features(features)

if __name__ == "__main__":
    with Julabo("/dev/ttyS0") as chiller:
        chiller.setpoint.set(20.0, channel=0)
        chiller.setpoint_channel.set(0)
        chiller.onoff.set(True)

        # print(chiller.status.get())

        sp = chiller.setpoint.get(0)
        print("sp T1 =", sp, "deg")
        sp = chiller.setpoint.get(1)
        print("sp T2 =", sp, "deg")

        try:
            for i in range(10):
                print("T =", chiller.temperature.get(), "deg")
                sleep(1.0)
        except ValueError:
            print(chiller.interface.read())
        except KeyboardInterrupt:
            pass

    print("Finished")
