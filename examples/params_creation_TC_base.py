"""params_creation_TC_base.py: parameters for creation of an TaylorCouetteExp
-----------------------------------------------------------------------------

This file is imported by create_exp_TC_lin.py and should be
modified. It should be run to test the consistency of the parameters.

"""
from __future__ import division, print_function

import numpy as np

import fluiddyn as fld



def Omega2_pseudo_keplerian(Omega1, R1, R2, gamma):
    """Return the Omega2 computed using the Kepler scaling law.

    Parameters
    ----------
    gamma : number
        Coefficient for scaling law.

    Note
    ----
    .. math:: \mu_o = {\eta_i}^\gamma

"""
    eta_i = R1 / R2
    mu_o = eta_i**gamma
    return mu_o*Omega1


def Omega2_Kepler(Omega1, R1, R2):
    """Return the Omega2 computed using the Kepler scaling law."""
    return Omega2_pseudo_keplerian(Omega1, R1, R2, gamma=3/2)


# geometry and kinetic:
R1 = 100.  # (mm)
R2 = 240.  # (mm)

Omega1 = 1.  # (rad/s)
Omega2 = 0.0  # (rad/s)
# gamma = 3/2
# Omega2 = Omega2_pseudo_keplerian(Omega1, R1, R2, gamma=gamma)

# stratification:
rho_min = 1.0338  # fld.constants.rho_pure_water
rho_max = 1.1031

# 3 regions:
# zs_norm = np.array(  [0., 1/3, 2/3, 1.])
# rhos_norm = np.array([1., 1/2, 1/2, 0.])
# constant N:
# zs_norm = np.array(  [0., 1.])
# rhos_norm = np.array([1., 0.])
# 2 homogeneous layers:
zint = 142./299.5
zs_norm = np.array(  [0., zint, zint, 1.])
rhos_norm = np.array([1.,  1.,  0., 0.])

z_max = 299.5
zs = z_max*zs_norm
Delta_rho = rho_max - rho_min
rhos = rho_min + Delta_rho*rhos_norm

# particular description for this experiment
description="""
I2L experiment

Only the inner cylinder rotates (Omega1_max = {:5.2f} rad/s).

- Short ramp of 10 min up to 0.2 rad/s.

- sinusoidal variation between 0.2 and 1. rad/s with a period of 4 hours.

The lid is fixed to the outer cylinder.

""".format(Omega1)
