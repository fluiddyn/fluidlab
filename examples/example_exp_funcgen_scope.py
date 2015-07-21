from __future__ import print_function, division

import numpy as np

from fluidlab import Session
from fluiddyn.util.timer import Timer

from fluidlab.instruments.scope.agilent_dsox2014a import AgilentDSOX2014a
from fluidlab.instruments.funcgen.tektronix_afg3022b import TektronixAFG3022b


nb_changes = 10
period = 2.

volt_min = 0.1
volt_max = 3.

volts_out = np.linspace(volt_min, volt_max, nb_changes)

# conversion volt into temperature (nothing physical, just for the example)
alpha = 0.01


# Initialization session, log, saving and emails
session = Session(
    path='Tests',
    name='',
    email_to='pierre.augier@legi.cnrs.fr',
    email_title='False experiment with function generator and oscilloscope',
    email_delay=2*3600)

print = session.print_log

# data_table = session.get_data_table()
# data_table.init_plot(['Umin', 'Umax'], num_fig=1)
# data_table.init_plot(['T1', 'T2'], num_fig=2)


# set-up the function generator
funcgen = TektronixAFG3022b('USB0::1689::839::C034062::0::INSTR')

offset = 1.

funcgen.function_shape.set('sin')
funcgen.frequency.set(1e4)
funcgen.voltage.set(volts_out[0])
funcgen.offset.set(offset)
funcgen.output1_state.set(True)


# set-up the oscilloscope
scope = AgilentDSOX2014a('USB0::2391::6040::MY51450715::0::INSTR')

scope.channel1_coupling.set('DC')
scope.channel1_range.set(volts_out.max())
scope.timebase_range.set('1e3')
scope.trigger_level.set(offset)


# start the time loop
timer = Timer(period)
for it in range(nb_changes):

    funcgen.voltage.set(volts_out[it])

    time, volts = scope.get_curve(nb_points=200)
    # we have to divide by 2 because of impedance issues
    volts /= 2

    Umin = volts.min()
    Umax = volts.max()

    # data_table.add_data({'Umin': Umin, 'Umax': Umax,
    #                      'T1': alpha*Umin, 'T2': alpha*Umax})

    # for fig in data_table.figures:
    #     fig.draw()

    if it < nb_changes-1:
        timer.wait_till_tick()
