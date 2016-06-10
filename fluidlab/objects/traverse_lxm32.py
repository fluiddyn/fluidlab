
"""
192.168.28.11 - Variateur1
192.168.28.12 - Variateur2
192.168.28.13 - Variateur3
192.168.28.14 - Variateur4
192.168.28.19 - PC pilote Muriel

"""

from __future__ import division

import os
from time import time, sleep, ctime
from threading import Thread

import numpy as np

try:
    from u3 import U3
except ImportError:
    pass

from fluiddyn.util.timer import Timer
from fluiddyn.util import time_as_str

from fluidlab.objects.motors.lxm32_modbus import Motor

volt_no_movement = 2.5

path_dir = os.path.expanduser('~\.fluidlab')
if not os.path.exists(path_dir):   
    os.makedirs(path_dir)          


class TraverseError(ValueError):
    pass


class Traverse(object):
    def __init__(self, ip_modbus='192.168.28.12', const_position=1.062):
        self.motor = Motor(
            ip_modbus=ip_modbus, disable_limit_switches=False)
        self.movement_allowed = True
        self._const_position = const_position

        sleep(0.2)
        if self.motor.state == 'Fault (9)':
            self.motor.fault_reset()
            sleep(0.1)
            self.enable()
        if self.motor.state == 'Ready To Switch (4)':
            self.enable()
            sleep(0.1)

    def get_absolute_position(self):
        return self.motor.get_position_actual()/1.0273e6

    def get_relative_position(self):
        return self._const_position - self.get_absolute_position()

    def set_relative_position(self, pos):
        self._const_position = pos + self.get_absolute_position()

    _coef_meter_per_rot = 2.65e-4

    def close(self):
        self.motor.close()

    def stop_all(self):
        self.movement_allowed = False
        self.motor.stop_rotation()

    def enable(self):
        self.movement_allowed = 1
        self.motor.enable()

    def disable(self):
        self.movement_allowed = 0
        self.motor.disable()

    def get_state(self):
        return self.motor.get_state()

    def is_displacement_possible(self, displacement, position=None):
        upper_limit = 1.2
        lower_limit = 0.01

        if position is None:
            position = self.get_absolute_position()

        new_position = position - displacement

        if new_position > upper_limit or new_position < lower_limit:
            raise TraverseError(
                'Travelled distance too long (absolute position: {}).'.format(
                    new_position))

        return True

    def calibrate(self, delta_t, rpm):
        """Function to compute _coef_meter_per_rot.

        Parameters
        ----------

        delta_t : float
          Time of the translation (s).

        rpm : int
          Rotation speed of the motor (rotation per minute, can be negative).

        Notes
        -----

        The motor turns during delta_t at rpm. With the position
        sensor, this function can evaluate the translation speed of
        the carriage.

        Normally, _coef_meter_per_rot has to be constant whatever the
        value of rpm.  But for small rotation speed, it can be false.

        """
        self.motor.set_target_rotation_rate(rpm)
        sleep(2)
        l1 = self.get_absolute_position()
        sleep(delta_t)
        l2 = self.get_absolute_position()
        self.motor.set_target_rotation_rate(0)
        travelled_length = abs(l2-l1)
        speed = travelled_length/delta_t
        coef_meter_per_rot = speed/abs(rpm)
        print('rpm: {}\nspeed: {}\n_coef_meter_per_rot: {:.4e}'.format(
            abs(rpm), speed, coef_meter_per_rot))
        return coef_meter_per_rot

    def set_target_speed(self, speed):
        self.motor.set_target_rotation_rate(
            -speed / self._coef_meter_per_rot)

    def move(self, displacement, speed=0.05):
        """Move the carriage.

        Parameters
        ----------

        displacement : float
          Distance in meter.

        speed : float
          Velocity of displacement in m/s (positive)

        """
        self.is_displacement_possible(displacement)
        direction = -np.sign(displacement)
        time_theo = abs(displacement/speed)
        d0 = self.get_relative_position()
        self.motor.set_target_rotation_rate(
            direction * speed / self._coef_meter_per_rot)

        tstart = time()
        while time() - tstart < time_theo:
            sleep(0.02)
            if not self.movement_allowed:
                break
        self.motor.set_target_rotation_rate(0)
        d1 = self.get_relative_position()
        print('Travelled distance : {}\tError : {}'.format(
            abs(d1-d0), abs(abs(d1-d0)-abs(displacement))))

    def go_to(self, position_to_go, speed=0.05, relative=True):
        """
        move the platform from your position to the absolute position.

        Parameters
        ----------

        position_to_go : float
          Position in m.

        speed : float
          Translation velocity (m/s, positive).

        absolute : {True, bool}
          Absolute or relative position.

        """
        print('go_to({}, speed={}, relative={})'.format(
            position_to_go, speed, relative))
        if relative:
            get_pos = self.get_relative_position
        else:
            get_pos = self.get_absolute_position

        current_position = get_pos()
        displacement = position_to_go - current_position
        self.move(displacement, speed)
        if abs(get_pos()-position_to_go) > 0.005 and self.movement_allowed:
            self.go_to(position_to_go, relative=relative)

    def make_profiles(self, z_min, z_max, speed_down, speed_up=None,
                      period=None, nb_periods=None):

        if speed_up is None:
            speed_up = speed_down

        distance = z_max - z_min
        if distance < 0:
            raise ValueError('z_max < z_min')

        if period is None:
            period = distance * (speed_down + speed_up)
        elif distance * (speed_down + speed_up) + 2 > period:
            raise ValueError('distance * (speed_down + speed_up) > period.')

        self.go_to(z_max, speed_up)

        i_period = 0

        timer = Timer(period)
        while True:
            if not self.movement_allowed or \
               nb_periods is not None and i_period >= nb_periods:
                break
            print('go down')
            self.go_to(z_min, speed_down)
            print('go up')
            self.go_to(z_max, speed_up)
            i_period += 1
            if not self.movement_allowed:
                break
            timer.wait_tick()

    def record_positions(self, duration, dtime=0.2):

        path = os.path.join(path_dir, 'positions_traverse_{}.txt'.format(
            time_as_str()))

        with open(path, 'w') as f:
            timer = Timer(dtime)
            f.write(
                '# time start (since Epoch): {:.4f} s ({})\n'.format(
                    timer.tstart, ctime(timer.tstart)) +
                '# time, position\n')
            t_loop = 0.
            while t_loop < duration:
                pos = self.get_relative_position()
                t = time()
                f.write('{:.4f},{:.4f}\n'.format(t - timer.tstart, pos))
                t_loop = timer.wait_tick()

    def record_positions_async(self, duration, dtime=0.2):
        thread = Thread(
            target=self.record_positions, args=(duration, dtime))
        thread.start()
        return thread


