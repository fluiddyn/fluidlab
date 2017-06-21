"""Unidrive SP motor (Leroy Somer)
==================================

How to setup and control the motor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pad, parameters and menus**

The power drive has to be setup using its pad. There are arrow keys
and two important buttons (a red button for reset, validate and stop
the motor and a green one to start it). Using the arrow key, you can
access many parameters organized in 23 menus.

Menu 0 gathers important parameters from other menus. For a simple
usage, it's the only one that matters.

**Terminals**

The power drive cannot be controlled only with the pad and terminals
("bornes" in french) have to be linked. In particular, we have to use:

- Terminal 22 gives 24 V.

- Terminal 31 has to be plugged to 24 V to give a "drive
  enable signal".

- Terminal 26 has to be plugged to 24 V to give a "run signal".

**Indications written on the drive**

- "inh" stands for inhibited, it means the motor is locked.

- "rdY" stands for ready.

- "trip" means there is a problem, check section K of the manual for
  solutions.

**Control the motor with a computer**

The value of the parameter 0.05 controls how the motor is driven.

- 0.05 -> PAd : controlled by the pad on the power drive.

- 0.05 -> Pr : controlled by other parameters (that can be set by the
  computer). In particular the rotating rate of the motor in
  proportional to the value of parameter 0.24. The "run signal" can be
  given with the parameter 6.34.

**Modes**

The power drive can drive the motor in three modes,

- Open loop,

- close loop,

- servo.

The parameter 0.48 correspond to the modes. In order to change the
mode, one need to change the parameter 0.48, to change the parameter
0.00 and to reset the drive by pressing the red "reset" button. Then
the user has to manually launch an auto-calibration process.
Therefore, it is not possible to change mode only from the
computer. Since some parameters have different meanings in the
different modes, we provide one class for each mode.

The setup procedures for the different modes are described in the
docstring of the classes.

.. autoclass:: BaseUnidriveSP
   :members:
   :private-members:

.. autoclass:: OpenLoopUnidriveSP
   :members:
   :private-members:

.. autoclass:: ServoUnidriveSP
   :members:
   :private-members:

.. autoclass:: ServoUnidriveSPCaptureError
   :members:
   :private-members:


**Note on how to read the commercial designation**

At LEGI, we have a motor "055U2C300BAMRA063110". This name can be
decomposed as 055-U-2-C-30-0-B-A-MR-A-063-110. The different parts of
the name mean:

- 055: frame size
- U: voltage (400 V)
- 2: torque selection (std)
- C: stator length
- 30: winding speed (3000 rpm)
- 0: brake (no brake)
- B: connection type
- A: output shaft (std)
- MR: Feedback device (Incremental encoder 2048 ppr)
- A: inertial (std)
- 063: PCD (std)
- 110: Shaft diameter.

**Connection**

RS485 (2 wires, half-duplex, differential) plugged to an RJ45: cable 2
RJ45 is the + (or B) of the RS485 and cable 7 of the RJ45 is the - (or
A) of the RS485.

"""

from time import sleep
from fluiddyn.util.timer import TimerIrregular
import warnings
import numpy as np


from fluidlab.instruments.modbus.driver import ModbusDriver
from fluidlab.instruments.modbus.features import (
    DecimalInt16Value, Int16StringValue)
from fluiddyn.util.terminal_colors import print_fail, print_warning


class ModeError(Exception):
    """Some values are only useable in one mode (open_loop, closed_loop, servo)
    When a value is used, a function checks the current mode, and raises
    a ModeError if it doesn't match.
    """


