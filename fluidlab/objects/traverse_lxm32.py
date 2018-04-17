
"""
192.168.28.11 - Variateur1
192.168.28.12 - Variateur2
192.168.28.13 - Variateur3
192.168.28.14 - Variateur4
192.168.28.19 - PC pilote Muriel

"""

from __future__ import division, print_function

from fluidlab.util.calcul_track import (
    make_track_sleep_1period_tbottom, concatenate
)
from fluiddyn.io import query

import os
import sys
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
from fluidlab.util.util import make_ip_as_str

volt_no_movement = 2.5

path_dir = os.path.expanduser("~\.fluidlab")
if not os.path.exists(path_dir):
    os.makedirs(path_dir)


class TraverseError(ValueError):
    pass


def define_track_profilometer(
    z_max, z_min, v_up, v_down, acc, dacc, dt, t_exp, t_bottom, t_period=None
):

    times1, positions1, speeds1, t_total = make_track_sleep_1period_tbottom(
        z_max, z_min, v_up, v_down, acc, dacc, dt, t_bottom, t_period
    )
    nb_periods = int(round(t_exp / t_total, 0))
    times, speeds, positions = concatenate(
        times1, speeds1, positions1, nb_periods
    )

    return times, speeds, positions


class Traverse(object):

    def __init__(self, ip_modbus=None, const_position=1.062, offset_abs=None):
        self.motor = Motor(ip_modbus=ip_modbus, disable_limit_switches=False)
        self.movement_allowed = True
        self._const_position = const_position
        self.ip_modbus = ip_modbus
        sleep(0.2)
        if self.motor.state == "Fault (9)":
            self.motor.fault_reset()
            sleep(0.1)
            self.enable()
        if self.motor.state == "Ready To Switch (4)":
            self.enable()
            sleep(0.1)

        self._offset_abs = offset_abs
        self.u3 = U3()
        self._use_u3 = False
        self.u3.writeRegister(5000, volt_no_movement)

        # Load calibration*
        try:
            self._coef_meter_per_rot = self._load_calibration()
        except IOError:
            self._coef_meter_per_rot = 1e6
            print(
                "Calibration file doesn't exist. Use function self.calibrate()."
            )

    def get_absolute_position(self):
        # coeff1 = 1.0273e6
        # Value chosen by hand
        coeff1 = 1e6  # Variateur 1, 2 et 3
        # coeff2 = 8e5
        if self._offset_abs:
            abs_pos = self.motor.get_position_actual() / coeff1 - self._offset_abs
        else:
            abs_pos = self.motor.get_position_actual() / coeff1
        return abs_pos

    def get_relative_position(self):
        return self._const_position - self.get_absolute_position()

    def set_relative_position(self, pos):
        self._const_position = pos + self.get_absolute_position()

    # _coef_meter_per_rot = 2.65e-4
    # _coef_meter_per_rot = 9.7303e-7
    # _coef_meter_per_rot = 9.729128113524125e-7
    # _coef_meter_per_rot = 9.994783e-7

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
                "Travelled distance too long (absolute position: {}).".format(
                    new_position
                )
            )

        return True

    def calibrate(self, delta_t, rpm, save=False):
        """Function to compute _coef_meter_per_rot.

        Parameters
        ----------

        delta_t : float
          Time of the translation (s).

        rpm : int
          Rotation speed of the motor (rotation per minute, can be negative).

        save : bool
        Save calibration file

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
        travelled_length = abs(l2 - l1)
        speed = travelled_length / delta_t
        coef_meter_per_rot = speed / abs(rpm)
        print(
            "rpm: {}\nspeed: {}\n_coef_meter_per_rot: {:.4e}".format(
                abs(rpm), speed, coef_meter_per_rot
            )
        )

        # Save calibration file
        if save:
            path = os.path.join(
                path_dir, make_ip_as_str(self.ip_modbus) + "calibration.txt"
            )

            with open(path, "w") as f:
                f.write("coef_meter_per_rot = {}".format(coef_meter_per_rot))

        # Use the calibration coefficient
        self._coef_meter_per_rot = coef_meter_per_rot

        return coef_meter_per_rot

    def _load_calibration(self):
        """ Loads the calibration of the traverse.

        Returns
        -------
        _coef_meter_per_rot : float
        Value of the calibration
        
        """
        path = os.path.join(
            path_dir, make_ip_as_str(self.ip_modbus) + "calibration.txt"
        )
        with open(path, "r") as f:
            coef_meter_per_rot = float(f.readlines()[0].split("=")[1])

        return coef_meter_per_rot

    def set_target_speed(self, speed):
        self.motor.set_target_rotation_rate(-speed / self._coef_meter_per_rot)

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
        time_theo = abs(displacement / speed)
        d0 = self.get_relative_position()
        self.motor.set_target_rotation_rate(
            direction * speed / self._coef_meter_per_rot
        )

        tstart = time()
        while time() - tstart < time_theo:
            sleep(0.02)
            if not self.movement_allowed:
                break

        self.motor.set_target_rotation_rate(0)
        d1 = self.get_relative_position()
        print(
            "Travelled distance : {}\tError : {}".format(
                abs(d1 - d0), abs(abs(d1 - d0) - abs(displacement))
            )
        )

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
        print(
            "go_to({}, speed={}, relative={})".format(
                position_to_go, speed, relative
            )
        )
        if relative:
            get_pos = self.get_relative_position
        else:
            get_pos = self.get_absolute_position

        current_position = get_pos()
        displacement = position_to_go - current_position
        self.move(displacement, speed)
        new_pos = get_pos()
        error_pos = abs(new_pos - position_to_go)
        if (
            error_pos > 0.005
            and abs(new_pos - current_position) > 0.5 * abs(displacement)
            and self.movement_allowed
        ):
            self.go_to(position_to_go, relative=relative)

    def make_profiles(
        self,
        z_min,
        z_max,
        speed_down,
        speed_up=None,
        period=None,
        nb_periods=None,
    ):

        if speed_up is None:
            speed_up = speed_down

        distance = z_max - z_min
        if distance < 0:
            raise ValueError("z_max < z_min")

        if period is None:
            period = distance * (speed_down + speed_up)
        elif distance * (speed_down + speed_up) + 2 > period:
            raise ValueError("distance * (speed_down + speed_up) > period.")

        self.go_to(z_max, speed_up)

        i_period = 0

        timer = Timer(period)
        while True:
            if (
                not self.movement_allowed
                or nb_periods is not None
                and i_period >= nb_periods
            ):
                break

            print("profile number {}".format(i_period))
            print("go down")
            self.go_to(z_min, speed_down)
            print("go up")
            self.go_to(z_max, speed_up)
            i_period += 1
            if not self.movement_allowed:
                break

            timer.wait_tick()

    def record_positions(self, duration, dtime=0.2):

        path = os.path.join(
            path_dir, "positions_traverse_{}.txt".format(time_as_str())
        )

        with open(path, "w") as f:
            timer = Timer(dtime)
            f.write(
                "# time start (since Epoch): {:.4f} s ({})\n".format(
                    timer.tstart, ctime(timer.tstart)
                )
                + "# time, position\n"
            )
            t_loop = 0.
            while t_loop < duration:
                pos = self.get_relative_position()
                t = time()
                f.write("{:.4f},{:.4f}\n".format(t - timer.tstart, pos))
                f.flush()
                t_loop = timer.wait_tick()

    def record_positions_async(self, duration, dtime=0.2):
        thread = Thread(target=self.record_positions, args=(duration, dtime))
        thread.start()
        return thread

    def make_profiles_from_track(self, times, speeds, positions, save=False):

        speeds = abs(speeds)
        speeds[speeds == 0] = speeds[1]

        # Go to starting position
        it = 0
        pos_start = positions[0]
        print("****** Go to starting position ******")
        traverse.go_to(pos_start, speed=0.05, relative=True)
        if save:
            pat_to_save = os.path.join(path_dir, "profilometers_motion.txt")
            f = open(path_to_save, "w")
            f.write(
                "it = {} ; t = {} ; z = {} ; v = {} ; ".format(
                    it, times[0], positions[0], speeds[0]
                )
            )

        # Follow track and track register
        for it, t in enumerate(times[1:-1]):
            it += 1
            print("it = ", it)
            pos_to_go = float(positions[it])
            speed = float(speeds[it])
            traverse.go_to(pos_to_go, speed, relative=True)

            if save:
                f.write(
                    "it = {} ; t = {} ; z = {} ; v = {} ; ".format(
                        it, times[it], positions[it], speeds[it]
                    )
                )

        if save:
            f.close()

    def follow_track(
        self,
        times,
        speeds,
        positions,
        fact_multiplicatif_accel=1,
        coeff_smooth=2.,
        periodic=True,
        use_u3=False,
    ):

        if use_u3:
            self.u3.writeRegister(5000, volt_no_movement)

        dt = timestep = times[1] - times[0]

        self.times = times
        self.speeds = speeds
        self.positions = positions

        rotation_rates = self.rotation_rates = self.speeds / self._coef_meter_per_rot

        # to decrease discretization error
        speeds[:-1] = (speeds[:-1] + speeds[1:]) / 2

        eps = 0.001  # an error of eps m in position is accepted
        error_v = 0.0001
        x_measured = []
        v_sent = []
        t_sent = []
        acc = abs((rotation_rates[1] - rotation_rates[0])) / timestep or 600
        self.motor.set_acceleration(acc * fact_multiplicatif_accel)

        t_start = time()
        path_out = os.path.join(
            path_dir, time_as_str() + "_track_profiler_" + self.ip_modbus + ".txt"
        )
        f = open(path_out, "w")
        f.write(
            "# track_profiler "
            + self.ip_modbus
            + "\n# time since epock: {}".format(t_start)
            + "\n# time(s), position (m)\n"
        )
        f.flush()
        timer = Timer(dt)
        v = speeds[0]
        t = time() - t_start
        x = self.get_relative_position()
        x_measured.append(x)
        v_sent.append(v)
        t_sent.append(time() - t_start)
        self.set_target_speed(v)
        f.write("{:.4f},{:.4f}\n".format(t, x))
        f.flush()

        timer.wait_tick()

        for it, t in enumerate(times[1:-1]):
            it += 1
            v_theo = speeds[it]
            t = time() - t_start
            x = self.get_relative_position()

            if not self.movement_allowed:
                print("not self.movement_allowed")
                self.motor.set_target_rotation_rate(0)
                self.motor.run_quick_stop()
                raise TraverseError("not self.movement_allowed.")

            error = abs(positions[it] - x)

            if error > 0.02:
                print(
                    "Large error position carriage! error = "
                    "{}:\n".format(error) + "STOP traverse " + self.ip_modbus
                )
                self.set_target_speed(0)
                self.motor.run_quick_stop()
                return

            v_should_go = (positions[it + 1] - x) / timestep

            if use_u3:
                if abs(v_theo) <= error_v:
                    value = volt_no_movement
                elif v_theo < -error_v:
                    value = 5.
                else:
                    value = 0.
                self.u3.writeRegister(5000, value)

            if error >= eps:
                v_target = (coeff_smooth * v_theo + v_should_go) / (
                    coeff_smooth + 1
                )
            else:
                v_target = v_theo

            if error > 5 * eps:
                print(
                    (
                        "Warning ({}): error = {:4.3f} m, " "v_target:{:4.3f} m/s"
                    ).format(
                        self.ip_modbus, error, v_target
                    )
                )
                sys.stdout.flush()

            acc = (
                abs(rotation_rates[it + 1] - rotation_rates[it - 1])
                / (2 * timestep)
                or 600
            )

            self.motor.set_acceleration(acc * fact_multiplicatif_accel)

            t_sent.append(time() - t_start)
            self.set_target_speed(v_target)

            x_measured.append(x)
            v_sent.append(v_target)

            f.write("{:.4f},{:.4f}\n".format(t, x))
            f.flush()

            if self.motor.state != "Operation Enabled (6)":
                print("Error: motor not enable, " + self.ip_modbus)
                self.set_target_speed(0)
                self.motor.run_quick_stop()
                return

            if it % 10 == 0:
                print(
                    "traverse "
                    + self.ip_modbus
                    + ", it = {}, t = {:.4f} s".format(it, t)
                )
                sys.stdout.flush()

            timer.wait_tick()

        t = time() - t_start
        x = self.get_relative_position()

        if periodic:
            pos_end = positions[0]
        else:
            pos_end = positions[-1]

        v = (pos_end - x) / timestep
        x_measured.append(x)
        v_sent.append(v)
        t_sent.append(time() - t_start)
        self.set_target_speed(v)

        f.write("{:.4f},{:.4f}\n".format(t, x))
        f.flush()
        f.close()
        timer.wait_tick()
        self.motor.set_acceleration(1000)
        self.motor.set_target_rotation_rate(0)

        if use_u3:
            self.u3.writeRegister(5000, volt_no_movement)

        self.x_measured = np.array(x_measured)
        self.v_sent = np.array(v_sent)
        self.t_sent = np.array(t_sent)

        return self.x_measured


class Traverses(object):

    def __init__(self, ip_addresses=None, const_positions=None, offset_abs=None):
        if ip_addresses is None:
            ip_addresses = ["192.168.28.11", "192.168.28.12", "192.168.28.13"]

        if const_positions is None:
            const_positions = [1.046875] * 3

        if offset_abs is None:
            offset_abs = [0.] * 3

        self.ip_addresses = ip_addresses
        self.movement_allowed = True

        self.traverses = []
        for ind_traverse, ip in enumerate(ip_addresses):
            traverse = Traverse(
                ip_modbus=ip,
                const_position=const_positions[ind_traverse],
                offset_abs=offset_abs[ind_traverse],
            )
            self.traverses.append(traverse)
            self.__dict__["traverse" + str(ind_traverse)] = traverse

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
            thread = Thread(
                target=traverse.go_to,
                args=(position_to_go,),
                kwargs={"speed": speed, "relative": relative},
            )
            threads.append(thread)
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        self.u3.writeRegister(5000, volt_no_movement)

    def make_profiles(
        self,
        z_min,
        z_max,
        speed_down,
        speed_up=None,
        period=None,
        nb_periods=None,
    ):

        if speed_up is None:
            speed_up = speed_down

        distance = z_max - z_min
        if distance < 0:
            raise ValueError("z_max < z_min")

        if period is None:
            period = distance * (speed_down + speed_up)
        elif distance * (speed_down + speed_up) + 2 > period:
            raise ValueError("distance * (speed_down + speed_up) > period.")

        self.go_to(z_max, speed_up)

        path = os.path.join(
            path_dir, "make_profiles_{}.txt".format(time_as_str())
        )

        with open(path, "w") as f:
            f.write(
                time_as_str(2) + "\nmake_profiles(z_min="
                "{}, z_max={}, speed_down={},\n".format(z_min, z_max, speed_down)
                + "              speed_up={},\n".format(speed_up)
                + "              period={}, nb_periods={})\n".format(
                    period, nb_periods
                )
            )

        i_period = 0
        timer = Timer(period)

        while True:
            if (
                not self.movement_allowed
                or nb_periods is not None
                and i_period >= nb_periods
            ):
                break

            print("profile number {}".format(i_period))
            print("go down")
            self.go_to(z_min, speed_down)
            print("go up")
            self.go_to(z_max, speed_up)
            i_period += 1
            if (
                not self.movement_allowed
                or nb_periods is not None
                and i_period >= nb_periods
            ):
                break

            timer.wait_tick()

    def make_profiles_from_track(self, times, speeds, positions, save=False):

        speeds = abs(speeds)
        speeds[speeds == 0] = speeds[1]

        # Go to starting position
        it = 0
        pos_start = positions[0]
        print("****** Go to starting position ******")
        self.go_to(pos_start, speed=0.05, relative=True)
        if save:
            pat_to_save = os.path.join(path_dir, "profilometers_motion.txt")
            f = open(path_to_save, "w")
            f.write(
                "it = {} ; t = {} ; z = {} ; v = {} ; ".format(
                    it, times[0], positions[0], speeds[0]
                )
            )

        # Follow track and track register
        for it, t in enumerate(times[1:-1]):
            it += 1
            print("it = ", it)
            pos_to_go = float(positions[it])
            speed = float(speeds[it])
            self.go_to(pos_to_go, speed, relative=True)

            if save:
                f.write(
                    "it = {} ; t = {} ; z = {} ; v = {} ; ".format(
                        it, times[it], positions[it], speeds[it]
                    )
                )

        if save:
            f.close()

    def record_positions(self, duration, dtime=0.2):

        path = os.path.join(
            path_dir, "positions_traverses_{}.txt".format(time_as_str())
        )

        nb_traverses = len(self.traverses)

        positions = np.empty([nb_traverses])
        times = np.empty_like(positions)

        with open(path, "w") as f:
            timer = Timer(dtime)
            f.write(
                "# time start (since Epoch): {:.4f} s ({})\n".format(
                    timer.tstart, ctime(timer.tstart)
                )
                + "# {} traverse(s)\n".format(nb_traverses)
                + "# time, position\n"
            )
            t_loop = 0.
            while t_loop < duration:
                for it, traverse in enumerate(self.traverses):
                    positions[it] = traverse.get_relative_position()
                    times[it] = time()

                times -= timer.tstart

                s = ""
                for it, t in enumerate(times):
                    if s != "":
                        s += ","
                    pos = positions[it]
                    s += "{:.4f},{:.4f}".format(t, pos)
                f.write(s + "\n".format(t, pos))
                t_loop = timer.wait_tick()

    def record_positions_async(self, duration, dtime=0.2):
        thread = create_thread_record_positions(duration, dtime)
        thread.start()
        return thread

    def create_thread_record_positions(self, duration, dtime=0.2):
        thread = Thread(target=self.record_positions, args=(duration, dtime))
        return thread

    def run_profiles(
        self, times, speeds, positions, relative=True, thread_record=None
    ):

        eps = 0.001
        for traverse in self.traverses:
            pos = traverse.get_relative_position()
            if abs(pos - positions[0]) > eps:
                print("First run traverses.go_to({}, 0.01)".format(positions[0]))
                return

        threads = []

        if thread_record is not None:
            threads.append(thread_record)

        # The master driver is also driven the 0/5 volts output signal
        thread = Thread(
            target=self.traverses[0].follow_track,
            args=(times, speeds, positions),
            kwargs={"use_u3": True},
        )
        threads.append(thread)

        for traverse in self.traverses[1:]:
            thread = Thread(
                target=traverse.follow_track, args=(times, speeds, positions)
            )
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print("threads = ", threads)


if __name__ == "__main__":
    ip_addresses = ["192.168.28.11"]
    traverses = Traverses(ip_addresses=ip_addresses)
    # traverses = Traverses()
    # traverse0 = traverses.traverse0
    # traverse1 = traverses.traverse1
    # traverse = Traverse(ip_modbus='192.168.28.13')

    # Parameters
    z_max = 0.77
    z_min = 0.02

    coef = 2

    v_up = 0.1 / coef
    v_down = 0.07 / coef

    accel = 0.05 / coef
    dacc = 0.05 / coef

    dt = 0.25 * coef
    t_exp = 200.
    t_bottom = 5. * coef
    t_period = 60. * coef

    profile = True
    if profile:

        times, speeds, positions = define_track_profilometer(
            z_max, z_min, v_up, v_down, accel, dacc, dt, t_exp, t_bottom, t_period
        )

        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.gca()
        ax.set_title("Position Vs Time")
        ax.set_xlabel("time (s)")
        ax.set_ylabel("z (m)")
        ax.plot(times, positions, "x")
        plt.show(block=True)

        answer = query.query("\n Is the expected track? [y/n] ")

        if answer.startswith("n"):
            print("track cancelled")
            pass

        else:
            print("running track")
            traverses.run_profiles(times, speeds, positions)
