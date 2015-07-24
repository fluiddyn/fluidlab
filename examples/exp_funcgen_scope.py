from __future__ import print_function, division

import numpy as np

from fluidlab.exp.session import Session
from fluiddyn.util.timer import Timer
from fluiddyn.output.figs import show


from fluidlab.instruments.scope.agilent_dsox2014a import AgilentDSOX2014a
from fluidlab.instruments.funcgen.tektronix_afg3022b import TektronixAFG3022b

total_time = 5.
time_step = 1.
omega = 2*np.pi/2.

# conversion volt into temperature (nothing physical, just for the example)
alpha = 0.01


# Initialization session, log, saving and emails
session = Session(
    path='./Tests',
    name='Exp_funcgen_scope',
    # email_to='pierre.augier@legi.cnrs.fr',
    # email_title='False experiment with function generator and oscilloscope',
    # email_delay=2*3600
)

print = session.logger.print_log
send_mail_if_has_to = session.logger.send_mail_if_has_to

data_table = session.get_data_table(
    fieldnames=['U0', 'U1', 'T0', 'T1'])

data_table.init_figure(['T0', 'T1'])


# set-up the function generator
funcgen = TektronixAFG3022b('USB0::1689::839::C034062::0::INSTR')
offset = 1.
funcgen.function_shape.set('sin')
funcgen.frequency.set(1e4)
funcgen.voltage.set(0.)
funcgen.offset.set(offset)
funcgen.output1_state.set(True)

# set-up the oscilloscope
scope = AgilentDSOX2014a('USB0::2391::6040::MY51450715::0::INSTR')
scope.channel1_coupling.set('DC')
scope.channel1_range.set(5.)
scope.timebase_range.set(1e-3)
scope.trigger_level.set(offset)


# initialization of the time loop
t_last_print = 0.
timer = Timer(time_step)
t = timer.get_time_till_start()

# start the time loop
while t < total_time:

    t = timer.get_time_till_start()
    volts_out = np.cos(omega*t) + 0.1*np.random.rand()

    funcgen.voltage.set(volts_out)

    time, volts = scope.get_curve(nb_points=200)

    U0 = volts.min()
    U1 = volts.max()

    data_table.add_data({'U0': U0, 'U1': U1,
                         'T0': alpha*U0, 'T1': alpha*U1})

    if t - t_last_print > 1 - time_step/2.:
        t_last_print = t
        print('time till start: {:8.5} s'.format(t))
        data_table.update_figures()

        # send_mail_if_has_to()

    timer.wait_till_tick()

print('last time: {:8.5} s'.format(t))
show()
