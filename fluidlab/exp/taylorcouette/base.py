r"""
TC experiments (:mod:`fluidlab.exp.taylorcouette.base`)
===========================================================

.. currentmodule:: fluidlab.exp.taylorcouette.base

Provides:

.. autoclass:: TaylorCouetteExp
   :members:
   :private-members:



Physical notes on Taylor-Couette flows
--------------------------------------




Boussinesq approximation
^^^^^^^^^^^^^^^^^^^^^^^^

The equation of Navier-Stokes can be written as

.. |bnabla| mathmacro:: \boldsymbol{\nabla}
.. |vv| mathmacro:: \textbf{v}
.. |Dt| mathmacro:: \mbox{D}_t
.. |xx| mathmacro:: \textbf{x}

.. math:: \rho \Dt \vv
   = - \bnabla P + \rho\textbf{g} + \eta \bnabla^2 \vv,
   :label: eq1

where |vv| is the velocity and |bnabla| is the pressure gradient.

where :math:`\eta` is the dynamic viscosity.

The Boussinesq approximation is based on the decomposition
:math:`\rho(\xx,t) = \rho_0 + \tilde \rho(\xx,t)` and on the
conditions :math:`\tilde \rho(\xx,t)\ll \rho_0` (and also in practice
:math:`\Dt \tilde \rho \ll 1)`. These inequalities have the
consequence that the conservation of mass can be written as
:math:`\bnabla \cdot \vv = 0`.

By dividing the equation for the velocity vector by :math:`\rho_0`, we
get exactly

.. math::

   \Dt \vv + \frac{\tilde\rho}{\rho_0} \Dt \vv = -\bnabla \tilde p +
   \frac{\tilde\rho}{\rho_0} \textbf{g} + \nu \bnabla^2 \vv,

where :math:`\nu = \eta/\rho_0` and :math:`\tilde p = P/\rho_0 + gz`.
We stress that we have only rewritten equation :eq:`eq1` with
no approximation.










Parameters characterising the geometry and the cinetic of the cylinders
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The geometry is characterized by the ratio :math:`\eta_i = R_i/R_o`. The
movement of the cylinders is characterised by the ratio :math:`\mu_o =
\Omega_o/\Omega_i`.


Laminar solution
^^^^^^^^^^^^^^^^

For the laminar solution, the velocity is

.. math::
   v(r) = A r + \frac{B}{r}

where

.. math::
   A = \frac{\Omega_i}{1-{\eta_i}^2} (\mu_o - {\eta_i}^2), \quad
   B = \frac{\Omega_i}{1-{\eta_i}^2} {R_i}^2 (1 - \mu_o),

which can be rewritten as :math:`v(r) = \Omega(r) r`, with

.. math::
   \Omega(r) = \frac{\Omega_i}{1-{\eta_i}^2}
   \left[  (\mu_o - {\eta_i}^2)
   + \left(\frac{R_i}{r}\right)^2 (1-\mu_o)  \right].




Centrifugal instability, Rayleigh condition and quasi-Kepler rotation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If :math:`d_r ( \Omega(r) r^2 ) <0`, the flow is unstable to the centrifugal
instability. For the laminar solution, this condition known as the
Rayleigh condition can be written as :math:`{\eta_i}^2 > \mu_o`,


For spherical trajectory, the rotational rate of light objects
rotating around a heavy one is related to the radius of the trajectory
as :math:`\Omega^2 r^3 = GM` (simple version of the Kepler law).  If
the rotations of the two cylinders of a Taylor-Couette are related
with the Kepler scaling, :math:`{\Omega_i}^2 {R_i}^3 = {\Omega_o}^2
{R_o}^3`, we have :math:`\mu_o = {\eta_i}^{3/2}`. This is a
quasi-Kepler Taylor-Couette flow.  Since :math:`\eta_i<1`, we have
:math:`{\eta_i}^2 < \mu_o = {\eta_i}^{3/2}`, which implies that
this flow is not unstable to the centrifugal instability.



"""

