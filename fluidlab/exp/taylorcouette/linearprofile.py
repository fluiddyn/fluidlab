"""
ILS TC experiments (:mod:`fluidlab.exp.taylorcouette.linearprofile`)
========================================================================

.. currentmodule:: fluidlab.exp.taylorcouette.linearprofile

Provides:

.. autoclass:: ILSTaylorCouetteExp
   :members:
   :private-members:

"""

from __future__ import division, print_function

import os
import numpy as np

from fluidlab.exp.taylorcouette import TaylorCouetteExp, A, c
from fluiddyn.util import load_exp
from fluiddyn.util.constants import g, rho0, rho_pure_water

class ILSTaylorCouetteExp(TaylorCouetteExp):
    """Initially linear stratification Taylor-Couette experiment.

    Parameters
    ----------
    (for the __init__ method)

    rho_min : number, optional
        Density minimum (in kg/m^3).

    rho_max : number, optional
        Density maximum (in kg/m^3).

    N0 : number, optional
        Brunt-Vaisala frequency (in rad/s).

    prop_homog : {0, number}, optional
        Proportion of the height that is homogeneous.

    Omega1 : number
        Rotation rate of the inner cylinder (in rad/s).

    Omega2 : {0., number}
        Rotation rate of the outer cylinder (in rad/s).

    R1 : number
        Radius of the inner cylinder (in mm).

    R2 : {261, number}
        Radius of the outer cylinder (in mm).

    params : dict, optional
        Contain parameters. The previously listed parameters can be
        given directly in this dictionary. Other parameters can be
        added and will also be saved.

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

    Examples
    --------

    Create an experiment::

        exp = ILSTaylorCouetteExp(Omega1=Omega1, R1=R1,
            rho_max=rho_max, N0=N0, prop_homog=prop_homog,
            description='''The tank is slowly put into rotation with a
            linear ramp during 1 hour to Omega_max = 0.75 rad/s.''')

    Fill the tank::

        str_path = 'Exp_Omega=0.75_N0=1.83_2014-05-16_09-20-32'
        exp = fld.load_exp(str_path=str_path)
        exp.tank.fill(pumps=True)

    """
    _base_dir = os.path.join('TaylorCouette', 'ILS')
    def __init__(self, 
                 rho_min=None, rho_max=None,
                 N0=None, prop_homog=None,
                 Omega1=None, Omega2=None,
                 R1=None, R2=None,
                 description=None, params=None,
                 str_path=None,
                 position_start=352., position_max=None, Deltaz=340.,
                 need_board=True
    ):
        # start the init. and find out if it is the first creation
        self._init_from_str(str_path)

        if self.first_creation:
            # add a bit of description
            description_base = """
Initially linear stratification (ILS)...

"""
            description = self._complete_description(
                description_base, description=description)

            # initialise `params` with `params` and the other parameters
            if params is None:
                params = {}
            if rho_min is None:
                if 'rho_min' in params:
                    rho_min = params['rho_min']
                else:
                    rho_min = rho_pure_water
            params['rho_min'] = rho_min
            if rho_max is not None:
                params['rho_max'] = rho_max
            if N0 is not None:
                params['N0'] = N0
            if prop_homog is not None:
                params['prop_homog'] = prop_homog
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
                keys_needed=[
                    'rho_min', 'rho_max', 
                    'N0', 'prop_homog',
                    'Omega1', 'Omega2','R1', 'R2']
            )

            # calculate the parameters needed for the inherited class
            Delta_rho = params['rho_max'] - params['rho_min']
            if prop_homog is None:
                prop_homog = params['prop_homog']

            zs_norm = np.array(  [0, prop_homog/2, 1-prop_homog/2, 1])
            rhos_norm = np.array([1., 1.,   0.,   0.])
            if N0 is None:
                N0 = params['N0']
            z_max = g*Delta_rho/(rho0*N0**2*(1-prop_homog))*1000 # (mm)

            zs = z_max*zs_norm
            rhos = rho_min + Delta_rho*rhos_norm

            params.update({
                'zs':zs, 
                'rhos':rhos
            })

        # call the __init__ function of the inherited class
        super(ILSTaylorCouetteExp, self).__init__(
            params=params,
            description=description, 
            str_path=str_path,
            position_start=position_start, 
            position_max=position_start, Deltaz=Deltaz,
            need_board=need_board
            )








    def _create_self_params(self, params):
        r"""Calculate some parameters.

        First, call the inherited function `_create_self_params`.
        Then,  Then, update the instance variable
        `params` with the Brunt-Vaisala frequency :math:`N_0`, the
        characteristic layer thickness :math:`h_l` and the Richardson
        number :math:`Ri`.

        Parameters
        ----------
        params : dict
            Containing parameters.

        Notes
        -----
        .. math:: 

           {N_0}^2 = \frac{g \Delta\rho}{\rho_0 (z[2] - z[1])},

           h_l = A \frac{U_c}{N_0} + c,

           Ri_N = \frac{R_2 N_0^2  h_l}{U_1^2},

           R_b = \left( \frac{L_b}{L_\nu} \right) = \frac{A^2 {\Omega_i}^3
           R_1 \Delta R}{\nu N^2},

        where :math:`L_\nu = \nu/\Omega_i` and :math:`L_b = \Omega_i
        \sqrt{R_1 \Delta R} / N_0`.



        """
        super(ILSTaylorCouetteExp, self)._create_self_params(params)

        if len(params) == 0:
            return

        R2 = self.params['R2']

        Uc = self.params['Uc']
        U1 = self.params['U1']
        Delta_rho = self.params['Delta_rho']

        zs = params['zs']

        if Delta_rho == 0:
            N0 = 0.
        else:
            N0 = np.sqrt(g*Delta_rho/(rho0* (zs[2] - zs[1])/1e3))

        hl = (A*Uc/N0 + c) *1e3
        Ri_N = R2/U1**2 *N0**2 *hl *1e-6

        R1, nu, Omega1 = (self.params[k] for k in ['R1', 'nu', 'Omega1'])
        Rb = A**2 * Omega1**3 * R1* (R2-R1) *1e-6  / (nu*N0**2)

        self.params.update({
            'N0':N0,
            'hl':hl,
            'Ri_N':Ri_N,
            'Rb':Rb
        })





    def _init_name_dir(self):
        """Init the name of the directory where the data are saved.

        Initialise as `begin+infos+end` and return (`begin`,
        `end`). To see what is `infos`, look at the code.

        Returns
        -------
        begin : str
            equal to `'Exp_'`.
        end : str
            coding the time of creation.

        """
        begin, end = super(ILSTaylorCouetteExp, self)._init_name_dir()

        self.name_dir = (
            begin+
            'Omega1={0:4.2f}_'.format(self.params['Omega1'])+
            'N0={0:4.2f}_'.format(self.params['N0'])+
            end)
        return begin, end












if __name__ == '__main__':
    pass












