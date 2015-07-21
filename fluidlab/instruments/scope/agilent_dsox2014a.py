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

from fluidlab.instruments.features import (QueryCommand, BoolValue, IntValue)


class AgilentDSOX2014a(IEC60488, Trigger, ObjectIdentification,
                       StoredSetting, Learn):
    """


    """

    def autoscale(self):
        """ Autoscale the scope """
        self.interface.write(':AUTOscale')

    def get_curve(self, nb_points=1000, format_output='ascii', warn=True):
        """Returns two lists:
        The first is the list of the X-axis coordinates
        The second is the list of the Y-axis coordinates

        Parameters
        ----------

        nb_points : int
          number of points returned

        format_output : string
          format of the data that is sent from the scope.
          Has to be in ['ascii', 'byte']

         """
        self.interface.write(':DIGitize')
        self.interface.write(':WAVeform:FORMat ' + format_output)
        # self.interface.write(':WAVeform:POINts ' + str(nb_points))
        self.nb_points.set(nb_points, warn)
        self.interface.write(':WAVeform:DATA?')
        raw_data = self.interface.read_raw()
        # waveform:preamble returns information for the waveform source:
        # format (0 for BYTE, 1 for WORD, 2 for ASCii)
        # type (2 for AVERage, 0 for NORMal, 1 for PEAK detect)
        # points
        # count (Average count or 1 if PEAK or NORMal)
        # xincrement
        # xorigin
        # xreference
        # yincrement
        # yorigin
        # yreference
        pa = [float(s) for s in self.interface.query(
            ':WAVeform:PREamble?').split(',')]
        format_output = format_output.lower()
        if format_output == 'ascii':
            data = np.array([float(s) for s in raw_data[10:].split(',')])
        elif format_output == 'byte':
            data = np.array([(ord(s)-pa[9])*pa[7] + pa[8]
                             for s in raw_data[10:-1]])
        else:
            raise ValueError('the third argument must be ascii or byte')
        time = np.array([(s - pa[6]) * pa[4] + pa[5]
                         for s in range(len(data))])
        return time, data


AgilentDSOX2014a._build_class_with_features([
    IntValue(
        'nb_points', doc='number of points returned.',
        command_set=':WAVeform:POINts')])

if __name__ == '__main__':
    scope = AgilentDSOX2014a(
        interface='USB0::2391::6040::MY51450715::0::INSTR')