class BaseUnidriveSP(ModbusDriver):
    """Base class for the driver for the motor driver Unidrive SP

    Parameters
    ----------

    port : {None, str}
      The port where the motor is plugged.

    timeout : {1, number}
      Timeout for the communication with the motor (in s).

    module : {'minimalmodbus', str}
      Module used to communicate with the motor.

    Notes
    -----

    This class can be used to write other classes for drivers of the
    Unidrive SP.

    """
    _constant_nb_pairs_poles = 4

    def __init__(self, port=None, timeout=1,
                 module='minimalmodbus', signed=False):

        self.signed = signed

        if port is None:
            from fluidlab.util import userconfig
            try:
                port = userconfig.port_unidrive_sp
            except AttributeError:
                raise ValueError(
                    'If port is None, "port_unidrive_sp" has to be defined in'
                    ' one of the FluidLab user configuration files.')

        super(BaseUnidriveSP, self).__init__(port=port, method='rtu',
                                             timeout=timeout, module=module)

        mode = self.mode.get()
        if hasattr(self, '_mode') and self._mode_cls != mode:
            raise ModeError(
                'Instantiating a class for mode '
                '{} but driver is in mode {}.'.format(self._mode_cls, mode))

    def unlock(self):
        """Unlock the motor (then rotation is possible)."""
        self._unlocked.set(1)

    def lock(self):
        """Lock the motor (then rotation is not possible)."""
        self._unlocked.set(0)

    def start_rotation(self, speed=None, direction=None):
        """Start the motor rotation.

        Parameters
        ----------

        speed : {None, number}
          Rotation rate in Hz. If speed is None, start the rotation
          with the speed that the motor has in memory.

        direction : {None, number}
          Direction (positive or negative).

        """
        self._reference_selection.set("preset")

        if not self._unlocked.get():
            self._unlocked.set(1)

        if speed is not None:
            self.set_target_rotation_rate(speed)

        self._rotate.set(1)

    def stop_rotation(self):
        """Stop the rotation."""
        self._reference_selection.set('preset')
        self._rotate.set(0)

    def set_target_rotation_rate(self, rotation_rate, check=False):
        """Set the target rotation rate in Hz."""
        raise NotImplementedError()

    def get_target_rotation_rate(self):
        """Get the target rotation rate in Hz."""
        raise NotImplementedError()


def _compute_from_param_str(parameter_str):
    l = parameter_str.split('.')
    menu = int(l[0])
    parameter = int(l[1])
    address = 100 * menu + parameter - 1
    return menu, parameter, address


class Value(DecimalInt16Value):
    def __init__(self, name, doc='', parameter_str='', number_of_decimals=0):
        self._menu, self._parameter, address = \
            _compute_from_param_str(parameter_str)
        super(Value, self).__init__(
            name, doc, address, number_of_decimals=number_of_decimals)


class StringValue(Int16StringValue):
    def __init__(self, name, doc='', int_dict=None, parameter_str=''):
        self._menu, self._parameter, address = \
            _compute_from_param_str(parameter_str)
        super(StringValue, self).__init__(name, doc, int_dict, address)

    def set(self, value, check=True):
        """Set the Value to value.
        If check equals 1, checks that the value was properly set.
        To disable this function, enter check = 0
        """
        super(StringValue, self).set(value)
        if check:
            self._check_value(value)

    def _check_value(self, value):
        """After a value is set, checks the instrument value and
        sends a warning if it doesn't match."""
        instr_value = self.get()
        if instr_value != value:
            msg = (
                'Value {} could not be set to {} and was set to {} instead'
            ).format(self._name, value, instr_value)
            warnings.warn(msg, UserWarning)


int_dict_mode = {1: 'open_loop', 2: 'closed_loop', 3: 'servo', 4: 'regen'}

int_dict_ref ={0: 'A1.A2', 1: 'A1.pr', 2: 'A2.pr', 3: 'preset',
               4: 'pad', 5: 'Prc'}


BaseUnidriveSP._build_class_with_features([
    StringValue(name='mode',
                doc='The operating mode.',
                int_dict=int_dict_mode,
                parameter_str='0.48'),
    StringValue(name='_reference_selection',
                doc=('Defines how the rotation speed is given to the motor.'
                     '\n\n- "preset" is what we want here,\n'
                     '- "pad" means it can be entered with the arrow keys '
                     'of the motor pad'),
                int_dict=int_dict_ref,
                parameter_str='0.05'),
    Value(name='_unlocked',
          doc=('When this variable is equal to 0, '
               'the motor is inhibited and displays "inh". '
               'When it is equal to 1, the motor is ready to run '
               'and displays "rdY".'),
          parameter_str='6.15'),
    Value(name='_rotate',
          doc='Set this to 1 to give an order of rotation',
          parameter_str='6.34'),
    Value(name='acceleration_time',
          doc='The time to go from 0 Hz to 100 Hz (s).',
          parameter_str='0.03',
          number_of_decimals=1),
    Value(name='deceleration_time',
          doc='The time to go from 100 Hz to 0 Hz (s).',
          parameter_str='0.04',
          number_of_decimals=1),
    Value(name='_number_of_pairs_of_poles',
          doc='The number of pairs of poles of the motor.',
          parameter_str='0.42'),
    Value(name='_rated_voltage',
          doc='The Rated voltage of the motor (V).',
          parameter_str='0.44'),
    Value(name='_rated_current_open_loop',
          doc='Rated current of the motor. Used in open loop.',
          parameter_str='0.46',
          number_of_decimals=2)])