class Traverses(object):
    def __init__(self, ip_addresses=None, const_positions=None):
        if ip_addresses is None:
            ip_addresses = ['192.168.28.11', '192.168.28.12']

        if const_positions is None:
            const_positions = [1.0205, 1.0352]

        self.ip_addresses = ip_addresses
        self.movement_allowed = True

        self.traverses = []
        for ind_traverse, ip in enumerate(ip_addresses):
            traverse = Traverse(ip_modbus=ip,
                                const_position=const_positions[ind_traverse])
            self.traverses.append(traverse)
            self.__dict__['traverse' + str(ind_traverse)] = traverse

        try:
            self.u3 = U3()
            self._use_u3 = True
            self.u3.writeRegister(5000, volt_no_movement)
        except NameError:
            self._use_u3 = False
            
    def close(self):
        for traverse in self.traverses:
            traverse.close()

    def stop_all(self):
        self.movement_allowed = False
        for traverse in self.traverses:
            traverse.stop_all()

    def enable(self):
        self.movement_allowed = True
        for traverse in self.traverses:
            traverse.enable()

    def disable(self):
        for traverse in self.traverses:
            traverse.disable()

    def get_relative_position(self):
        return self.traverse0.get_relative_position()

    def go_to(self, position_to_go, speed=0.05, relative=True):
        """
        Go to a position.

        Parameters
        ----------

        position_to_go : float
          Position in m.

        speed : float
          Translation velocity (m/s, positive).

        relative : {True, bool}
          Absolute or relative position.

        """
        if self._use_u3:
            if relative:
                displacement = position_to_go - self.get_relative_position()
                sign = np.sign(displacement)
            else:
                raise NotImplementedError

            if sign > 0:
                value = 5.
            else:
                value = 0.

            self.u3.writeRegister(5000, value)

        threads = []
        for traverse in self.traverses:
            thread = Thread(target=traverse.go_to,
                            args=(position_to_go,),
                            kwargs={'speed': speed, 'relative': relative})
            threads.append(thread)
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        self.u3.writeRegister(5000, volt_no_movement)

    def make_profiles(self, z_min, z_max, speed_down, speed_up=None,
                      period=None, nb_periods=None):
              
        if speed_up is None:
            speed_up = speed_down

        distance = z_max - z_min
        if distance < 0:
            raise ValueError('z_max < z_min')

        if period is None:
            period = distance * (speed_down + speed_up)
        elif distance * (speed_down + speed_up) + 2 > period:
            raise ValueError('distance * (speed_down + speed_up) > period.')

        self.go_to(z_max, speed_up)

        path = os.path.join(path_dir, 'make_profiles_{}.txt'.format(
            time_as_str()))                                            

        with open(path, 'w') as f:                                     
            f.write('make_profiles(z_min={}, z_max={}, speed_down={},\n'.format(
                        z_min, z_max, speed_down) +
                    '              speed_up={},\n'.format(speed_up) +
                    '              period={}, nb_periods={})\n'.format(
                        period, nb_periods))

        i_period = 0
        timer = Timer(period)

        while True:
            if not self.movement_allowed or \
               nb_periods is not None and i_period >= nb_periods:
                break
            print('go down')
            self.go_to(z_min, speed_down)
            print('go up')
            self.go_to(z_max, speed_up)
            i_period += 1
            if not self.movement_allowed or \
               nb_periods is not None and i_period >= nb_periods:
                break
            timer.wait_tick()

    def record_positions(self, duration, dtime=0.2):

        path = os.path.join(path_dir, 'positions_traverses_{}.txt'.format(
            time_as_str()))

        nb_traverses = len(self.traverses)

        positions = np.empty([nb_traverses])
        times = np.empty_like(positions)

        with open(path, 'w') as f:
            timer = Timer(dtime)
            f.write(
                '# time start (since Epoch): {:.4f} s ({})\n'.format(
                    timer.tstart, ctime(timer.tstart)) +
                '# {} traverse(s)\n'.format(nb_traverses) +
                '# time, position\n')
            t_loop = 0.
            while t_loop < duration:
                for it, traverse in enumerate(self.traverses):
                    positions[it] = traverse.get_relative_position()
                    times[it] = time()

                times -= timer.tstart

                s = ''
                for it, t in enumerate(times):
                    if s != '':
                        s += ','
                    pos = positions[it]
                    s += '{:.4f},{:.4f}'.format(t, pos)
                f.write(s + '\n'.format(t, pos))
                t_loop = timer.wait_tick()

    def record_positions_async(self, duration, dtime=0.2):
        thread = Thread(
            target=self.record_positions, args=(duration, dtime))
        thread.start()
        return thread


if __name__ == '__main__':

    traverses = Traverses()
    traverse0 = traverses.traverse0
    traverse1 = traverses.traverse1

    # traverses.make_profiles(0.1, 0.5, 0.05, period=40, nb_periods=2)
