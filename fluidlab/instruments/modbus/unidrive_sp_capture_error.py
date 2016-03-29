from __future__ import print_function

from fluidlab.instruments.modbus.unidrive_sp import \
    ServoUnidriveSP

from fluiddyn.util.terminal_colors import print_fail, print_warning

from fluidlab.exp import Timer

from fluiddyn.util.timer import Timer2

import numpy as np


def attempt(func, *args, **kwargs):
    """Attempt to call a function."""

    if 'maxattempt' in kwargs:
        maxattempt = kwargs.pop('maxattempt')
    else:
        maxattempt = 100

    test = 1
    count = 1
    while test:
        try:
            func(*args, **kwargs)
            test = 0
        except (ValueError, IOError):
            if count <= maxattempt:
                count += 1
            else:
                break

    return count


class ServoUnidriveSPCaptureError(ServoUnidriveSP):
    """Robust ServoUnidriveSP class."""
    isprintall = 0
    isprint_error = 1

    def set_target_rotation_rate(self, rotation_rate, check=False,
                                 maxattempt=10):
        """Set the target rotation rate in rpm."""

        count = attempt(
            super(ServoUnidriveSPCaptureError, self).set_target_rotation_rate,
            rotation_rate, check, maxattempt=maxattempt)
        if count == maxattempt + 1:
            print_fail(
                'set rotation at ' + str(rotation_rate) +
                ' rpm aborted (number of attempt exceeds ' +
                str(maxattempt) + ')')
        elif count > 1 and (self.isprint_error or self.isprintall):
            print_warning('set rotation to ' + str(rotation_rate) +
                          ' rpm at the ' + str(count) + 'th attempt')
        elif self.isprintall:
            print('set rotation to ' + str(rotation_rate) + ' rpm')
        return count


    def get_target_rotation_rate(self):
        """Get the target rotation rate in rpm."""
        count = attempt(
            super(ServoUnidriveSPCaptureError, self).get_target_rotation_rate)

        if count > 1 and (self.isprint_error or self.isprintall):
            print_warning(
                'got rotation at the ' + str(count) + 'th attempt')

    def start_rotation(self, speed=None, direction=None):
        count = attempt(
            super(ServoUnidriveSPCaptureError, self).start_rotation,
            speed, direction)

        if count > 1 and (self.isprint_error or self.isprintall):
            print_warning('start rotation at ' + str(speed) +
                          ' rpm at the ' + str(count) + 'th attempt')
        elif self.isprintall:
            print('start rotation at ' + str(speed) + ' rpm')

    def stop_rotation(self):
        count = attempt(
            super(ServoUnidriveSPCaptureError, self).stop_rotation)

        if count > 1 and (self.isprint_error or self.isprintall):
            print_warning('stop rotation at the ' + str(count) + 'th attempt')
        elif self.isprintall:
            print('stop rotation')

    def unlock(self):
        count = attempt(
            super(ServoUnidriveSPCaptureError, self).unlock)

        if count > 1 and (self.isprint_error or self.isprintall):
            print_warning('unlocked at the ' + str(count) + 'th attempt')
        elif self.isprintall:
            print('unlocked')

    def lock(self):
        count = attempt(
            super(ServoUnidriveSPCaptureError, self).lock)
        if count > 1 and (self.isprint_error or self.isprintall):
            print_warning('unlocked at the ' + str(count) + 'th attempt')
        elif self.isprintall:
            print('locked')

    def set_acceleration_time(self, acc, check=False, maxattempt=10):
        """Set the acceleration time XXs / 1000 rpm"""

        if acc >= 0:
            count = attempt(
                super(ServoUnidriveSPCaptureError, self).acceleration_time.set,
                acc, check, maxattempt=maxattempt)
        else:
           count = attempt(
                super(ServoUnidriveSPCaptureError, self).deceleration_time.set,
                acc, check, maxattempt=maxattempt) 
        

        if count == maxattempt + 1:
            print_fail(
                'set acceleration (or deceleration) time to ' + str(acc) +
                ' s / 1000 rpm aborted (number of attempt exceeds ' +
                str(maxattempt) + ')')
        elif count > 1 and (self.isprint_error or self.isprintall):
            print_warning(
                'set acceleration (or deceleration) time to '
                '{} s / 1000rpm at the {}th attempt.'.format(acc, count))
        elif self.isprintall:
            print('set acceleration (or deceleration) time to ' + str(acc) +
                  ' s / 1000 rpm')
        return count
   
    def control_rotation(self, time, rotation_rate, fact_multiplicatif_accel=1):
        if not ( isinstance(time, np.ndarray) and
                 isinstance(rotation_rate, np.ndarray) ):
            print("time and rotation_rate as to be of type numpy.ndarray ")
        time_instruct = 0.025  # typical time of exection of an instruction set
        maxattempt = int( max([ (time[1] - time[0]) / time_instruct, 1]))
        self.set_acceleration_time(int( (time[1] - time[0]) / 1000.0 *
                                        (rotation_rate[1] - rotation_rate[0]) /
                                        fact_multiplicatif_accel) )
        self.start_rotation(0)
        timer = Timer2(time)

        for t, ti in np.ndenumerate(time):
            t=t[0]
            count=self.set_target_rotation_rate(rotation_rate[t],
                                                 maxattempt = maxattempt)
            if ti < max(time):
                self.set_acceleration_time(int( (time[t+1] - time[t]) / 1000.0 *
                                                (rotation_rate[t+1] -
                                                 rotation_rate[t]) /
                                                fact_multiplicatif_accel),
                                           maxattempt = maxattempt - count )
                
                maxattempt= int(max([ (time[t+1] - time [t])/
                                       time_instruct, 1]))
            timer.wait_tick()

if __name__ == '__main__':

    def ftest(a, b, end=''):
        raise ValueError('pas content')

    attempt(ftest, 1, 'hello', end='')
