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


AgilentDSOX2014a._build_class_with_features([
    WriteCommand(
        'autoscale', doc='Autoscale the oscilloscope.',
        command_str=':AUTOscale'),
    IntValue(
        'nb_points', doc='The number of points returned.',
        command_set=':WAVeform:POINts'),
    FloatValue(
        'channel1_probe_attenuation',
        doc="""The probe attenuation ratio.""",
        command_set=':CHANnel1:PROBe'),
    FloatValue(
        'channel1_range',
        doc="""The vertical full-scale range value (in volt).""",
        command_set=':CHANnel1:range'),
    FloatValue(
        'channel1_scale',
        doc="""The number of units per division of the channel.""",
        command_set=':CHANnel1:SCALe'),
    StringValue(
        'channel1_coupling',
        doc="""The type of input coupling for the channel.

        It can be set to "AC" or "DC".""",
        command_set=':CHANnel1:COUPling',
        valid_values=['ac', 'dc']),
    BoolValue(
        'channel1_display',
        doc="""A boolean setting the display of the channel.""",
        command_set=':CHANnel1:DISPlay'),
    FloatValue(
        'timebase_range',
        doc="""The time for 10 division in seconds.""",
        command_set=':TIMebase:RANGe'),
    FloatValue(
        'trigger_level',
        doc="""The trigger level voltage for the active trigger source.""",
        command_set=':TRIGger:LEVel')
])


if __name__ == '__main__':
    scope = AgilentDSOX2014a(
        interface='USB0::2391::6040::MY51450715::0::INSTR')