class OpenLoopUnidriveSP(BaseUnidriveSP):
    """Driver for the motor driver Unidrive SP setup in open loop mode.

    Parameters
    ----------

    port : {None, str}
      The port where the motor is plugged.

    timeout : {1, number}
      Timeout for the communication with the motor (in s).

    module : {'minimalmodbus', str}
      Module used to communicate with the motor.

    Notes
    -----

    **Setup of the power drive in "open loop" mode**

    See short guide (section 7.2) and long guide (chapter H1). Follow
    the instructions.

    *Example for LEGI*

    Reset in open loop mode:

    - 0.00 -> 1253,

    - 0.48 -> OPEn.LP + reset.

    For this to work, the parameter 0.48 has to be changed. If it is
    already in open loop, you have to first to reset the motor in
    another mode and then reset it in open loop.

    In case of error br.th, 0.51 -> 8 + reset.

    Main parameters:

    - 0.02 -> 200 (Hz, 50 * 4 pairs of poles),

    - 0.03 -> 5 (s, time of acceleration 0 to 100 Hz),

    - 0.04 -> 10 (s, time of deceleration 100 to 0 Hz),

    - 0.21 -> th.

    Motor parameters (read on the motor):

    - 0.44 -> 400 (V),

    - 0.45 -> 3000 (rpm, max (?) rotation rate),

    - 0.46 -> 1 (A, current),

    - 0.47 -> 200 (Hz, 3000/60 (Hz) * 4 pairs of poles).

    Warning: the parameters 0.45 (motor rated speed, min-1) and 0.47
    (rated frequency, Hz) must be proportional: Rated frequency =
    motor rated speed / 60 * number of pairs of poles.

    Autocalibration

    - 0.40 -> 2 (for rotating calibration, 1 for stationary calibration),

    - Plug the terminals to send "drive enable signal" (link terminals
      22 and 31) and "run signal" (link terminals 22 and 26),

    - Remove the terminals,

    - 0.00 - > 1000 (memorization of the parameters),

    - Send "drive enable signal" (link terminals 22 and 31).

    Other useful parameters:

    - 6.15 -> 1 (unlock) or 0 (lock),

    - 6.34 -> 1 (order of rotation) or 0 (no rotation).

    """
    _constant_nb_pairs_poles = 4

    _mode_cls = 'open_loop'

    def set_target_rotation_rate(self, rotation_rate, check=False):
        """Set the target rotation rate in Hz."""
        # The value `_speed` is actually equal to _constant_nb_pairs_poles
        # times the rotation rate in Hz.

        if not isinstance(rotation_rate, (int, float)):
            rotation_rate = float(rotation_rate)

        self._speed.set(self._constant_nb_pairs_poles * rotation_rate,
                        check=check)

    def get_target_rotation_rate(self):
        """Get the target rotation rate in Hz."""
        # The value `_speed` is actually equal to _constant_nb_pairs_poles
        # times the rotation rate in Hz.
        raw_speeed = self._speed.get()
        return raw_speeed / self._constant_nb_pairs_poles


OpenLoopUnidriveSP._build_class_with_features([
    Value(name='_speed',
          doc=('Frequency of the driving signal (Hz).\n\n'
               'Warning: the actual rotation rate in Hz '
               'is equal to this value divided by the number of poles.'),
          parameter_str='0.24',
          number_of_decimals=1),
    Value(name='_min_frequency',
          doc='Minimum limit of frequency (Hz).',
          parameter_str='0.01',
          number_of_decimals=1),
    Value(name='_rated_speed',
          doc='Rated speed of the motor (rpm).',
          parameter_str='0.45'),
    Value(name='_rated_frequency',
          doc=('Rated frequency of the driving signal of the motor (Hz).\n\n'
               'It has to be equal to '
               '[rated speed / 60 * number of pairs of poles].'),
          parameter_str='0.47',
          number_of_decimals=1)])