from __future__ import division, print_function

import numpy as np
import os

from fluiddyn.util.constants import g, rho0, nu_pure_water

from fluidlab.exp.withconductivityprobe import ExpWithConductivityProbe

from fluidlab.objects.tanks import TaylorCouette


A = 0.215
c = 0.009  # (m)


class TaylorCouetteExp(ExpWithConductivityProbe):
    """Represent Taylor-Couette experiments with a stratified fluid.

    Parameters
    ----------
    (for the __init__ method)

    zs : array_like, optional
        Position array (in mm).

    rhos : array_like, optional
        Density array (in kg/m^3).

    Omega1 : number
        Rotation rate of the inner cylinder (in rad/s).

    Omega2 : {0., number}
        Rotation rate of the outer cylinder (in rad/s).

    R1 : number
        Radius of the inner cylinder (in mm).

    R2 : {261, number}
        Radius of the outer cylinder (in mm).

    params : dict, optional
        Contain parameters (`rhos` and `zs` can be given in this
        dictionary. Other parameters can be added and will also be
        saved.)

    description : str, optional
        A description of the experiment.

    str_path : str, optional
        A string related to the path where the experiment is saved
        or will be saved.

    Notes
    -----
    There are two modes of creating an instance of this class:

    1. if `str_path` doesn't point on an already saved experiment, a
       new experiment is created (the instance variable
       `first_creation` is True). In this case, the parameters `rhos`
       or `zs` have to be given (either directy or through the
       dictionary `params`).

    2. if `str_path` points on an already saved experiment, the instance
       variable `first_creation` is False and the experiment is loaded.

    Note that if you want to load an already saved experiment, it is
    more convenient to use the function :func:`fluiddyn.load_exp` like
    so::

        exp = fld.load_exp('2014-03-25_12-43-48')

    Attributes
    ----------
    board : :class:`fluidlab.board.PowerDAQBoard`
        For controlling the acquisition board.
    sprobe : :class:`fluidlab.objects.probes.MovingConductivityProbe`
        For controlling the conductivity probe and the traverse.
    profiles : :class:`fluidlab.exp.withconductivityprobe.Profiles`
        For profiles...

    tank : :class:`fluidlab.objects.tanks.TaylorCouette`
        Contains the informations on the tank and the density profile.
    first_creation : bool
        False if the experiment has not been loaded from the disk.
    params : dict
        Containing parameters.
    description : str
        A description of the experiment..
    path_save : str
        The absolute path of the directory associated with the experiment.
    name_dir : str
        Name of the directory associated with the experiment.
    time_start : str
        Coding the time of creation.

    """
    _base_dir = os.path.join('TaylorCouette', 'Base')

    def __init__(self,
                 zs=None, rhos=None,
                 Omega1=None, Omega2=None,
                 R1=None, R2=None,
                 params=None,
                 description=None,
                 str_path=None,
                 position_start=352., position_max=None, Deltaz=340.,
                 need_board=True
                 ):

        # start the init. and find out if it is the first creation
        self._init_from_str(str_path)

        if self.first_creation:
            # add a bit of description
            description_base = """
Experiment in a Taylor-Couette.

This tank is 520 mm high. The radius of the outer cylinder is
approximately {:5.0f} mm.

""".format(R2 or params['R2'])
            description = self._complete_description(
                description_base, description=description)

            # initialise `params` with `params` and the other parameters
            if params is None:
                params = {}
            if rhos is not None:
                params['rhos'] = rhos
            if zs is not None:
                params['zs'] = zs
            if Omega1 is not None:
                params['Omega1'] = Omega1
            if Omega2 is not None:
                params['Omega2'] = Omega2
            if R1 is not None:
                params['R1'] = R1
            if R2 is not None:
                params['R2'] = R2

            # verify if enough params have been given for the first creation
            self._verify_params_first_creation(
                params,
                keys_needed=['rhos', 'zs', 'Omega1', 'Omega2', 'R1', 'R2']
            )

        # call the __init__ function of the inherited class
        super(TaylorCouetteExp, self).__init__(
            params=params,
            description=description,
            str_path=str_path,
            position_start=position_start,
            position_max=position_start, Deltaz=Deltaz,
            need_board=need_board)


    def _create_self_params(self, params):
        r"""Calculate some parameters.

        First, call the function `_create_self_params` of the
        inherited class.  Then, update the instance variable `params`
        with the rotation rates :math:`\Omega_1` and :math:`\Omega_2`,
        the rotation rate ratio :math:`\mu_o = \Omega_o/\Omega_i`, the
        radii :math:`R_1` and :math:`R_2`, the radius ratio
        :math:`\eta_i = R_i/R_o`, the gap :math:`\Delta R = R_2 -
        R_1`, the velocities of the surface of the inner and outer
        cylinders :math:`U_1=\Omega_1 R_1` and :math:`U_2=\Omega_2
        R_2`, the characteristic velocity :math:`U_c`, the (inner)
        Reynolds number :math:`Re` and the Taylor number
        :math:`Ta`. We also compute the outer, the shear and the mean
        Reynolds numbers, :math:`Re_s`, :math:`Re_s` and :math:`Re_m`,
        respectively.

        Parameters
        ----------
        params : dict
            Dictionary containing parameters.

        Notes
        -----
        .. math::

           U_c = U_1\sqrt{\Delta R/R_1},

           Re = \frac{U_1 \Delta R}{\nu},

           Ta = \frac{2 \Delta R}{(R_1+R_2)^2}  Re^2,

           Re_o = \frac{U_2 \Delta R}{\nu},

           Re_s = Re_o - Re_i,

           Re_m = (Re_o + Re_i)/2,

           Ri = \frac{g\Delta\rho R_2}{\rho_0{U_1}^2}.

        """
        super(TaylorCouetteExp, self)._create_self_params(params)

        if len(params) == 0:
            return

        zs = params['zs']
        zmax = zs[-1] - zs[0]

        try:
            Omega1 = params['Omega1']
            Omega2 = params['Omega2']
        except KeyError:
            Omega1 = params['Omega']
            Omega2 = 0.
            self.params['Omega1'] = Omega1
            self.params['Omega2'] = Omega2

        mu_o = Omega2/Omega1

        R1 = params['R1']
        R2 = params['R2']

        if R1 not in [50, 100, 150]:
            raise ValueError('Are you sure of the value of R1?')

        eta_i = R1/R2
        DeltaR = R2 - R1
        Gamma = zmax/DeltaR

        U1 = R1*Omega1 *1e-3  # (m/s)
        U2 = R2*Omega2 *1e-3  # (m/s)
        Uc = np.sqrt(DeltaR/R1)*U1

        nu = self.params['nu']
        Re = U1*DeltaR/nu *1e-3
        Ta = 2*DeltaR/(R1+R2)**2 * Re**2 *1e3

        Re_o = U2*DeltaR/nu_pure_water *1e-3
        Re_s = Re - Re_o
        Re_m = (Re_o + Re)/2

        Delta_rho = self.params['Delta_rho']
        Ri = g*Delta_rho/rho0 *R2*1e-3 / U1**2

        self.params.update({
            'mu_o': mu_o,
            'eta_i': eta_i,
            'DeltaR': DeltaR,
            'Gamma': Gamma,
            'U1': U1, 'U2': U2,
            'Uc': Uc,
            'Re': Re,
            'Ta': Ta,
            'Re_o': Re_o,
            'Re_s': Re_s,
            'Re_m': Re_m,
            'Ri': Ri
        })









    def _create_tank(self):
        """Create the instance variable representing the tank.

        Here, `tank` represents a Taylor-Couette tank
        (:class:`fluidlab.objects.tanks.TaylorCouette`).

        """
        # print(self.params)
        if 'R1' in self.params:
            R1 = self.params['R1']
        else:
            R1 = 100.

        if 'R2' in self.params:
            R2 = self.params['R2']
        else:
            R2 = 261.

        if 'H' in self.params:
            H = self.params['H']
        else:
            H = 520.

        if 'zs' in self.params:
            zs = self.params['zs']
            rhos = self.params['rhos']
        else:
            zs = [0, H]
            rhos = [1.2, 1.]

        self.tank = TaylorCouette(Rin=R1, Rout=R2, H=H,
                                  z=zs, rho=rhos)












