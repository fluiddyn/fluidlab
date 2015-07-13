"""agilent_dsox2014a
=====================

.. autoclass:: AgilentDSOX2014a
   :members:
   :private-members:


"""

from fluidlab.instruments.iec60488 import (
    IEC60488, PowerOn, Calibration, Trigger, ObjectIdentification,
    StoredSetting)

from fluidlab.instruments.features import (
    QueryCommand, BoolValue, IntValue)


class AgilentDSOX2014a(IEC60488, PowerOn, Calibration,
                       Trigger, ObjectIdentification, StoredSetting):
    """


    """


AgilentDSOX2014a._build_class_with_features([
    IntValue(
        'nb_points', doc='number of points returned.',
        command_set=':WAVeform:POINts')])


if __name__ == '__main__':
    scope = AgilentDSOX2014a(
        interface='USB0::2391::6040::MY51450715::0::INSTR')
