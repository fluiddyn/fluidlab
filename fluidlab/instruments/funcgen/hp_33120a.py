"""Hewlett Packard 33120A
=========================

.. autoclass:: HP33120a
   :members:
   :private-members:


"""

__all__ = ["HP33120a"]

from fluidlab.instruments.iec60488 import IEC60488, Trigger
from fluidlab.instruments.features import SuperValue, FloatValue


class HP33120a(IEC60488, Trigger):
    """
    Driver for the function generator Hewlett-Packard 33120A

    """

    def configure_burst(self, freq, ncycles):
        """Configure a TTL burst with a given number of cycles
        Send ``*TRG`` or ``gbf.trigger()`` to start a burst.

        Conditions: ncyles must be <= 50000 and if freq <= 100 Hz, we
        must have:
        burst count / carrier frequency <= 500 seconds
        """

        if freq <= 100.0 and ncycles / freq > 500.0:
            raise ValueError(
                "For freq <= 100 Hz, ncycles/freq must be <= 500 seconds"
            )
        if ncycles > 50000:
            raise ValueError("Maximum count number is 50000")
        self.interface.write("OUTP:LOAD INF")
        self.interface.write(f"APPL:SQU {freq} HZ, 5 VPP, +2.5 V")
        self.interface.write(f"BM:NCYC {ncycles}")
        self.interface.write("BM:PHAS -20")
        self.interface.write("TRIG:SOUR BUS")
        self.interface.write("BM:STAT ON")
        
    def configure_square(self, vmin, vmax=None, freq=None):
        """
        Set the device in Square function
        """

        if vmax and freq:
            vpp = vmax - vmin
            voffset = (vmin + vmax) / 2
            self.interface.write("OUTP:LOAD INF")
            self.interface.write(
                "APPL:SQU {freq:} HZ, {ampl:} VPP, {offset:} V".format(
                    freq=freq, ampl=vpp, offset=voffset
                )
            )


class HP33120a_ShapeValue(SuperValue):
    shapes = {
        "sine": "SIN",
        "square": "SQU",
        "triangle": "TRI",
        "ramp": "RAMP",
        "noise": "NOIS",
        "dc": "DC",
    }

    def __init__(self):
        super().__init__("shape", doc="Shape of the output signal")

    def set(self, value):
        if value not in self.shapes.keys():
            raise ValueError(
                "Bad shape name. Possible values are sine, square, triangle, ramp, noise or dc"
            )

        self._interface.write("SOUR:FUNC:SHAP " + self.shapes[value])

    def get(self):
        rvalue = self._interface.query("SOUR:FUNC:SHAP?")
        if rvalue.endswith("\n"):
            rvalue = rvalue[:-1]
        rkey = None
        for key, value in self.shapes.iteritems():
            if value == rvalue:
                rkey = key
        return rkey


features = [
    FloatValue(
        "freq",
        doc="Frequency of output signal",
        command_get="SOUR:FREQ?",
        command_set="SOUR:FREQ",
        check_instrument_value=False,
    ),
    FloatValue(
        "vrms",
        doc="Set/get output amplitude (default to INF load)",
        command_get="SOUR:VOLT:UNIT VRMS\nSOUR:VOLT?",
        command_set="SOUR:VOLT:UNIT VRMS\nOUTP:LOAD INF\nSOUR:VOLT",
        check_instrument_value=False,
    ),
    FloatValue(
        "vdc",
        doc="Set/get output offset voltage (default is 0)",
        command_get="VOLT:OFFS?",
        command_set="OUTP:LOAD INF\nVOLT:OFFS",
        check_instrument_value=False,
    ),
    FloatValue(
        "load",
        doc="Get/Select the output termination",
        command_get="OUTP:LOAD?",
        command_set="OUTP:LOAD",
        check_instrument_value=False,
    ),
    HP33120a_ShapeValue(),
]

HP33120a._build_class_with_features(features)
