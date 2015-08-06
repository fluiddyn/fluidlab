from __future__ import print_function, division

import numpy as np

from fluidlab.exp import Session, Timer
from fluidlab.output import show

raise_error = False

# unless explicitly mentioned, FluidLab uses SI units, so the times are is s
total_time = 5.
time_step = 0.2
omega = 2*np.pi/2.

# conversion volt into temperature (nothing physical, just for the example)
alpha = 2.

# initialize session, log, saving and emails
session = Session(
    path='Tests',
    name='False_exp',
    # email_to='experimentalist@lab.earth',
    # email_title='False experiment without instrument',
    # email_delay=30  # time in s
)

print = session.logger.print_log
send_email_if_has_to = session.logger.send_email_if_has_to

data_table = session.get_data_table(
    fieldnames=['U0', 'U1', 'T0', 'T1'])

data_table.init_figure(['U0', 'U1'])


# initialization of the time loop
t_last_print = 0.
t = 0.
timer = Timer(time_step)

# start the time loop
while t < total_time:

    U0 = np.cos(omega*t) + 0.1*np.random.rand()
    U1 = U0 * np.random.rand()

    data_table.save({'U0': U0, 'U1': U1,
                     'T0': alpha*U0, 'T1': alpha*U1})

    if t - t_last_print > 1 - time_step/2.:
        t_last_print = t
        print('time till start: {:8.5} s'.format(t))
        data_table.update_figures()
        send_email_if_has_to()

    t = timer.wait_tick()

if raise_error:
    print("let's raise a ValueError to see what it gives.")
    raise ValueError('The flag raise_error is True...')

print('Time end: {:8.5} s'.format(t))

show()
