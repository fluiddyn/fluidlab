"""unidrive_sp
    =====================
    
    .. autoclass:: Unidrive_sp
    :members:
    :private-members:
    
    
    """
from fluidlab.instruments.modbus.driver import ModbusDriver
from fluidlab.instruments.modbus.features import (
ReadOnlyBoolValue, BoolValue, ReadOnlyInt16Value, Int16Value,
ReadOnlyFloat32Value, Float32Value, Int16StringValue)


class Unidrive_sp(ModbusDriver):
    """Driver for the motor driver Unidrive sp
        
    
    """
    def autotune(self):
        raise NotImplementedError
    
    def enable_rotation(self):
        raise NotImplementedError
    
    def disable_rotation(self):
        raise NotImplementedError

    def rotate(self, speed, direction):
        raise NotImplementedError


# class ValueChecked():


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

    def _check_mode(self):
        mode = self._driver.mode.get()
        if self._mode == "all":
            pass
        elif mode != self._mode:
            raise ModeError('value {} can only be used in mode {}, and the '
            'current mode is {}'.format(self._name, self._mode, mode))

    def get(self):
        if self._mode != 'all':
            self._check_mode() # to do: integer case
        return float(super(Value, self).get()
        ) / 10 ** self._number_of_decimals

    def set(self, value):
        if self._mode != 'all':
            self._check_mode()
        super(Value, self).set(int(value * 10 ** self._number_of_decimals))


class StringValue(Int16StringValue):
    def __init__(self, name, doc='', int_dict=None,
                 menu=None, parameter=None, mode='all'):
        self._mode = mode
        self._menu = menu
        self._parameter = parameter
        adress = 100 * menu + parameter - 1
        super(StringValue, self).__init__(name, doc, int_dict, adress)

    def _check_mode(self):
        mode = self._driver.mode.get()
        if self._mode == "all":
            pass
        elif mode != self._mode:
            raise ModeError(('Value {} can only be used in mode {}, and the '
            'current mode is {}.').format(self._name, self._mode, mode))

    def get(self):
        if self._mode != 'all':
            self._check_mode()
        return super(StringValue, self).get()

    def set(self, value):
        if self._mode != 'all':
            self._check_mode()
        super(StringValue, self).set(value)


int_dict = {1:'open_loop', 2:'closed_loop', 3:'servo', 4:'regen'}
Unidrive_sp._build_class_with_features([
StringValue(name='mode',
            doc='The operating mode.',
            int_dict=int_dict, mode='all', menu=0, parameter=48),

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

