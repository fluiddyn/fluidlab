"""
I2L TC experiments (:mod:`fluidlab.exp.taylorcouette.twolayers`)
====================================================================

.. currentmodule:: fluidlab.exp.taylorcouette.twolayers

Provides:

.. autoclass:: I2LTaylorCouetteExp
   :members:
   :private-members:

"""

from __future__ import division, print_function

import numpy as np
import os


from fluidlab.exp.taylorcouette import TaylorCouetteExp, A, c
from fluiddyn.util import load_exp
from fluiddyn.util.constants import g, rho0, rho_pure_water





class I2LTaylorCouetteExp(TaylorCouetteExp):
    """Initially two layers Taylor-Couette experiment.

    Parameters
    ----------
    (for the __init__ method)

    rho_min : number, optional
        Density minimum (in kg/m^3).

    rho_max : number, optional
        Density maximum (in kg/m^3).

    zmax : {300, number}, optional
        Depth (in mm).

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

    """
    _base_dir = os.path.join('TaylorCouette', 'I2L')
    def __init__(self, 
                 rho_min=None, rho_max=None,
                 z_max=300.,
                 Omega1=None, Omega2=0,
                 R1=None, R2=261.,
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
Initially two layers (I2L)...

"""
            description =self._complete_description(
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
            if z_max is not None:
                params['z_max'] = z_max
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
                    'z_max',
                    'Omega1', 'Omega2','R1', 'R2']
            )

            # calculate the parameters needed for the inherited class
            Delta_rho = params['rho_max'] - params['rho_min']

            zs_norm = np.array(  [0, 1./2, 1./2, 1])
            rhos_norm = np.array([1., 1.,   0.,   0.])

            zs = params['z_max']*zs_norm
            rhos = params['rho_min'] + Delta_rho*rhos_norm

            params.update({
                'zs':zs, 
                'rhos':rhos
            })

        # call the __init__ function of the inherited class
        super(I2LTaylorCouetteExp, self).__init__(
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
        Then, calculate the Richardson number :math:`Ri` and update
        the variable `params`.

        Parameters
        ----------
        params : dict
            Dictionary containing parameters.

        Notes
        -----
        .. math::  Ri = \frac{R_2}{{U_1}^2}  \frac{g \Delta \rho}{\rho_0}


        """
        super(I2LTaylorCouetteExp, self)._create_self_params(params)

        if len(params) == 0:
            return

        R2 = self.params['R2']
        U1 = self.params['U1']
        Delta_rho = self.params['Delta_rho']
        rhos = self.params['rhos']

        Ri = R2*1e-3/U1**2 *g*Delta_rho/rhos.min()

        self.params.update({
            'Ri':Ri
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
        begin, end = super(I2LTaylorCouetteExp, self)._init_name_dir()

        self.name_dir = (
            begin+
            'Omega1={0:4.2f}_'.format(self.params['Omega1'])+
            end)
        return begin, end






period_rr = 60*60
Omega1_max=2.
Tramp = period_rr/2


def rotation_rate_from_t(t):
    t = t%period_rr
    if t<Tramp:
        return Omega1_max*t/Tramp
    else:
        return Omega1_max*(1 - (t-Tramp)/Tramp)





def give_n_jump_by_modulo(t):
    
    rr = rotation_rate_from_t(t)/Omega1_max
    if rr < 0.1:
        return 4
    elif rr < 0.3:
        return 2
    else: return 1






def load_exp_and_measure_profiles(str_path, daemon=None):

    exp = load_exp(str_path=str_path,
                   position_start=314., Deltaz=285.
    )
    exp.sprobe.set_sample_rate(2000.)

    T1 = 2*np.pi/exp.params['Omega1']
    period = 2*T1
    duration = 60*60*48

    if daemon is not None:
        daemon.start()
        inner_cylinder = daemon.ro
    else:
        inner_cylinder = None

    exp.profiles.measure(duration=duration, period=period, 
                         deltaz=284, speed_measurements=100, 
                         speed_up=60,
                         give_n_jump_by_modulo=give_n_jump_by_modulo,
                         inner_cylinder=inner_cylinder
    )

    if daemon is not None:
        daemon.stop()

    exp.plot_profiles()
    return exp




if __name__ == '__main__':

    str_path = 'Exp_Omega=1.00_2014-05-14_10-45-50'


    exp = load_exp(str_path=str_path,
                   need_board=False
                   # need_board=True
    )

    # exp.tank.profile.plot()

