
from time import time

from fluidlab.instruments.powersupply.isotech_ips2303s import IsoTechIPS2303S
from fluidlab.exp import Timer

voltage_max = 8

pwrsupply = IsoTechIPS2303S()

print('Initialize the device ' + pwrsupply.query_identification())
pwrsupply.set_output_state(False)
pwrsupply.iset1.set(0.3)
pwrsupply.iset2.set(0.3)
pwrsupply.vset1.set(0.)
pwrsupply.vset2.set(voltage_max)
pwrsupply.set_output_state(True)


def switch(channel):
    volt = channel.get()
    if volt > 0:
        volt = 0
    else:
        volt = voltage_max
    channel.set(volt)

time_step = 2.
total_time = 20.

print('Loop during total_time = {:7.5} s'.format(total_time))
t = 0.
timer = Timer(time_step)
tstart = timer.tstart
while t < total_time:
    print('time till start: {:7.5} s'.format(t))

    switch(pwrsupply.vset1)
    switch(pwrsupply.vset2)

    t = timer.wait_tick()

print('time at the end: {:7.5} s'.format(time() - tstart))
pwrsupply.set_output_state(False)
