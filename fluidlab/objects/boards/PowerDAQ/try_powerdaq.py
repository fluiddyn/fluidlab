
"""
This script tests the library powerdaq (minimal API from python).

output 0 should be plugged in input 0.
"""

from __future__ import division, print_function

import numpy as np
import time

from fluidlab.objects.boards.powerdaq import PowerDAQBoard
from fluidlab.createfigs import CreateFigs

SAVE_FIG = 0
import matplotlib.pyplot as plt


# initialize the board
board = PowerDAQBoard()

# prepare analogic output
frequency = 50.
tend = 5.2
nb_values = tend * frequency

dt = 1. / frequency
t = dt * (np.arange(nb_values) + 1)

# t = np.linspace(0, tend, nb_values)

period_signal = 1.
outcos = np.cos(2 * np.pi / period_signal * t)
outconst = np.ones(t.shape)
out0 = 6. * outcos

# prepare analogic input
channels = [1]
sample_rate = 10000
gain_channels = [1]

board.ain.configure(
    sample_rate,
    channels=channels,
    Cv_master=True,
    range10V=True,
    bipolar=False,
    gain_channels=gain_channels,
    differential=False,
)

# board.ain.configure(bipolar=False)

# sample_rate = 1000

board.ain.configure(  # sample_rate,
    # channels=channels,
    # gain_channels=gain_channels,
    bipolar=True
)


nb = tend * sample_rate
print("nb", nb)
print("sample_rate", sample_rate)


# Be carreful, the first point is not at t=0!
# tin = 1./sample_rate*(np.arange(nb)+1)


# t1 = time.clock()


# launch output and input
tout = board.aout(out0=out0, out1=None, frequency=frequency, return_times=True)

# t2 = time.clock()

tin, volts = board.ain(nb, return_times=True)

# t3 = time.clock()

# print('duration aout: {0}'.format(t2-t1))
# print('duration ain:  {0}'.format(t3-t2))


# print('in try_powerdaq, volts:', volts[0])


volts0 = volts[0].transpose()


fontsize = 20

create_figs = CreateFigs(SAVE_FIG=SAVE_FIG, FOR_BEAMER=False, fontsize=fontsize)

size_axe = [0.12, 0.14, 0.83, 0.8]
fig, ax1 = create_figs.figure_axe(
    name_file="fig_", fig_width_mm=190, fig_height_mm=150, size_axe=size_axe
)

ax1.set_xlabel(r"$t$")
ax1.set_ylabel(r"$U$ (V)")


t = tout

tplot = np.empty(len(t) * 2)
tplot[::2] = t
tplot[1:-1:2] = t[1:]
tplot[-1] = t[-1]

outplot = np.empty(len(t) * 2)
outplot[::2] = out0
outplot[1::2] = out0

lout = ax1.plot(t, out0, "-r")

ax1.plot(tplot, outplot, "--r")


lin = ax1.plot(tin, volts[0], "b.")

# ax1.set_xlim([0, tend])
# ax1.set_ylim([-2.5, 2.5])

leg1 = plt.figlegend(
    [lout[0], lin[0]], ["output", "input"], loc=(0.15, 0.15), labelspacing=0.2
)

create_figs.save_fig()
create_figs.show()
