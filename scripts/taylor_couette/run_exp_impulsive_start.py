"""run_exp_impulsive_start.py: run the "working" experiment.
------------------------------------------------------------

"""

from __future__ import division, print_function

import numpy as np

from .str_path_working_exp import str_path

import fluiddyn as fld

from fluidlab.exp.withconductivityprobe import DaemonMeasureProfiles

from fluidlab.util.gui import MainFrameRunExp


def run_exp(exp):

    Omega1 = exp.params['Omega1']

    # def give_n_jump_by_modulo(t):
    #     tadim = t*Omega1
    #     if tadim < 100:
    #         return 4
    #     elif tadim < 400:
    #         return 2
    #     else:
    #         return 1

    give_n_jump_by_modulo = lambda x: 2

    T1 = 2*np.pi/Omega1
    period = 2*T1
    duration = 60*3

    # exp.sprobe.set_sample_rate(2000.)
    daemon_profiles = DaemonMeasureProfiles(
        exp=exp,
        duration=duration, period=period,
        deltaz=355,
        speed_measurements=60,
        speed_up=60,
        give_n_jump_by_modulo=give_n_jump_by_modulo)

    mainframe = MainFrameRunExp(exp=exp)
    mainframe.add_frame_object(exp.profiles, column=0, row=3)

    # should do that to avoid a bug in Windows
    mainframe.after(100, daemon_profiles.start)

    mainframe.mainloop()






if __name__ == '__main__':

    exp = fld.load_exp(
        str_path,
        position_start=371., Deltaz=355.
    )

    exp.save_script()

    run_exp(exp)
