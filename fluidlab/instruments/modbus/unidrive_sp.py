"""Unidrive SP motor (Leroy Somer)
==================================

.. autoclass:: UnidriveSP
   :members:
   :private-members:

"""

from time import sleep

from fluidlab.instruments.modbus.driver import ModbusDriver
from fluidlab.instruments.modbus.features import Int16Value, Int16StringValue

import warnings


def custom_formatwarning(message, category, filename, lineno, line=None):
    return '{}:{}: {}: {}\n'.format(
        filename, lineno, category.__name__, message)

warnings.formatwarning = custom_formatwarning
warnings.simplefilter('always', UserWarning)


class UnidriveSP(ModbusDriver):
    """Driver for the motor driver Unidrive SP

    Parameters
    ----------

    port : {None, str}
      The port where the motor is plugged.

    timeout : {1, number}
      Timeout for the communication with the motor (in s).

    module : {'minimalmodbus', str}
      Module used to communicate with the motor.

    """
    _constant_nb_poles = 4

    def __init__(self, port=None, timeout=1,
                 module='minimalmodbus'):

        if port is None:
            from fluidlab.util import userconfig
            try:
                port = userconfig.port_unidrive_sp
            except AttributeError:
                raise ValueError(
                    'If port is None, "port_unidrive_sp" has to be defined in'
                    ' one of the FluidLab user configuration files.')

        super(UnidriveSP, self).__init__(port=port, method='rtu',
                                         timeout=timeout, module=module)

    # def autotune(self):
    #     raise NotImplementedError

    def unlock(self):
        """Unlock the motor (then rotation is possible)."""
        self._unlocked.set(1)

    def lock(self):
        """Lock the motor (then rotation is not possible)."""
        self._unlocked.set(0)

    def set_target_rotation_rate(self, rotation_rate, check=False):
        """Set the target rotation rate in Hz."""
        # The value `_speed` is actually equal to _constant_nb_poles
        # times the rotation rate in Hz.
        self._speed.set(self._constant_nb_poles * rotation_rate,
                        check=check)

    def get_target_rotation_rate(self):
        """Get the target rotation rate in Hz."""
        # The value `_speed` is actually equal to _constant_nb_poles
        # times the rotation rate in Hz.
        raw_speeed = self._speed.get()
        return raw_speeed / self._constant_nb_poles

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


class ModeError(Exception):
    """Some values are only useable in one mode (open_loop, closed_loop, servo)
    When a value is used, a function checks the current mode, and raises
    a ModeError if it doesn't match.
    """
    pass


class Value(Int16Value):
    def __init__(self, name, doc='', number_of_decimals=0, mode='all',
                 menu=None, parameter=None):
        if menu is None or parameter is None:
            raise ValueError('menu and parameter should not be None.')
        self._number_of_decimals = number_of_decimals
        self._mode = mode
        self._menu = menu
        self._parameter = parameter
        adress = 100 * menu + parameter - 1
        super(Value, self).__init__(name, doc, adress)

    def get(self):
        if self._mode != 'all':
            self._check_mode()  # to do: integer case

        raw_value = super(Value, self).get()

        if self._number_of_decimals == 0:
            return raw_value
        else:
            return float(raw_value) / 10 ** self._number_of_decimals

    def set(self, value, check=True):
        """Set the Value to value.

        If check, checks that the value was properly set.
        """
        if self._mode != 'all':
            self._check_mode()
        super(Value, self).set(int(value * 10 ** self._number_of_decimals))
        if check:
            self._check_instrument_value(value)

    def _check_mode(self):
        mode = self._driver.mode.get()
        if self._mode == "all":
            pass
        elif mode != self._mode:
            raise ModeError(
                'value {} can only be used in mode {}, and the '
                'current mode is {}'.format(self._name, self._mode, mode))

    def _check_instrument_value(self, value):
        """After a value is set, checks the instrument value and
        sends a warning if it doesn't match."""
        instr_value = self.get()
        if instr_value != value:
            msg = (
                'Value {} could not be set to {} and was set to {} instead'
            ).format(self._name, value, instr_value)
            warnings.warn(msg, UserWarning)


