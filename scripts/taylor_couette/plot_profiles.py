"""plot_profiles.py: plot profiles of the "working" experiment.
---------------------------------------------------------------

See
:class:`fluidlab.exp.withconductivityprobe.ExpWithConductivityProbe`.

"""

from __future__ import division, print_function

import numpy as np

from str_path_working_exp import str_path

import fluiddyn as fld

if __name__ == '__main__':

    exp = fld.load_exp(str_path, need_board=False)


    tstart = 0
    times_slice = np.array([tstart, tstart+110*60, None])
    times_slice = np.array([0, 120*60, None])
    times_slice = None



    # exp.profiles.plot_2d(ind_file_profiles=-1, hastosave=False,
    #                      times_slice=times_slice)


    exp.profiles.plot(ind_file_profiles=[0, 1], hastosave=False,
                      times_slice=times_slice)
