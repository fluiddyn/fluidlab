from __future__ import division, print_function

import fluiddyn as fld

from fluidlab.objects.rotatingobjects import (
    create_rotating_objects_pseudokepler
)

from str_path_working_exp import str_path

exp = fld.load_exp(str_path, need_board=False)

R1 = exp.params['R1']
R2 = exp.params['R2']

Omega_max = exp.params['Omega1']

Tramp = 20*60


def rotation_rate_from_t(t):
    if t < Tramp:
        return Omega_max*(1-t/Tramp)
    else:
        return 0

gamma = 1/2


inner_cylinder, rotating_table = create_rotating_objects_pseudokepler(
    rotation_rate_from_t, R1, R2, gamma)
