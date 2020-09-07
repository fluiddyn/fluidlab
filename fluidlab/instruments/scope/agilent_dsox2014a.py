"""agilent_dsox2014a
=====================

.. autoclass:: AgilentDSOX2014a
   :members:
   :private-members:

This class was tested also on Agilent DSO-X 3014A.

"""
import numpy as np

from fluidlab.instruments.iec60488 import (
    IEC60488,
    Trigger,
    ObjectIdentification,
    StoredSetting,
    Learn,
)

from fluidlab.instruments.features import (
    WriteCommand,
    BoolValue,
    IntValue,
    FloatValue,
    StringValue,
)

__all__ = ["AgilentDSOX2014a"]


class AgilentDSOX2014a(
    IEC60488, Trigger, ObjectIdentification, StoredSetting, Learn
):
    """Driver for the oscilloscope Agilent DSOX2014a."""

    def get_curve(
        self, channel=1, nb_points=65535, acquire=True, format_output="byte"
    ):
        """Acquire and return two Numpy arrays (time and data).

        Parameters
        ----------

        channel: int or Iterable of ints
          The channels to get data from

        nb_points : int
          The number of points that have to be returned (max is 65535)

        acquire: bool
          if True, starts a single acquisition
          if False, get data without restarting digitization

        format_output : string
          The format of the data that is sent from the scope.
          Has to be in ['ascii', 'byte'].

        """

        if format_output not in ["ascii", "byte"]:
            raise ValueError('format_output must be "ascii" or "byte"')

        if not isinstance(channel, int):
            data_list = []
            for ii, chan in enumerate(channel):
                t, d = self.get_curve(
                    chan, nb_points, acquire if ii == 0 else False, format_output
                )
                data_list.append(d)
            return (t, *data_list)

        # prepare the acquisition
        if acquire:
            self.interface.write(":DIGitize")
        self.interface.write(":WAVeform:FORMat " + format_output)
        self.interface.write(":WAVeform:POINts " + str(nb_points))
        self.interface.write(f":WAVeform:SOURce CHAN{channel}")

        # read the raw data
        self.interface.write(":WAVeform:DATA?")
        raw_data = self.interface.read_raw()
        if raw_data[0] != ord("#"):
            print(raw_data[0])
            raise ValueError("Bad response from Oscillo")
        nbytes = int(chr(raw_data[1]))
        nbytes_total = int(raw_data[2 : (nbytes + 2)])

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
        pre = [
            float(s)
            for s in self.interface.query(":WAVeform:PREamble?").split(",")
        ]
        xincrement = pre[4]
        xorigin = pre[5]
        xreference = pre[6]

        if format_output == "ascii":
            data = np.array(
                [float(s) for s in raw_data[(nbytes + 2) :].split(",")]
            )
        elif format_output == "byte":
            yincrement = pre[7]
            yorigin = pre[8]
            yreference = pre[9]
            data = np.array(
                [
                    (s - yreference) * yincrement + yorigin
                    for s in raw_data[(nbytes + 2) : -1]
                ]
            )

        time = np.array(
            [(s - xreference) * xincrement + xorigin for s in range(nbytes_total)]
        )

        return time, data


features = [
    WriteCommand(
        "autoscale", doc="Autoscale the oscilloscope.", command_str=":AUTOscale"
    ),
    IntValue(
        "nb_points",
        doc="The number of points returned.",
        command_set=":WAVeform:POINts",
    ),
    FloatValue(
        "timebase_range",
        doc="""The time for 10 division in seconds.""",
        command_set=":TIMebase:RANGe",
    ),
    FloatValue(
        "trigger_level",
        doc="""The trigger level voltage for the active trigger source.""",
        command_set=":TRIGger:LEVel",
    ),
]

for channel in range(1, 3):
    features += [
        FloatValue(
            f"channel{channel}_probe_attenuation",
            doc="""The probe attenuation ratio.""",
            command_set=f":CHANnel{channel}:PROBe",
        ),
        FloatValue(
            f"channel{channel}_range",
            doc="""The vertical full-scale range value (in volt).""",
            command_set=f":CHANnel{channel}:range",
        ),
        FloatValue(
            f"channel{channel}_scale",
            doc="""The number of units per division of the channel.""",
            command_set=f":CHANnel{channel}:SCALe",
        ),
        StringValue(
            f"channel{channel}_coupling",
            doc="""The type of input coupling for the channel.

It can be set to "AC" or "DC".""",
            command_set=f":CHANnel{channel}:COUPling",
            valid_values=["ac", "dc"],
        ),
        BoolValue(
            f"channel{channel}_display",
            doc="""A boolean setting the display of the channel.""",
            command_set=f":CHANnel{channel}:DISPlay",
        ),
    ]


AgilentDSOX2014a._build_class_with_features(features)


if __name__ == "__main__":
    scope = AgilentDSOX2014a(interface="USB0::0x0957::0x17A8::MY55390593::INSTR")
