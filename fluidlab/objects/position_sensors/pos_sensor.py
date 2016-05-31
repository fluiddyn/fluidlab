
from __future__ import print_function

import os
import signal
import atexit
import sys

import numpy as np

import u3

from fluiddyn.util import time_as_str


path_save = os.path.join(os.path.expanduser("~"), '.fluidlab')
if not os.path.exists(path_save):
    os.mkdir(path_save)


def sig_handler(signo, frame):
    sys.exit(0)


class PositionSensor(object):
    """Communicate with the position sensor (2 output signals A and B in
    quadrature) via an acquisition card LabJack U3-HV.

    Parameters
    ----------

    port : {4, integer}

      Number of the FIO port on the card for A signal. B will be on
      the next port. Note tat you can't use AIN0-AIN3 which are
      dedicated for analog inputs.

    Notes
    -----

    The acquisition card considers these 2 signals as timers. They have to be
    configured in quadrature (mode 8).

    The sensor does not provide an absolute position but only a
    relative displacement. This class save the absolute position in a
    file save_position.txt.

    """

    def __init__(self, port=4):

        self.daq_u3 = u3.U3()
        self.daq_u3.configIO(TimerCounterPinOffset=port,
                             NumberOfTimersEnabled=2, FIOAnalog=0)
        self.daq_u3.getFeedback(u3.Timer0Config(8), u3.Timer1Config(8))

        self.meter_per_increment = 0.000105/4

        try:
            self._shift_absolute_pos, self._shift_relative_pos = self.load()
        except IOError:
            self._shift_relative_pos = 0.
            self._shift_absolute_pos = 0.

        atexit.register(self.save)
        signal.signal(signal.SIGTERM, sig_handler)

    def get_value_counter(self):
        return self.daq_u3.getFeedback(u3.QuadratureInputTimer())[0]

    def get_relative_position(self):
        counter = self.get_value_counter()
        return counter * self.meter_per_increment + self._shift_relative_pos

    def get_absolute_position(self):
        counter = self.get_value_counter()
        return counter * self.meter_per_increment + self._shift_absolute_pos

    def reset_counter_to_zero(self):
        self._shift_relative_pos = self.get_relative_position()
        self._shift_absolute_pos = self.get_absolute_position()
        self.daq_u3.getFeedback(u3.Timer0(UpdateReset=True),
                                u3.Timer1(UpdateReset=True))

    def set_relative_origin(self, value=0.):
        rel_pos = self.get_relative_position()
        self._shift_relative_pos += value - rel_pos

    def set_absolute_origin(self, value=0.):
        abs_pos = self.get_absolute_position()
        self._shift_absolute_pos += value - abs_pos

    def save(self):
        abs_pos = self.get_absolute_position()
        rel_pos = self.get_relative_position()
        print('save positions:', [abs_pos, rel_pos])
        data = np.array([abs_pos, rel_pos])
        date = time_as_str()
        path = os.path.join(path_save, 'positions_sensor.txt')

        np.savetxt(
            path, data, fmt='%.8e',
            header=date + ': positions (absolute and relative, m)')

    def load(self):
        path = os.path.join(path_save, 'positions_sensor.txt')
        return np.loadtxt(path)

if __name__ == '__main__':
    sensor = PositionSensor()
