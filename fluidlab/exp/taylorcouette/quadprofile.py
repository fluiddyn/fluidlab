"""
IQS TC experiments (:mod:`fluidlab.exp.taylorcouette.linearprofile`)
========================================================================

.. currentmodule:: fluidlab.exp.taylorcouette.quadprofile

Provides:

.. autoclass:: IQSTaylorCouetteExp
   :members:
   :private-members:

"""

from __future__ import division, print_function

import numpy as np
import os


from fluidlab.exp.taylorcouette import TaylorCouetteExp, A, c

from fluidlab import load_exp
from fluiddyn.util.constants import g, rho0, rho_pure_water






class IQSTaylorCouetteExp(TaylorCouetteExp):
    r"""Initially quadratic stratification Taylor-Couette experiment.

    Parameters
    ----------
    (for the __init__ method)

    rho_min : number, optional
        Density minimum (in kg/m^3).

    rho_max : number, optional
        Density maximum (in kg/m^3).

    z_max : number, optional
        Total height (in mm).

    alpha : {1, number}, optional
        Non-dimensional number characterising the quadratic profile.

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

    The quadratic profile is:

    .. math:: 
        \frac{g\rho}{\rho_{mid0}} = 
        g - {N_{mid0}}^2 (z-H) (1+\alpha \frac{z}{H}),

    where :math:`z` is ??? and :math:`H` is ???.


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
    _base_dir = os.path.join('TaylorCouette', 'IQS')
    def __init__(self, 
                 rho_min=None, rho_max=None,
                 z_max=None,
                 alpha=1,
                 Omega1=None, Omega2=None,
                 R1=None, R2=261.,
                 description= None,
                 params=None,
                 str_path=None,
                 position_start=352., position_max=None, Deltaz=340.,
                 need_board=True
                 ):
        # start the init. and find out if it is the first creation
        self._init_from_str(str_path)
        if self.first_creation:
            # add a bit of description
            description_base = """
