"""agilent_dsox2014a
=====================

.. autoclass:: AgilentDSOX2014a
   :members:
   :private-members:


"""
import numpy as np

from fluidlab.instruments.iec60488 import (
    IEC60488, Trigger, ObjectIdentification,
    StoredSetting, Learn)

from fluidlab.instruments.features import (
    QueryCommand, BoolValue, IntValue)


class AgilentDSOX2014a(IEC60488, Trigger, ObjectIdentification,
                       StoredSetting, Learn):
    """


    """

    def autoscale(self):
        self.interface.write(':AUTOscale')

    def get_curve(self, nb_points=1000, format='ascii'):
        """ to be implemented: max nbpoints """
        self.interface.write(':DIGitize')
        self.interface.write(':WAVeform:FORMat ' + format)
        self.interface.write(':WAVeform:POINts ' + str(nb_points))
        self.interface.write(':WAVeform:DATA?')
        raw_data = self.interface.read_raw()
        # waveform:preamble returns information for the waveform source:
        # format 16-bit NR1> (0 for BYTE, 1 for WORD, 2 for ASCii)
        # <type 16-bit NR1> (2 for AVERage, 0 for NORMal, 1 for PEAK detect)
        # <points 32-bit NR1>
        # <count 32-bit NR1> (Average count or 1 if PEAK or NORMal)
        # <xincrement 64-bit floating point NR3>
        # <xorigin 64-bit floating point NR3>
        # <xreference 32-bit NR1>
        # <yincrement 32-bit floating point NR3>
        # <yorigin 32-bit floating point NR3>
        # <yreference 32-bit NR1>
        pa = [float(s) for s in self.interface.query(
            ':WAVeform:PREamble?').split(',')]
        format = format.lower()
        if format == 'ascii':
            data = np.array([float(s) for s in raw_data[10:].split(',')])
        elif format == 'byte':
            data = np.array([(ord(s)-pa[9])*pa[7] + pa[8]
                             for s in raw_data[10:-1]])
        else:
            raise ValueError('the third argument must be ascii or byte')
        time = np.array([(s - pa[6]) * pa[4] + pa[5]
                         for s in range(nb_points)])
        return time, data


AgilentDSOX2014a._build_class_with_features([
    IntValue(
        'nb_points', doc='number of points returned.',
        command_set=':WAVeform:POINts')])


if __name__ == '__main__':
    scope = AgilentDSOX2014a(
        interface='USB0::2391::6040::MY51450715::0::INSTR')
