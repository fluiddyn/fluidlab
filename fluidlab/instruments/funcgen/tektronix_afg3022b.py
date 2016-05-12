"""tektronix_afg3022b
=====================

.. autoclass:: TektronixAFG3022b
   :members:
   :private-members:


"""

__all__ = ['TektronixAFG3022b']

from fluidlab.instruments.iec60488 import (
    IEC60488, PowerOn, Calibration, Trigger, ObjectIdentification,
    StoredSetting)

from fluidlab.instruments.features import (
    BoolValue, FloatValue, StringValue)


class TektronixAFG3022b(IEC60488, PowerOn, Calibration,
                        Trigger, ObjectIdentification, StoredSetting):
    """
    A driver for the function generator Tektronix AFG 3022 B.



    """

TektronixAFG3022b._build_class_with_features([
    BoolValue('output1_state', doc='', command_set='OUTPut1:STATe'),
    BoolValue('output2_state', doc='', command_set='OUTPut2:STATe'),
    StringValue(
        'function_shape',
        doc=(
"""The function shape (str).

Has to be in ['sine', 'sin', 'ramp', 'square'] (not case sensitive)

"""),
        command_set='FUNCTION',
        valid_values=['sin', 'sine', 'ramp', "squ",  'square']),
    FloatValue(
        'frequency', doc='The function frequency.', command_set='FREQUENCY'),
    FloatValue(
        'voltage',
        doc=(
"""Peak to peak voltage (in volt).

Warning: The voltage depends on the impedance of the receiver of the
signal.  If its impedence is very large, the actual output voltage is
twice what it should be.  If its impedance is 50 ohm, there is no
problem.

"""),
        command_set='VOLTAGE:AMPLITUDE'),
    FloatValue(
        'offset', doc='The function offset (in volt).',
        command_set='VOLTAGE:OFFSET')])


if __name__ == '__main__':
    funcgen = TektronixAFG3022b(interface='USB0::1689::839::C034062::0::INSTR')
