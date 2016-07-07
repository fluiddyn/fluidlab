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
    WriteCommand, BoolValue, IntValue, FloatValue, StringValue)

__all__ = ["AgilentDSOX2014a"]

class AgilentDSOX2014a(IEC60488, Trigger, ObjectIdentification,
                       StoredSetting, Learn):
    """Driver for the oscilloscope Agilent DSOX2014a.


    """

    def get_curve(self, nb_points=1000, format_output='byte'):
        """Acquire and return two Numpy arrays (time and data).

        Parameters
        ----------

        nb_points : int
          The number of points that have to be returned.

        format_output : string
          The format of the data that is sent from the scope.
          Has to be in ['ascii', 'byte'].

        """

        # to be implemented: max nb_points

        if format_output not in ['ascii', 'byte']:
            raise ValueError('format_output must be "ascii" or "byte"')

        # prepare the acquisition
        self.interface.write(':DIGitize')
        self.interface.write(':WAVeform:FORMat ' + format_output)
        self.interface.write(':WAVeform:POINts ' + str(nb_points))

        # read the raw data
        self.interface.write(':WAVeform:DATA?')
        raw_data = self.interface.read_raw()

        # parse the raw data
        # waveform:preamble returns information for the waveform source:
        # - format (0 for BYTE, 1 for WORD, 2 for ASCii)
        # - type (2 for AVERage, 0 for NORMal, 1 for PEAK detect)
        # - points
        # - count (Average count or 1 if PEAK or NORMal)
        # - xincrement
        # - xorigin
        # - xreference
        # - yincrement
        # - yorigin
        # - yreference
        pre = [float(s) for s in self.interface.query(
            ':WAVeform:PREamble?').split(',')]
        xincrement = pre[4]
        xorigin = pre[5]
        xreference = pre[6]

        time = np.array([(s - xreference) * xincrement + xorigin
                         for s in range(nb_points)])

        if format_output == 'ascii':
            data = np.array([float(s) for s in raw_data[10:].split(',')])
        elif format_output == 'byte':
            yincrement = pre[7]
            yorigin = pre[8]
            yreference = pre[9]
            data = np.array([(ord(s) - yreference) * yincrement + yorigin
                             for s in raw_data[10:-1]])

        return time, data


features = [
    WriteCommand(
        'autoscale', doc='Autoscale the oscilloscope.',
        command_str=':AUTOscale'),
    IntValue(
        'nb_points', doc='The number of points returned.',
        command_set=':WAVeform:POINts'),
    FloatValue(
        'timebase_range',
        doc="""The time for 10 division in seconds.""",
        command_set=':TIMebase:RANGe'),
    FloatValue(
        'trigger_level',
        doc="""The trigger level voltage for the active trigger source.""",
        command_set=':TRIGger:LEVel')]

for channel in range(1, 3):
    features += [
        FloatValue(
            'channel{}_probe_attenuation'.format(channel),
            doc="""The probe attenuation ratio.""",
            command_set=':CHANnel{}:PROBe'.format(channel)),
        FloatValue(
            'channel{}_range'.format(channel),
            doc="""The vertical full-scale range value (in volt).""",
            command_set=':CHANnel{}:range'.format(channel)),
        FloatValue(
            'channel{}_scale'.format(channel),
            doc="""The number of units per division of the channel.""",
            command_set=':CHANnel{}:SCALe'.format(channel)),
        StringValue(
            'channel{}_coupling'.format(channel),
            doc="""The type of input coupling for the channel.

It can be set to "AC" or "DC".""",
            command_set=':CHANnel{}:COUPling'.format(channel),
            valid_values=['ac', 'dc']),
        BoolValue(
            'channel{}_display'.format(channel),
            doc="""A boolean setting the display of the channel.""",
            command_set=':CHANnel{}:DISPlay'.format(channel))]


AgilentDSOX2014a._build_class_with_features(features)


if __name__ == '__main__':
    scope = AgilentDSOX2014a(
        interface='USB0::2391::6040::MY51450715::0::INSTR')
