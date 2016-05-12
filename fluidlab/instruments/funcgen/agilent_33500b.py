"""Agilent 33500b
=================

.. autoclass:: Agilent33500b
   :members:
   :private-members:

"""

__all__ = ['Agilent33500b']

from fluidlab.instruments.funcgen.agilent_33220a import Agilent33220a


class Agilent33500b(Agilent33220a):
    """Minimal implementation of a driver for the Agilent 33500B."""
    pass
