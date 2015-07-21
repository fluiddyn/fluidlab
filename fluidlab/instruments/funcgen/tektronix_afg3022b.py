"""tektronix_afg3022b
=====================

.. autoclass:: TektronixAFG3022b
   :members:
   :private-members:


"""

from fluidlab.instruments.iec60488 import (
    IEC60488, PowerOn, Calibration, Trigger, ObjectIdentification,
    StoredSetting)

from fluidlab.instruments.features import (
    QueryCommand, BoolValue, FloatValue, StringValue)


class TektronixAFG3022b(IEC60488, PowerOn, Calibration,
                        Trigger, ObjectIdentification, StoredSetting):
    """


    """

    # def set_function_shape(self, shape):
    #     """Set the function's shape

    #     Parameters
    #     ----------

    #     shape : string
    #       defining the function shape. Has to be in ['sine', 'sin',
    #       'ramp', 'square'] (not case sensitive)

    #     """
    #     shape = shape.lower()
    #     if shape in ('sin', 'sine'):
    #         self.interface.write('FUNCTION SIN')
    #     elif shape == 'ramp':
    #         self.interface.write('FUNCTION RAMP')
    #     elif shape == 'square':
    #         self.interface.write('FUNCTION SQUARE')
    #     else:
    #         raise ValueError('First argument must be sin, ramp or square')


TektronixAFG3022b._build_class_with_features([
    BoolValue('output1_state', doc='', command_set='OUTPut1:STATe'),
    BoolValue('output2_state', doc='', command_set='OUTPut2:STATe'),
    StringValue('function_shape', doc='', command_set='FUNCTION',
                valid_values=['sin', 'sine', 'ramp', "squ",  'square']),
    FloatValue(
        'frequency', doc='The function frequency.', command_set='FREQUENCY'),
    FloatValue(
        'voltage',
        doc=(
"""Peak to peak voltage.

Warning: The voltage depends on the impedance of the receiver of the signal.
If its impedence is high, the actual output voltage is twice what it should be.
If its impedance is 50ohm, there is no problem.

"""),
        command_set='VOLTAGE:AMPLITUDE'),
    FloatValue(
        'offset', doc='The function offset.', command_set='VOLTAGE:OFFSET')])


if __name__ == '__main__':
    funcgen = TektronixAFG3022b(interface='USB0::1689::839::C034062::0::INSTR')