class ServoUnidriveSP(BaseUnidriveSP):
    """Driver for the motor driver Unidrive SP setup in "servo" mode.

    Warning: NotImplemented the content of the class has to be adapted
    to the mode.

    Parameters
    ----------

    port : {None, str}
      The port where the motor is plugged.

    timeout : {1, number}
      Timeout for the communication with the motor (in s).

    module : {'minimalmodbus', str}
      Module used to communicate with the motor.

    Notes
    -----

    **Setup of the power drive in "servo" mode**

    See short guide (section 7.2) and long guide (chapter H1). Follow
    the instructions.

    *Example for LEGI*

    Drive enable signal and run signal are not given

    Reset in open loop mode:

    - 0.00 -> 1253,

    - 0.48 -> ServO + reset.

    In case of error br.th, 0.51 -> 8 + reset.

    Motor parameters (read on the motor and on 4146 documentation):
    - 0.02 -> 3000 (rpm, maximum velocity),,

    - 0.21 -> th.

    - 0.41 -> 12 (kHz, switching frequency)

    - 0.42 -> 8 (number of poles)

    - 0.45 -> 42 (s, thermal time constant),

    - 0.46 -> 1 (A, stalling current),

    Coder parameters:

    - 0.49 -> L2

    - 3.34 -> 2048 (ppr)

    - 3.36 -> 5 (V)

    - 3.38 -> Ab.SErvo

    Autocalibration

    - 0.40 -> 2 (for rotating calibration, 1 for stationary calibration),

    - Plug the terminals to send "drive enable signal" (link terminals
      22 and 31) and "run signal" (link terminals 22 and 26),

    - Unplug the terminals when calibration is over,

    - connect the motor to the load

    - 0.40 -> 3

    - Plug the terminals to send "drive enable signal" (link terminals
      22 and 31) and "run signal" (link terminals 22 and 26)

    - Unplug the terminals when calibration is over,

    - 0.00 - > 1000 (memorization of the parameters),

    - Send "drive enable signal" (link terminals 22 and 31).

    Other useful parameters:

    - 6.15 -> 1 (unlock) or 0 (lock),

    - 6.34 -> 1 (order of rotation) or 0 (no rotation).

    """
    _constant_nb_pairs_poles = 4

    _mode_cls = 'servo'

    def set_target_rotation_rate(self, rotation_rate, check=False, signed=False):
        """Set the target rotation rate in rpm."""
        self._speed.set(rotation_rate, check=check, signed=signed)

    def get_target_rotation_rate(self):
        """Get the target rotation rate in rpm."""
        return self._speed.get()


ServoUnidriveSP._build_class_with_features([
    Value(name='_speed',
          doc=('Rotation rate of the motor (rpm).'),
          parameter_str='0.24',
          number_of_decimals=1),
    Value(name='_min_frequency',
          doc='Minimum limit of frequency (rpm).',
          parameter_str='0.01',
          number_of_decimals=1)])


def example_linear_ramps(motor, max_speed=3., duration=5., steps=30):
    max_speed = float(max_speed)
    duration = float(duration)
    steps = int(steps)
    t = 0.
    speed = 0
    start_speed = motor.get_target_rotation_rate()
    motor.start_rotation(speed)
    while t < duration/2:
        sleep(duration/steps)
        speed += 2*max_speed/steps
        t += duration/steps
        motor.set_target_rotation_rate(speed, check=False)
    while t < duration:
        sleep(duration/steps)
        speed -= 2*max_speed/steps
        t += duration/steps
        if speed < 0:
            speed = 0.
        motor.set_target_rotation_rate(speed, check=False)
    motor.stop_rotation()
    motor.set_target_rotation_rate(start_speed, check=False)
    motor.lock()


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

    def control_rotation(self,
                         time, rotation_rate, fact_multiplicatif_accel=1):
        if not (isinstance(time, np.ndarray) and
                isinstance(rotation_rate, np.ndarray)):
            print("time and rotation_rate as to be of type numpy.ndarray ")
        time_instruct = 0.025  # typical time of exection of an instruction set
        maxattempt = int(max([(time[1] - time[0]) / time_instruct, 1]))
        self.set_acceleration_time(int((time[1] - time[0]) / 1000.0 *
                                       (rotation_rate[1] - rotation_rate[0]) /
                                       fact_multiplicatif_accel))
        self.start_rotation(0)
        timer = TimerIrregular(time)

        for t, ti in np.ndenumerate(time):
            t = t[0]
            count = self.set_target_rotation_rate(rotation_rate[t],
                                                  maxattempt=maxattempt)
            if ti < max(time):
                self.set_acceleration_time(int((time[t+1] - time[t]) / 1000.0 *
                                               (rotation_rate[t+1] -
                                                rotation_rate[t]) /
                                               fact_multiplicatif_accel),
                                           maxattempt=maxattempt - count)

                maxattempt = int(max([(time[t+1] - time[t]) /
                                      time_instruct, 1]))
            timer.wait_tick()
