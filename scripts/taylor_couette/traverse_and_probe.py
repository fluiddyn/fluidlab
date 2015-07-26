"""traverse_and_probe.py: for moving the traverse and testing the probe.
------------------------------------------------------------------------

See :mod:`fluidlab.objects.traverse` and :mod:`fluidlab.objects.probes`.

"""

from __future__ import division, print_function

import numpy as np

from str_path_working_exp import str_path

import fluiddyn as fld

if __name__ == '__main__':

    exp = fld.load_exp(str_path)




    # exp.sprobe.set_sample_rate(200.)
    # exp.sprobe.measure(duration=0.1, VERBOSE=True)
    # exp.sprobe.measure(duration=0.1, VERBOSE=True)
    # exp.sprobe.measure(duration=2., VERBOSE=True)

    # exp.sprobe.plot_calibrations()


    # exp.sprobe.move(deltaz=-40, speed=60, bloquing=True)
    # exp.sprobe.move(deltaz=500, speed=100, bloquing=True)

    # exp.sprobe.test_measure(duration=4, rho_real=1.10784)