class StringValue(Int16StringValue):
    def __init__(self, name, doc='', int_dict=None,
                 menu=None, parameter=None, mode='all'):
        self._mode = mode
        self._menu = menu
        self._parameter = parameter
        adress = 100 * menu + parameter - 1
        super(StringValue, self).__init__(name, doc, int_dict, adress)

    def get(self):
        if self._mode != 'all':
            self._check_mode()
        return super(StringValue, self).get()

    def set(self, value, check=True):
        """Set the Value to value.
        If check equals 1, checks that the value was properly set.
        To disable this function, enter check = 0
        """
        if self._mode != 'all':
            self._check_mode()
        super(StringValue, self).set(value)
        if check:
            self._check_instrument_value(value)

    def _check_mode(self):
        mode = self._driver.mode.get()
        if self._mode == "all":
            pass
        elif mode != self._mode:
            raise ModeError(
                ('Value {} can only be used in mode {}, and the '
                 'current mode is {}.').format(self._name, self._mode, mode))

    def _check_instrument_value(self, value):
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

UnidriveSP._build_class_with_features([
    StringValue(name='mode',
                doc='The operating mode.',
                int_dict=int_dict_mode, mode='all', menu=0, parameter=48),

    StringValue(name='_reference_selection',
                doc=('Defines how the rotation speed is given to the motor.'
                     '"preset" is what we want here, '
                     '"pad" means it can be entered with the arrow keys '
                     'of the motor pad'),
                int_dict=int_dict_ref, mode='all', menu=0, parameter=5),

    Value(name='_unlocked',
          doc=('When this variable is equal to 0, '
               'the motor is inhibited and displays "Inh". '
               'When it is equal to 1, the motor is ready to run '
               'and displays "Rdy".'),
          number_of_decimals=0, mode='all', menu=6, parameter=15),

    Value(name='_rotate',
          doc='Set this to 1 to give an order of rotation',
          number_of_decimals=0, mode='all', menu=6, parameter=34),

    Value(name='_speed',
          doc=('Speed of rotation. Warning: the actual speed in Hz is equal '
               'to this value divided by the number of poles.'),
          number_of_decimals=1, mode='all', menu=0, parameter=24),

    Value(name='_min_frequency_open_loop',
          doc='Minimum limit of frequency (Hz). Used in open loop.',
          number_of_decimals=1, mode='open_loop', menu=0, parameter=1),

    Value(name='_min_speed_closed_loop',
          doc='Minimum limit of speed (rpm). Used in closed loop.',
          number_of_decimals=1, mode='closed_loop', menu=0, parameter=1),

    Value(name='_min_speed_servo',
          doc='Minimum limit of speed (rpm). Used in servo.',
          number_of_decimals=1, mode='servo', menu=0, parameter=1),

    Value(name='acceleration_time',
          doc='The time to go from 0 Hz to 100 Hz (s).',
          number_of_decimals=1, mode='all', menu=0, parameter=3),

    Value(name='deceleration_time',
          doc='The time to go from 100 Hz to 0 Hz (s).',
          number_of_decimals=1, mode='all', menu=0, parameter=4),

    Value(name='_number_of_pairs_of_poles',
          doc='The number of pairs of poles of the motor.',
          number_of_decimals=0, mode='all', menu=0, parameter=42),

    Value(name='_rated_voltage',
          doc='The Rated voltage of the motor (V).',
          number_of_decimals=0, mode='all', menu=0, parameter=44),

    Value(name='_rated_speed_open_loop',
          doc='Rated speed of the motor (rpm). Used in open loop.',
          number_of_decimals=0, mode='open_loop', menu=0, parameter=45),

    Value(name='_rated_speed_closed_loop',
          doc='Rated speed of the motor (rpm). Used in closed loop.',
          number_of_decimals=0, mode='closed_loop', menu=0, parameter=45),

    Value(name='_thermal_time_constant_servo',
          doc='Thermal time constant of the motor. Used in servo.',
          number_of_decimals=0, mode='servo', menu=0, parameter=45),

    Value(name='_rated_current_open_loop',
          doc='Rated current of the motor. Used in open loop.',
          number_of_decimals=2, mode='open_loop', menu=0, parameter=46),

    Value(name='_rated_current_closed_loop',
          doc='Rated current of the motor. Used in closed loop.',
          number_of_decimals=2, mode='closed_loop', menu=0, parameter=46),

    Value(name='_rated_frequency_open_loop',
          doc='Rated frequency of the motor. Used in open loop.',
          number_of_decimals=1, mode='open_loop', menu=0, parameter=47),

    Value(name='_rated_frequency_closed_loop',
          doc='Rated frequency of the motor. Used in closed loop.',
          number_of_decimals=1, mode='closed_loop', menu=0, parameter=47)
])


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
            speed=0.
        motor.set_target_rotation_rate(speed, check=False)
    motor.stop_rotation()
    motor.set_target_rotation_rate(start_speed, check=False)
    motor.lock()
