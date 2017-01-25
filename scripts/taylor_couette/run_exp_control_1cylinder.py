"""run_exp_control_1cylinder.py: run the "working" experiment.
--------------------------------------------------------------

"""

from __future__ import division, print_function

import numpy as np

from .str_path_working_exp import str_path

import fluiddyn as fld

from fluidlab.objects.rotatingobjects import (
    InnerCylinder, DaemonRunningRotatingObject
)

from fluidlab.exp.withconductivityprobe import DaemonMeasureProfiles

from fluidlab.util.gui import MainFrameRunExp




def run_exp(exp):

    # Omega_ramp = 0.2  # (rad/s)
    # T_ramp = 10*60  # (s)

    # Omega_oscillation = 0.8  # (rad/s)
    # T_oscillation = 4*60*60  # (s)

    # def rotation_rate_from_t(t):
    #     if t<T_ramp:
    #         return Omega_ramp*t/T_ramp
    #     else:
    #         return (Omega_ramp
    #                 + Omega_oscillation/2* (1 - np.cos(
    #                     2*np.pi*(t-T_ramp)/T_oscillation)))

    Omega_ramp = 0.25  # (rad/s)
    T_ramp = 20*60  # (s)

    Omega_max = 1.0  # (rad/s)
    T_ramp2 = 10*60*60  # (s)

    def rotation_rate_from_t(t):
        if t < T_ramp:
            return Omega_ramp*t/T_ramp
        elif t < T_ramp+T_ramp2:
            return Omega_ramp+(t-T_ramp)/T_ramp2*(Omega_max-Omega_ramp)
        elif t < T_ramp+2*T_ramp2:
            return Omega_max+(t-T_ramp-T_ramp2)/T_ramp2*(Omega_ramp-Omega_max)
        else:
            return Omega_ramp
                    
    Omega_max = exp.params['Omega1']
    def give_n_jump_by_modulo(t):
        rr = rotation_rate_from_t(t)/Omega_max
        if rr < 0.4:
            return 4
        elif rr < 0.7:
            return 2
        else:
            return 1


    T1 = 2*np.pi/exp.params['Omega1']
    period = 2*T1
    duration = 60*60*24

    inner_cylinder = InnerCylinder(rotation_rate=rotation_rate_from_t)
    daemon_ic = DaemonRunningRotatingObject(inner_cylinder)

    exp.sprobe.set_sample_rate(2000.)
    daemon_profiles = DaemonMeasureProfiles(
        exp=exp,
        duration=duration, period=period,
        deltaz=290,
        speed_measurements=100,
        speed_up=60,
        give_n_jump_by_modulo=give_n_jump_by_modulo)

    mainframe = MainFrameRunExp(exp=exp)
    mainframe.add_frame_object(exp.profiles, column=0, row=3)
    mainframe.add_frame_rotating_object(inner_cylinder, column=0, row=4)

    # should do that to avoid a bug in Windows
    def start_daemons():
        daemon_ic.start()
        daemon_profiles.start()
    mainframe.after(200, start_daemons)

    mainframe.mainloop()














if __name__ == '__main__':

    exp = fld.load_exp(
        str_path,
        position_start=301., Deltaz=290.
    )

    exp.save_script()

    run_exp(exp)


# hastoplot_Omega_vs_times = False
# if hastoplot_Omega_vs_times:
#     times = arange(0., 60*60*21)
#     Omega = np.array( [ rotation_rate_from_t(t) for t in times ] )