Initially quadratic stratification (IQS)...

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
            if z_max is not None:
                params['z_max'] = z_max
            if alpha is not None:
                params['alpha'] = alpha
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
                    'z_max', 'alpha',
                    'Omega1', 'Omega2','R1', 'R2']
            )

            # calculate the parameters needed for the inherited class
            Delta_rho = params['rho_max'] - params['rho_min']

            if z_max is None:
                z_max = params['z_max']
            Nmid0 = np.sqrt(g*Delta_rho/(rho0*z_max/1e3))

            if alpha is None:
                alpha = params['alpha']
            if alpha > 1 or alpha < -1:
                raise ValueError(
                    'alpha should be between -1 and 1')

            zs_norm = np.linspace(0, 1, 20)
            zs = z_max*zs_norm

            rhos = params['rho_min']*(
                1 - Nmid0**2/g*(zs-z_max)/1e3*(1+alpha*zs/z_max)
            )

            N0 = Nmid0*np.sqrt(1+alpha*(2*zs/z_max-1))

            params.update({
                'zs': zs, 
                'rhos': rhos,
                'Nmid0': Nmid0,
                'N0': N0
            })

        # call the __init__ function of the inherited class
        super(IQSTaylorCouetteExp, self).__init__(
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
        Then, update the instance variable `params` with the
        characteristic layer thickness :math:`h_l` corresponding to
        the heights zs (key "hls"), and some parameters characterising
        the profile at mid-height (Brunt-Vaisala frequency
        :math:`N_{mid0}`, Richardson number :math:`Ri` and
        characteristic layer thickness :math:`h_{mid}`.

        Parameters
        ----------
        params : dict
            Dictionary containing parameters.

        Notes
        -----
        .. math:: 

           {N_{mid0}}^2 = g \Delta\rho/(\rho_0 H)

           hmid = A\frac{U_c}{N_{mid0}} + c

           Rimid = R_2/U_1^2  N_0^2  h_l

           hls = A \frac{U_c}{N_0} + c

        """
        super(IQSTaylorCouetteExp, self)._create_self_params(params)

        if len(params) == 0:
            return

        R2 = self.params['R2']

        Uc = self.params['Uc']
        U1 = self.params['U1']
        Delta_rho = self.params['Delta_rho']

        zs = self.params['zs']

        Nmid0 = self.params['Nmid0']

        hmid = (A*Uc/Nmid0 + c) *1e3

        N0 = params['N0']

        hs = (A*Uc/N0 + c) *1e3

        Rimid = R2/U1**2 *Nmid0**2 *hmid *1e-6
        self.params.update({
            'hmid': hmid,
            'hls': hs,
            'Rimid': Rimid
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
        begin, end = super(IQSTaylorCouetteExp, self)._init_name_dir()

        self.name_dir = (
            begin+
            'Omega1={0:4.2f}_'.format(self.params['Omega1'])+
            'Nmid0={0:4.2f}_'.format(self.params['Nmid0'])+
            end)
        return begin, end





def prepareIQS(N0):

    Delta_rho_max = 0.14
    z_max = 0.480 # (m)

    Delta_rho = N0**2*rho0*z_max/g

    if Delta_rho > Delta_rho_max:
        Delta_rho = Delta_rho_max
        z_max = (Delta_rho/rho0) * (g/N0**2) *1000 # (mm)
    else:
        z_max *= 1000 # (mm)


    print("""
For Nmid0 = {0:5.2f}, 
Delta_rho: {1:5.2f}; z_max: {2:5.2f};
""".format(N0, Delta_rho, z_max)
)

    assert N0**2 == g/rho0 * Delta_rho/(z_max/1000)










def load_exp_and_measure_profils(str_path):

    exp = load_exp(str_path=str_path,
                   position_start=379., Deltaz=364.
    )

    T1 = 2*np.pi/exp.params['Omega']

    exp.sprobe.set_sample_rate(2000.)
    period = 2*T1
    duration = 60*60*30

    n_jump_by_modulo = np.array(
        [1, 1,   4,   4, 1, 1,   4,    4])
    ts_jump_by_modulo = np.array(
        [0, 0.5, 0.5, 5, 5, 5.5, 5.5, 48])*60*60

    exp.measure_profil(duration=duration, period=period, 
                       deltaz=362, speed_measurements=100, 
                       speed_up=60,
                       n_jump_by_modulo=n_jump_by_modulo,
                       ts_jump_by_modulo=ts_jump_by_modulo
    )

    exp.plot_profils()
    return exp









if __name__ == '__main__':

    # Nmid0 = 1.83 # (rad/s)
    # Omega = 0.73 # (rad/s)
    # R1 = 100. # (mm)

    # prepareIQS(Nmid0)

    # exp = IQSTaylorCouetteExp(Omega=Omega, R1=R1, 
    #                           rho_max=1.143, z_max=410, 
    #                           alpha=-0.7)

    str_path = 'Exp_Omega=0.73_Nmid0=1.85_2014-04-07_11-11-52'


    # exp = load_exp_and_measure_profils(str_path)



    exp = load_exp(str_path=str_path, 
                   need_board=False
                   # need_board=True
    )

    # exp.tank.profil.plot()

    # exp.tank.fill(pumps=True)


    tstart = 60*5

    times_slice = None
    exp.profiles.plot_2d(ind_file_profils=1, SAVE_FIG=False, 
                         times_slice=times_slice)


    times_slice = np.array([tstart, tstart+2*60, None])
    exp.profiles.plot(ind_file_profils=1, SAVE_FIG=False,
                      times_slice=times_slice)




    # exp.sprobe.set_sample_rate(200.)
    # exp.sprobe.measure(duration=0.1, VERBOSE=True)
    # exp.sprobe.measure(duration=0.1, VERBOSE=True)
    # exp.sprobe.measure(duration=2., VERBOSE=True)

    # exp.sprobe.plot_calibrations()


    # exp.sprobe.move(deltaz=40, speed=60, bloquing=True)
    # exp.sprobe.move(deltaz=500, speed=100, bloquing=True)




