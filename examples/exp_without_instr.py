from __future__ import print_function, division

import numpy as np

from fluidlab.exp.session import Session
from fluiddyn.util.timer import Timer
from fluiddyn.output.figs import show

total_time = 5.
time_step = 0.1
omega = 2*np.pi/2.

# conversion volt into temperature (nothing physical, just for the example)
alpha = 2.


# Initialization session, log, saving and emails
session = Session(
    path='./Tests',
    name='False_exp',
    # email_to='pierre.augier@legi.cnrs.fr',
    # email_title='False experiment without instrument',
    # email_delay=30
)

print = session.logger.print_log
send_mail_if_has_to = session.logger.send_mail_if_has_to

data_table = session.get_data_table(
    fieldnames=['U0', 'U1', 'T0', 'T1'])

data_table.init_figure(['U0', 'U1'])


# initialization of the time loop
t_last_print = 0.
timer = Timer(time_step)
t = timer.get_time_till_start()

# start the time loop
while t < total_time:

    t = timer.get_time_till_start()

    U0 = np.cos(omega*t) + 0.1*np.random.rand()
    U1 = U0 * np.random.rand()

    data_table.save({'U0': U0, 'U1': U1,
                     'T0': alpha*U0, 'T1': alpha*U1})

    if t - t_last_print > 1 - time_step/2.:
        t_last_print = t
        print('time till start: {:8.5} s'.format(t))
        data_table.update_figures()

        # send_mail_if_has_to()

    timer.wait_till_tick()

print('last time: {:8.5} s'.format(t))

show()
