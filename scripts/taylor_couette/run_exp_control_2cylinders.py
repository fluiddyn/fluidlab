"""run_exp_control_2cylinders.py: run the "working" experiment.
---------------------------------------------------------------

"""

from __future__ import division, print_function

# import numpy as np

from .str_path_working_exp import str_path

import fluiddyn as fld


from fluidlab.objects.rotatingobjects import (
    DaemonRunningRotatingObject,
    create_rotating_objects_pseudokepler
)

# from fluidlab.exp.withconductivityprobe import DaemonMeasureProfiles

from fluidlab.util.gui import MainFrameRunExp





def run_exp(exp):

    R1 = exp.params['R1']
    R2 = exp.params['R2']

    Omega_max = exp.params['Omega1']
    Tramp = 5*60  # (in s)

    def rotation_rate_from_t(t):
        if t<Tramp:
            return Omega_max*t/Tramp
        else:
            return Omega_max

    # def give_n_jump_by_modulo(t):
    #     rr = rotation_rate_from_t(t)/Omega_max
    #     if rr < 0.2:
    #         return 4
    #     elif rr < 0.4:
    #         return 2
    #     else:
    #         return 1

    gamma = 1.5

    inner_cylinder, rot_table = create_rotating_objects_pseudokepler(
        rotation_rate_from_t, R1, R2, gamma)

    daemon_ic = DaemonRunningRotatingObject(inner_cylinder)
    daemon_rt = DaemonRunningRotatingObject(rot_table)

    # T1 = 2*np.pi/exp.params['Omega1']
    # period = 2*T1
    # duration = 60*60*4

    # exp.sprobe.set_sample_rate(2000.)
    # daemon_profiles = DaemonMeasureProfiles(
    #     exp=exp,
    #     duration=duration, period=period,
    #     deltaz=330,
    #     speed_measurements=100,
    #     speed_up=60,
    #     give_n_jump_by_modulo=give_n_jump_by_modulo)


    mainframe = MainFrameRunExp(exp=exp)
    # mainframe.add_frame_object(exp.profiles, column=0, row=3)
    mainframe.add_frame_object(inner_cylinder, column=0, row=4)
    mainframe.add_frame_object(rot_table, column=0, row=5)

    # should do that to avoid a bug in Windows
    def start_daemons():
        daemon_ic.start()
        daemon_rt.start()
        # daemon_profiles.start()
    mainframe.after(100, start_daemons)

    mainframe.mainloop()














if __name__ == '__main__':

    exp = fld.load_exp(
        str_path,
        position_start=336., Deltaz=330.
    )

    exp.save_script()

    run_exp(exp)
