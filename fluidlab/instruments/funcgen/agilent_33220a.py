"""Agilent 33220a
=================

.. autoclass:: Agilent33220a
   :members:
   :private-members:


"""

__all__ = ["Agilent33220a"]

from fluidlab.instruments.iec60488 import (
    IEC60488, PowerOn, Calibration, Trigger, ObjectIdentification, StoredSetting
)


from fluidlab.instruments.features import SuperValue, QueryCommand

import re


class Agilent33220a_Vdc(SuperValue):

    def __init__(self):
        super(Agilent33220a_Vdc, self).__init__("vdc", doc="DC voltage")

    def set(self, value):
        self._interface.write("OUTP:LOAD INF")
        self._interface.write("APPLY:DC DEF, DEF, " + str(value))
        if value != 0.0:
            self._interface.write("OUTP ON")
        else:
            self._interface.write("OUTP OFF")

    def get(self):
        valeurs = self._driver.get_generator_state()
        return valeurs[3]


class Agilent33220a_Vrms(SuperValue):

    def __init__(self):
        super(Agilent33220a_Vrms, self).__init__("vrms", doc="RMS voltage")

    def set(self, value):
        self._interface.write("OUTP:LOAD INF")
        self._interface.write("VOLT:UNIT VRMS")
        if value != 0.0:
            (iFunc, iFreq, iAmpl, iOffset) = self._driver.get_generator_state()
            self._interface.write(
                "APPLY:SIN "
                + str(iFreq)
                + ", "
                + str(value)
                + ", "
                + str(iOffset)
            )
            self._interface.write("OUTP ON")
        else:
            self._interface.write("OUTP OFF")

    def get(self):
        valeurs = self._driver.get_generator_state()
        return valeurs[2]


class Agilent33220a_Frequency(SuperValue):

    def __init__(self):
        super(Agilent33220a_Frequency, self).__init__(
            "frequency", doc="Wave frequency"
        )

    def set(self, value):
        (iFunc, iFreq, iAmpl, iOffset) = self._driver.get_generator_state()
        self._interface.write(
            "APPLY:SIN " + str(value) + ", " + str(iAmpl) + ", " + str(iOffset)
        )

    def get(self):
        valeurs = self._driver.get_generator_state()
        return valeurs[1]


def parse_agilent33220a_configuration_str(str):
    """Parse the Agilent 33220A configuration string.

    Returns 4 elements: function name, frequency, amplitude, offset """
    valeurs = re.split(",", str)
    function_frequency = valeurs[0]
    amplitude = valeurs[1]
    offset = valeurs[2]
    Nchars = len(offset)
    valeurs = re.split(" ", function_frequency)
    function = valeurs[0]
    frequency = valeurs[1]
    return (
        function[1::],
        float(frequency),
        float(amplitude),
        float(offset[0:(Nchars - 2)]),
    )


class Agilent33220a(
    IEC60488, PowerOn, Calibration, Trigger, ObjectIdentification, StoredSetting
):
    """
    A driver for the function generator Agilent 33220A


    """

    def configure_am(self, vrms_min, vrms_max, freq, am_freq):
        self.interface.write("OUTP:LOAD INF")
        self.interface.write("VOLT:UNIT VRMS")
        self.interface.write(
            "APPL:SIN {freq:}, {ampl:}, 0.0".format(freq=freq, ampl=vrms_max)
        )
        self.interface.write("AM:INT:FUNC SQU")
        self.interface.write("AM:INT:FREQ {freq:}".format(freq=am_freq))
        self.interface.write(
            "AM:DEPT {ratio:d}".format(
                ratio=int(100.0 * (1.0 - (vrms_min / vrms_max)))
            )
        )
        self.interface.write("AM:STAT ON")
        self.interface.write("OUTP ON")

    def configure_square(self, vmin, vmax=None, freq=None):
        """
        Set the device in Square function
        """

        if vmax and freq:
            vpp = vmax - vmin
            voffset = (vmin + vmax) / 2
            self.interface.write("OUTP:LOAD INF")
            self.interface.write(
                "APPL:SQU {freq:}, {ampl:}, {offset:}".format(
                    freq=freq, ampl=vpp, offset=voffset
                )
            )
            self.interface.write("OUTP ON")
        else:
            if vmin == 0:
                self.interface.write("OUTP OFF")
            else:
                raise ValueError("Bad arguments")

    def configure_burst(self, freq, ncycles):
        """
        Configure a TTL burst with a given number of cycles
        Send *TRG or gbf.trigger() to start a burst
        """

        self.interface.write("OUTP:LOAD INF")
        self.interface.write(
            "APPL:SQU {freq:} HZ, 5 VPP, +2.5 V".format(freq=freq)
        )
        self.interface.write("BURS:MODE TRIG")
        self.interface.write("BURS:NCYC {ncycles:}".format(ncycles=ncycles))
        self.interface.write("BURS:PHAS 0")
        self.interface.write("TRIG:SOUR BUS")
        self.interface.write("BURS:STAT ON")
        self.interface.write("OUTP ON")


features = [
    QueryCommand(
        "get_generator_state",
        doc="Get the current configuration of the funcgen",
        command_str="APPLy?",
        parse_result=parse_agilent33220a_configuration_str,
    ),
    Agilent33220a_Vdc(),
    Agilent33220a_Vrms(),
    Agilent33220a_Frequency(),
]

Agilent33220a._build_class_with_features(features)
