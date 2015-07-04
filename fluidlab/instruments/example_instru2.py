"""Example of a instrument with trigger
=======================================

"""

from fluidlab.instruments.iec60488 import IEC60488

from fluidlab.instruments.features import StringValue, NumberValue


class Instru2(IEC60488):
    """An IEC60488 instrument with other things"""

    def do_something_particular(self):
        """Do something really particular"""


features = [
    StringValue('str0', doc='A string',
                command_get='*str?', command_set='*str',
                possible_values=['0', '1']),
    NumberValue('num0', doc='A number',
                command_get='*num?', command_set='*num',
                limits=[0, 1])]

Instru2._build_class(features)


if __name__ == '__main__':
    instr = Instru2()
