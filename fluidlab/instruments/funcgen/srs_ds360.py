"""Stanford Research System DS360
=================================

.. autoclass:: SrsDs360
   :members:
   :private-members:


"""

__all__ = ["StanfordDS360"]

from fluidlab.instruments.iec60488 import (
    IEC60488,
    PowerOn,
    Calibration,
    Trigger,
    ObjectIdentification,
    StoredSetting,
)


from fluidlab.instruments.features import (
    FloatScientificValue,
    FloatValue,
    BoolValue,
)


class StanfordDS360(
    IEC60488, PowerOn, Calibration, Trigger, ObjectIdentification, StoredSetting
):
    """
    A driver for the ultra low distorsion wave generator DS360


    """


features = [
    FloatScientificValue(
        "vrms",
        doc="RMS voltage of generated wave (can be zero)",
        channel_argument=True,
        command_set="AMPL {value:.2e} VR",
        command_get="AMPL?VR",
    ),
    FloatScientificValue(
        "vdc",
        doc="Offset voltage of generated wave",
        channel_argument=True,
        command_set="OFFS {value:.2e}",
        command_get="OFFS?",
    ),
    FloatValue(
        "frequency",
        doc="Frequency of generated wave",
        command_set="FREQ",
        command_get="FREQ?",
    ),
    BoolValue(
        "onoff", doc="Output ON/OFF", command_set="OUTE", command_get="OUTE?"
    ),
    BoolValue(
        "balanced",
        doc="Output mode (balanced or unbalanced)",
        command_set="OUTM",
        command_get="OUTM?",
    ),
]

StanfordDS360._build_class_with_features(features)
