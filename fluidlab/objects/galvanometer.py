"""Control a galvanometer with a labjack daq (T7)
=================================================


"""

from __future__ import print_function, division


from labjack import ljm

from fluidlab.instruments.daq.streaming_t7 import T7


serial_numbers = {"horiz": 470012356, "vert": 470012767}


try:
    input = raw_input
except NameError:
    pass


class Galva(object):

    def __init__(self):
        self.t7 = T7(identifier=serial_numbers["horiz"])

    def set_angle(self, volt):
        ljm.eWriteName(self.t7.handle, "DAC0", volt)

    def close(self):
        self.t7.close()
