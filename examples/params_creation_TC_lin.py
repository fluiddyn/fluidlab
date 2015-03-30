"""params_creation_TC_lin.py: parameters for creation of an ILSTaylorCouetteExp
-------------------------------------------------------------------------------

This file is imported by create_exp_TC_lin.py and should be
modified. It should be run to test the consistency of the parameters.

"""
from __future__ import division, print_function

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


_Delta_rho_max = 0.15

# geometry and kinetic:
R1 = 100.  # (mm)
R2 = 240.  # (mm)

Omega1 = 1.  # (rad/s)
Omega2 = 0.0 # (rad/s)
# Omega2 = Omega2_pseudo_keplerian(Omega1, R1, R2, gamma=1/2)

# stratification:
N0 = 1.8  # (rad/s)
prop_homog = 0.1
zmax = 340.46  # (mm)

# value that should be computed by running this script.
rho_max = 1.0992

rho_min = fld.constants.rho_pure_water
Delta_rho = rho_max - rho_min

# particular description for this experiment
description="""

The tank is slowly put into rotation with a linear ramp during 0.5
hours to Omega_max = {:5.2f} rad/s. The rotating table is also slowly
put in rotation such as the ratio Omega2/Omega1 is constant and the
two rotation rates are always related with the Kepler law.

The lid is fixed to the outer cylinder.

It is another Colin's experiment with a pretty low Reynolds number and the
largest Richardson number that we can get.

gamma = 1/2

The stratification was produced for another experiment:

Exp_Omega1=0.40_N0=2.20_2014-09-29_16-48-34

""".format(Omega1)



# For verification of consistency

rho0 = fld.constants.rho0
g = fld.constants.g


def verify_params_computing_deltarho(N0, prop_homog=0.1, zmax=480.):
    """Prepare an experiment by computing parameters.

    Compute the difference of density *Delta_rho* from *N0*,
    *prop_homog* and *zmax*.

    Parameters
    ----------

    N0 : number
       The Brunt-Vaisala frequency (rad/s).

    prop_homog : number, optional
       A number meaning the proportion of height homogeneous.

    zmax : number, optional
       The maximum height (mm).

    """

    Deltaz = zmax*(1-prop_homog)
    Delta_rho = rho0* N0**2/g *(Deltaz/1000)

    if Delta_rho > _Delta_rho_max:
        Delta_rho = _Delta_rho_max
        Deltaz = (Delta_rho/rho0) * (g/N0**2) *1000  # (mm)
        zmax = Deltaz/(1-prop_homog)

    assert 1 - g * Delta_rho/rho0 / (Deltaz/1000) / N0**2 < 1e-8

    return Delta_rho, zmax


def verify_params_computing_zmax(N0, prop_homog, rhomax):
    Delta_rho = rhomax - rho_min
    Deltaz = g/rho0 * Delta_rho/N0**2
    zmax = Deltaz/(1-prop_homog) * 1000
    return zmax



Delta_rho_new, zmax_new = verify_params_computing_deltarho(
    N0, prop_homog, zmax)

consistent = (
    abs(1 - Delta_rho/Delta_rho_new) < 1e-4
    and
    abs(1 - zmax/zmax_new) < 1e-4)

zmax_new2 = verify_params_computing_zmax(N0, prop_homog, rho_max)




if __name__ == '__main__':

    if Delta_rho_new == _Delta_rho_max and Delta_rho_new != Delta_rho:
        print(
"""
For these parameters (N0, prop_homog and zmax), Delta_rho would
be larger than Delta_rho_max, we have to fix Delta_rho to
Delta_rho_max ({:.2f} g/cm^3) and to compute the value of zmax that
leads to the wanted N0.
""".format(_Delta_rho_max))

    print("""
To get 
    N0: {:5.4f} rad/s 
    prop_homog: {:5.2f}

we can have:
    zmax: {:5.2f} mm
    Delta_rho: {:8.6f} g/cm^3
or
    Delta_rho: {:8.6f} g/cm^3
    zmax: {:5.2f} mm
""".format(N0, prop_homog, 
           zmax_new, Delta_rho_new, 
           Delta_rho, zmax_new2))



    if consistent:
        print('Delta_rho seems consistent with the other parameters.')
    else:
        print("""
For Delta_rho = {:8.6f} g/cm^3
rho_max = {:8.6f} g/cm^3 
if rho_min = {:8.6f} g/cm^3 
        """.format(Delta_rho_new, rho_min+Delta_rho_new, rho_min))

        print("""
For Delta_rho = {:8.6f} g/cm^3
rho_max = {:8.6f} g/cm^3 
if rho_min = {:8.6f} g/cm^3 
        """.format(Delta_rho, rho_min+Delta_rho, rho_min))

        print(
"""Warning: You should modify params_for_creation.Delta_rho and/or
params_for_creation.zmax to obtain the wanted parameters.""")


