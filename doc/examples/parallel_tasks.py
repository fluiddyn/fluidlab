"""This example demonstrates how we can launch independent daemons to
perform tasks in parallel.

It produces the following output (all times are in seconds):

Daemons launched!
loop dt = 0.100, t = 0.00000
loop dt = 0.025, t = 0.00000
loop dt = 0.025, t = 0.02514
loop dt = 0.025, t = 0.05015
loop dt = 0.025, t = 0.07510
loop dt = 0.100, t = 0.10018
loop dt = 0.025, t = 0.10010
loop dt = 0.025, t = 0.12509
loop dt = 0.025, t = 0.15013
loop dt = 0.025, t = 0.17510
end of loop dt = 0.100, t = 0.20019
end of loop dt = 0.025, t = 0.20009
End of the script

"""
from time import sleep

from fluidlab.exp import Timer

# We can use processes or threads...
from fluiddyn.util.daemons import DaemonProcess as Daemon
# from fluiddyn.util.daemons import DaemonThread as Daemon


def make_loop_function(dt, total_time):
    def loop():
        timer = Timer(dt)
        t = 0
        while t < total_time:
            print('loop dt = {:5.3f}, t = {:7.5f}'.format(dt, t))
            t = timer.wait_tick()
        print('end of loop dt = {:5.3f}, t = {:7.5f}'.format(dt, t))
    return loop


total_time = 0.2

daemons = []
for dt in [0.1, 0.025]:
    loop = make_loop_function(dt, total_time)
    daemons.append(Daemon(loop))

for daemon in daemons:
    daemon.start()

print('Daemons launched!')
sleep(total_time + 0.02)
print('End of the script')
