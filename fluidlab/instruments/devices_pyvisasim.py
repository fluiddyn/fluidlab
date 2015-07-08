"""Example with a device defined in pyvisa-sim
==============================================

"""

from fluidlab.instruments.driver import Driver

from fluidlab.instruments.features import (
    QueryCommand, StringValue, FloatValue, BoolValue)


class Device2(Driver):
    """An IEC60488 instrument with other things"""

Device2._build_class_with_features([
    QueryCommand('get_idn', doc='Get identity.', command_str='*IDN?'),
    StringValue('rail', doc='A string rail',
                command_set='INST',
                valid_values=['P6V', 'P25V', 'N25V']),
    FloatValue('voltage', doc='The voltage (in V)',
               command_set=':VOLT:IMM:AMPL',
               limits=[0, 6]),
    FloatValue('current', doc='The current (in A)',
               command_set=':CURR:IMM:AMPL',
               limits=[0, 6]),
    BoolValue('output_enabled', doc='Output enabled',
              command_set='OUTP')])


if __name__ == '__main__':
    device = Device2('ASRL2::INSTR', backend='@sim')