def create_exp(rho_max=1.146, z_max=400):

    rho_min = 1.
    Delta_rho = rho_max - rho_min

#     zs_norm = np.array([0, 1./6, 5./6, 1])
#     rhos_norm = np.array([1., 0.5, 0.5, 0.])
#     description = """
# Profil: strong linear stratification at the bottom and
# top. Unstratified in the middle.

# """

    zs_norm = np.array(  [0,  1./4, 1./2, 1./2, 3./4, 1])
    rhos_norm = np.array([1., 1.,   2./3, 1./3, 0.,   0.])
    description = """
Profil: two homogeneous layers at the bottom and top; two layers with
a linear stratification and a step in the middle.

Filling with a sponge to decrease the mixing in the tank (as Megan).

Quite large flow rate: flowrate_tot = 0.8*pumps.flow_rates_max.min()

Moreover, the volume in the tube between the pumps and the tank is
taken into account.

"""

    zs = z_max*zs_norm
    rhos = rho_min + Delta_rho*rhos_norm
    exp = TaylorCouetteExp(zs=zs, rhos=rhos, description=description)

    return exp








def load_exp_and_measure_profiles(str_path):

    exp = load_exp(str_path=str_path,
                   position_start=374., Deltaz=362.
    )
    exp.sprobe.set_sample_rate(2000.)

    period = 2*T1
    duration = 60*60*30

    n_jump_by_modulo = np.array(
        [1, 1,   4,   4, 1, 1,   4,    4])
    ts_jump_by_modulo = np.array(
        [0, 0.5, 0.5, 5, 5, 5.5, 5.5, 48])*60*60

    exp.profiles.measure(duration=duration, period=period,
                         deltaz=362, speed_measurements=100,
                         speed_up=60,
                         n_jump_by_modulo=n_jump_by_modulo,
                         ts_jump_by_modulo=ts_jump_by_modulo
    )

    exp.profiles.plot()
    return exp









