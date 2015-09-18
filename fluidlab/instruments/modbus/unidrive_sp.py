"""Unidrive SP motor (Leroy Somer)
==================================

.. autoclass:: Unidrive_sp
   :members:
   :private-members:

"""

from fluidlab.instruments.modbus.driver import ModbusDriver
from fluidlab.instruments.modbus.features import Int16Value, Int16StringValue

import warnings


def custom_formatwarning(message, category, filename, lineno, line=None):
    return '{}:{}: {}: {}\n'.format(
        filename, lineno, category.__name__, message)

warnings.formatwarning = custom_formatwarning
warnings.simplefilter('always', UserWarning)


class Unidrive_sp(ModbusDriver):
    """Driver for the motor driver Unidrive SP


    """
    def autotune(self):
        raise NotImplementedError

    def enable_rotation(self):
        self.unlock.set(1)

    def disable_rotation(self):
        self.unlock.set(0)

    def start_rotation(self, speed=None, direction=None):
        """Start the motor rotation.

        If speed is not None, set the motor speed (Hz) and start the
        rotation.  If speed is None, start the rotation with whatever
        speed the motor has

        """
        self.reference_selection.set("preset")
        if speed is not None:
            # the real speed is acutally one forth of the speed value
            # of the motor. 4*speed is here to compensate for this
            self.speed.set(4*speed)
        self._rotate.set(1)

    def stop_rotation(self):
        self.reference_selection.set("preset")
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
        return float(super(Value, self).get()) / 10 ** self._number_of_decimals

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

Unidrive_sp._build_class_with_features([
    StringValue(name='mode',
                doc='The operating mode.',
                int_dict=int_dict_mode, mode='all', menu=0, parameter=48),

    StringValue(name='reference_selection',
                doc=('Defines how the rotation speed is given to the motor.'
                     '"preset" is what we want here, '
                     '"pad" means it can be entered with the arrow keys '
                     'of the motor pad'),
                int_dict=int_dict_ref, mode='all', menu=0, parameter=5),

    Value(name='unlock',
          doc=('When this is 0, the motor is inhibited, it displays Inh'
               'When this is 1, the motor is ready to run, it displays Rdy'),
          number_of_decimals=0, mode='all', menu=6, parameter=15),

    Value(name='_rotate',
          doc='Set this to 1 to give an order of rotation',
          number_of_decimals=0, mode='all', menu=6, parameter=34),

    Value(name='speed',
          doc='Speed of rotation. The actual speed in a forth of this.',
          number_of_decimals=1, mode='all', menu=0, parameter=24),

    Value(name='min_frequency_open_loop',
          doc='Minimum limit of frequency (Hz). Used in open loop.',
          number_of_decimals=1, mode='open_loop', menu=0, parameter=1),

    Value(name='min_speed_closed_loop',
          doc='Minimum limit of speed (rpm). Used in closed loop.',
          number_of_decimals=1, mode='closed_loop', menu=0, parameter=1),

    Value(name='min_speed_servo',
          doc='Minimum limit of speed (rpm). Used in servo.',
          number_of_decimals=1, mode='servo', menu=0, parameter=1),

    Value(name='acceleration_time',
          doc='The time to go from 0Hz to 100Hz (s).',
          number_of_decimals=1, mode='all', menu=0, parameter=3),

    Value(name='deceleration_time',
          doc='The time to go from 100Hz to 0Hz (s).',
          number_of_decimals=1, mode='all', menu=0, parameter=4),

    Value(name='number_of_pairs_of_poles',
          doc='The number of pairs of poles of the motor',
          number_of_decimals=0, mode='all', menu=0, parameter=42),

    Value(name='rated_voltage',
          doc='The Rated voltage of the motor (V).',
          number_of_decimals=0, mode='all', menu=0, parameter=44),

    Value(name='rated_speed_open_loop',
          doc='Rated speed of the motor (rpm). Used in open loop.',
          number_of_decimals=0, mode='open_loop', menu=0, parameter=45),

    Value(name='rated_speed_closed_loop',
          doc='Rated speed of the motor (rpm). Used in closed loop.',
          number_of_decimals=0, mode='closed_loop', menu=0, parameter=45),

    Value(name='thermal_time_constant_servo',
          doc='Thermal time constant of the motor. Used in servo.',
          number_of_decimals=0, mode='servo', menu=0, parameter=45),

    Value(name='rated_currant_open_loop',
          doc='Rated current of the motor. Used in open loop.',
          number_of_decimals=2, mode='open_loop', menu=0, parameter=46),

    Value(name='rated_currant_closed_loop',
          doc='Rated current of the motor. Used in closed loop.',
          number_of_decimals=2, mode='closed_loop', menu=0, parameter=46),

    Value(name='rated_frequency_open_loop',
          doc='Rated frequency of the motor. Used in open loop.',
          number_of_decimals=1, mode='open_loop', menu=0, parameter=47),

    Value(name='rated_frequency_closed_loop',
          doc='Rated frequency of the motor. Used in closed loop.',
          number_of_decimals=1, mode='closed_loop', menu=0, parameter=47)
])
