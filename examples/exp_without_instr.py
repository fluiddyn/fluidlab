from __future__ import print_function, division

import numpy as np

from fluidlab.exp.session import Session
from fluiddyn.util.timer import Timer


nb_changes = 10
period = 2.

volt_min = 0.1
volt_max = 3.

volts_out = np.linspace(volt_min, volt_max, nb_changes)

# conversion volt into temperature (nothing physical, just for the example)
alpha = 2.


# Initialization session, log, saving and emails
session = Session(
    path='Tests',
    # name='False_exp',
    # email_to='pierre.augier@legi.cnrs.fr',
    # email_title='False experiment without instrument',
    # email_delay=2*3600
)

print = session.logger.print_log

data_table = session.get_data_table(
    fieldnames=['U0', 'U1', 'T0', 'T1'])

data_table.init_figure(['U0', 'U1'])
data_table.init_figure(['T0', 'T1'])


# start the time loop
timer = Timer(period)
for it in range(nb_changes):

    Umin = it*2
    Umax = it*3

    data_table.save({'U0': Umin, 'U1': Umax,
                     'T0': alpha*Umin, 'T1': alpha*Umax})

    if it % 2 == 0:
        print('it: {:3d}, time till start: {:8.5} s'.format(
            it, timer.get_time_till_start()))
        data_table.update_figures()

    if it < nb_changes-1:
        timer.wait_till_tick()