if __name__ == '__main__':

    Omega1 = 1.

    exp = TaylorCouetteExp(
        rhos=[1.1, 1], zs=[0, 200], Omega1=Omega1, R1=150)


    # exp = create_exp()

    # str_path = 'Exp_Omega=0.73_N0=1.83_2014-03-25_12-43-48'

    # exp = load_exp_and_measure_profiles(str_path)

    # exp = load_exp(str_path=str_path,
    #                need_board=False
    #                # need_board=True
    # )


    # exp.tank.fill(pumps=True)


    # times_minmax = np.array([0*60, 10*60])+60*300
    # times_minmax = None
    # exp.profiles.plot_2d(ind_file_profiles=1, SAVE_FIG=False,
    #                      times_minmax=times_minmax)

    # exp.profiles.plot(ind_file_profils=1, SAVE_FIG=False,
    #                   times_minmax=times_minmax)



    # exp.sprobe.set_sample_rate(200.)
    # exp.sprobe.measure(duration=0.1, VERBOSE=True)
    # exp.sprobe.measure(duration=0.1, VERBOSE=True)
    # exp.sprobe.measure(duration=2., VERBOSE=True)

    # exp.sprobe.plot_calibrations()


    # exp.sprobe.move(deltaz=40, speed=60, bloquing=True)
    # exp.sprobe.move(deltaz=500, speed=100, bloquing=True)
