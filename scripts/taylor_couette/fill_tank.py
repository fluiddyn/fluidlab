"""fill_tank.py: fill the tank of the "working" experiment.
-----------------------------------------------------------

See :mod:`fluidlab.objects.tanks`.

"""
from __future__ import division, print_function

from str_path_working_exp import str_path

import fluiddyn as fld

if __name__ == '__main__':
    exp = fld.load_exp(str_path, need_board=False)

    exp.tank.fill(pumps=True)
