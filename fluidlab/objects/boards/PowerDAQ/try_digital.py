
"""
This script tests the library powerdaq (minimal API from python).

output 0 should be plugged in input 0.
"""

from __future__ import division, print_function

import numpy as np
import time

from fluidlab.powerdaq import PowerDAQBoard
from fluidlab.timer import Timer

from fluidlab.createfigs import CreateFigs
SAVE_FIG = 0
import matplotlib.pyplot as plt

period = 2 # (s)


# initialize the board
board = PowerDAQBoard()

timer = Timer(period)

for i in xrange(5):
    time.sleep(1)
    board.dout.write(0)
    timer.wait_tick()
    board.dout.write(2)
