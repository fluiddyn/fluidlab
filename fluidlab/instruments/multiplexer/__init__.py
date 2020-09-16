"""Multiplexers (:mod:`fluidlab.instruments.multiplexer`)
=========================================================

Provides:

.. autosummary::
   :toctree:

   agilent_34970a
   keithley_2700
   keithley_705
   lakeshore_224
   cryocon_24c

.. autoclass:: CurveFormat
   :members:
   :private-members:
   
.. autoclass:: CurveCoefficient
   :members:
   :private-members:

"""

from enum import IntEnum

__all__ = [
    "agilent_34970a",
    "keithley_2700",
    "lakeshore_224",
    "keithley_705",
    "cryocon_24c",
]

class CurveFormat(IntEnum):
    """Curve format used for sensor calibration curves in
    various multiplexers such as Lakeshore and Cryocon."""

    MILLIVOLT_PER_KELVIN = 1
    VOLT_PER_KELVIN = 2
    OHM_PER_KELVIN = 3
    LOGOHM_PER_KELVIN = 4


class CurveCoefficient(IntEnum):
    """Curve coefficient for sensor calibration curves in various
    multiplexers such as Lakeshore and Cryocon."""

    NEGATIVE = 1
    POSITIVE = 2