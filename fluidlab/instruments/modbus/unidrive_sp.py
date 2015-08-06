"""unidrive_sp
    =====================
    
    .. autoclass:: Unidrive_sp
    :members:
    :private-members:
    
    
    """
from fluidlab.instrument.modbus.driver import ModbusDriver
from fluidlab.instrument.modbus.features import (ReadOnlyBoolValue, BoolValue, ReadOnlyInt16Value, Int16Value, ReadOnlyFloat32Value, Float32Value, Int16StringValue)


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

class ValueChecked():

class Value(Int16Value):
    def __init__(self, name, doc='', menu=None, parameter=None, mode='all', number_of_decimals=0):
        if menu is None or parameter is None:
            raise ValueError('menu and parameter should not be None.')
        self.mode = mode
        self._adress = 100 * menu + parameter - 1
        super(Value, self).__init__(name, doc)
    
    def check_mode(self):
        #if self.mode == 'all':
        #    return
        mode = self._driver.mode.get()
        if mode != self.mode:
            raise ModeError('value {} can only be used in mode {}, and the current mode is {}'.format(self.name, self.mode, mode))

    def get(self):
        if self.mode != 'all': #
            self.checkmode() # to do: integer case
        return float(self._interface.read_int16(self._adress)) / 10 ** number_of_decimals
    
    def set(self, value):
        if self.mode != 'all': #
            self.checkmode() #
        self._interface.write_int16(self._adress, int(value * 10 ** number_of_decimals)

                                    
class StringValue(Int16StringValue):
    def __init__(self, name, doc='', keys_ints=None, menu=None, parameter=None, mode='all'):
        self.mode = mode
        self._adress = 100 * menu + parameter - 1
        self.interger_list = interger_list
        self.string_list = string_list
        super(Value, self).__init__(name, doc)
                 
    def check_mode(self): #
        #if self.mode == 'all':
        #    return
        mode = self._driver.mode.get()
        if mode != self.mode:
            raise ModeError(
                ('Value {} can only be used in mode {}, '
                 'and the current mode is {}.').format(self.name, self.mode, mode))

    def get(self):
        if self.mode != 'all':
            self.checkmode()
        super(StringValue, self).get()
                                    
    def set(self, value):
        if self.mode != 'all':
            self.checkmode()
        super(StringValue, self).set(value)
                              

integers = [1, 2, 3, 4]
modes = ['open_loop', 'closed_loop', 'servo', 'regen']
Unidrive_sp._build_class_with_features([
StringValue('mode', doc='The operating mode.', integers, modes, mode='all', menu=0, paramater=48),
Value('min_frequency_open_loop', doc='Minimum limit of frequency (Hz). Used in open loop.', 1, 'open_loop', 0, 1),
Value('min_speed_closed_loop', doc='Minimum limit of speed (rpm). Used in closed loop.', 1, 'closed_loop', 0, 1),
Value('min_speed_servo', doc='Minimum limit of speed (rpm). Used in servo.', 1, 'servo', 0, 1),
Value('acceleration_time', doc='The time to go from 0Hz to 100Hz (s).', 1, 'all', 0, 3),
Value('deceleration_time', doc='The time to go from 100Hz to 0Hz (s).', 1, 'all', 0, 3),
                                        
Value('nominal_voltage', doc='The nominal voltage of the motor (V).', 0, 44),
Value('nominal_speed', doc='The nominal speed of the motor (rpm). Used in open loop and closed loop.', 0, 45)
Value('thermal_time_constant', doc='The thermal time constant of the motor. Used in servo.', 0, 46)
Value('', doc='', 0, 47)
                                        
#eu/us, bo/bf/servo, freqmax, acceler, deceler, tensionnom, vitessenom, courantnom, freqnom, nbpoles, ?
#WriteCommand('autoscale', doc='Autoscale the oscilloscope.', command_str=':AUTOscale'),
#IntValue('nb_points', doc='Number of points returned.', command_set=':WAVeform:POINts'),
])

