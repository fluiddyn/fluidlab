"""RPi acquisition board MCP3008SPI (:mod:`fluidlab.objects.raspberrypi.daq`)
=============================================================================

"""

from __future__ import division, print_function

try:
    import spidev
except ImportError:
    pass

import time

class MCP3008SPI(object):
    """Analogic / digital conversion with the MCP3008 SPI ADC chip."""
    def __init__(self, differential=True):
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz = int(1e6) # Hz

        self.differential = differential
        if self.differential:
            self.bit_sgl_diff = 0
        else:
            self.bit_sgl_diff = 1

    def convert(self, channel=0):
        """Ask for a conversion on channel `channel`."""
        # we have to send 3 bytes:
        # byte1 = 0b00000001 (start bit)
        # byte2 = (1 bit coding for single-ended (=1) or differential
        # (=0), 3 bits coding the channel and 4 "don't care" bits)
        # byte3 = (8 "don't care" bits)
        data = [1]
        data.append(self.bit_sgl_diff << 7  |  ( ((channel & 0b111) << 4)))
        data.append(0)

        # print('second byte send: {:08b}'.format(data[1]))
        self.spi.xfer2(data)

        # the return value is coded on 10 bits contained in data[1:]
        return (data[1]<< 8) & 0b1100000000 | (data[2] & 0xff)





if __name__ == '__main__':

    a2d = MCP3008SPI(differential=False)

    for i in range(3):
        print('channel {:2d}:'.format(i), a2d.convert(i))

