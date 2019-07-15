"""Control a galvanometer with a labjack daq (T7) (:mod:`fluidlab.objects.galvanometer`)
=========================================================================================

.. autosummary::
   :toctree:

.. autoclass:: Galva
   :members:

"""

from __future__ import print_function, division


from labjack import ljm

from fluidlab.daq.streaming_t7 import T7


serial_numbers = {"horiz": 470012356, "vert": 470012767}


class Galva:
    """Galvanometer which controls an oscillating mirror to set angles."""
    def __init__(self):
        self.t7 = T7(identifier=serial_numbers["horiz"])

    def set_angle(self, volt):
        """Set angle via labjack."""
        ljm.eWriteName(self.t7.handle, "DAC0", volt)

    def close(self):
        """Close T7 streaming."""
        self.t7.close()
