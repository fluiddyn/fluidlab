"""Tanks (:mod:`fluidlab.objects.tanks`)
========================================

.. _tanks:
.. currentmodule:: fluidlab.objects.tanks

.. todo:: Solve a bug loading the tank (about values Rin, Rout...).

Provides:

.. autoclass:: DensityProfile
   :members:

.. autoclass:: Surface
   :members:

.. autoclass:: StratifiedTank
   :members:

.. autoclass:: TaylorCouette
   :members:

"""

from __future__ import division, print_function

import numpy as np

import os
import h5py

import fluiddyn.output.figs as figs

from fluiddyn.util.signal import FunctionLinInterp
import fluiddyn.util.query as query
from fluiddyn.util.timer import Timer

from fluidlab.objects.pumps import MasterFlexPumps


class DensityProfile(FunctionLinInterp):
    """Represent the density profile as a function of the height.

    Parameters
    ----------
    z : array_like
        Position.

    rho : array_like
        Surface.

    Attributes
    ----------
    z: `numpy.ndarray`
        Position.

    rho: `numpy.ndarray`
        Density profile.

    """
    def __init__(self, z, rho):
        super(DensityProfile, self).__init__(z, rho)
        if any([r1 < r2 for r1, r2 in zip(rho, rho[1:])]):
            raise ValueError("rho must decrease!", rho)
        self.z = np.array(z, dtype=float)
        self.rho = np.array(rho, dtype=float)

    def plot(self):
        """Plot the density profile."""
        figures = figs.Figures()
        fig = figures.new_figure(
            name_file='fig_function',
            fig_width_mm=190, fig_height_mm=150,
            size_axe=[0.13, 0.16, 0.84, 0.76]
        )
        ax = fig.gca()

        ax.set_xlabel(r'$\rho$')
        ax.set_ylabel(r'$z$ (mm)')
        ax.plot(self.rho, self.z, 'k-.')

        figs.show()


class Surface(FunctionLinInterp):
    """Represent the surface as a function of the height.

    Parameters
    ----------
    z : array_like
        Position.

    S : array_like
        Surface.

    Attributes
    ----------
    z: `numpy.ndarray`
        Position.

    S: `numpy.ndarray`
        Surface.

    """
    def __init__(self, z, S):
        super(Surface, self).__init__(z, S)
        self.z = np.array(z, dtype=float)
        self.S = np.array(S, dtype=float)


class StratifiedTank(object):
    """Represent a tank with a density profile.

    Parameters
    ----------
    H : {520, number}, optional
        Height (in mm).

    S : {100, number}, optional
        Surface (in mm).

    dico_profile : dict, optional
        Characteristics of the profile.

    pumps : :class:`fluidlab.objects.pumps.MasterFlexPumps`
        Represent the pumps.

    str_path : str
        Related to the path of the associated directory.

    """

    def __init__(self, H=520, S=100,
                 z=None, rho=None,
                 dico_profile=None,
                 pumps=None,
                 str_path=None):

        if str_path is None:
            self._create(H, S, z, rho, dico_profile)
        else:
            self._load(str_path)
            self.S = self.surface.S[0]

        self.z_max = self.profile.x.max()
        self._compute_volume()
        self.volume_mliter = self.volume / 1e3

        if pumps is not None:
            self.pumps = pumps

    def _compute_volume(self):
        """Initialise the instance variable `volume`."""
        self.volume = self.S*self.z_max

    def _create(self, H, S, z, rho, dico_profile):
        """Initialisation."""
        self.H = float(H)
        self.S = float(S)

        self.surface = Surface([0, self.H], [self.S, self.S])

        if z is None and rho is None:
            self.dico_profile = dico_profile
            if dico_profile['keyword'].startswith('linear'):
                z, rho = self._compute_linear_profile()
            elif dico_profile['keyword'].startswith('step'):
                z, rho = self._compute_step_profile()
            elif dico_profile['keyword'].startswith('homo_middle'):
                z, rho = self._compute_homo_middle()
            else:
                raise ValueError('error value for dico_profile')

        self.profile = DensityProfile(z, rho)

    def _compute_linear_profile(self):
        """Compute a linear profile."""
        z_max = self.dico_profile['z_max']
        rho_max = self.dico_profile['rho_max']
        rho_min = self.dico_profile['rho_min']
        try:
            depth_homo = self.dico_profile['depth_homo']
        except KeyError:
            depth_homo = 0
        z = [0, depth_homo, z_max-depth_homo, z_max]
        rho = [rho_max, rho_max, rho_min, rho_min]
        return z, rho

    def _compute_step_profile(self):
        """Compute a step profile."""
        z_max = self.dico_profile['z_max']
        rho_max = self.dico_profile['rho_max']
        rho_min = self.dico_profile['rho_min']
        hstep = self.dico_profile['hstep']
        z = [0, hstep, hstep, z_max]
        rho = [rho_max, rho_max, rho_min, rho_min]
        return z, rho

    def _compute_homo_middle(self):
        """Compute a profile with a homogeneous layer."""
        z_max = self.dico_profile['z_max']
        rho_max = self.dico_profile['rho_max']
        rho_min = self.dico_profile['rho_min']
        depth_strat = self.dico_profile['depth_strat']
        z = [0, depth_strat, z_max-depth_strat, z_max]
        rho_middle = (rho_max+rho_min)/2
        rho = [rho_max, rho_middle, rho_middle, rho_min]
        return z, rho

    def save(self, path_save):
        """Save in a file tank.h5"""

        if not path_save.endswith('.h5'):
            path_h5_file = path_save + '/tank.h5'

        if os.path.exists(path_h5_file):
            raise ValueError('The file already exists.')

        with h5py.File(path_h5_file, 'w') as f:
            f.attrs['class_name'] = self.__class__.__name__
            f.attrs['module_name'] = self.__module__
            f.attrs['H'] = self.H
            f.attrs['volume_mliter'] = self.volume_mliter

            group1 = f.create_group('surface')

            group1.create_dataset('z', data=self.surface.z)
            group1.create_dataset('S', data=self.surface.S)

            group2 = f.create_group('profile')
            group2.create_dataset('z', data=self.profile.z)
            group2.create_dataset('rho', data=self.profile.rho)

    def _load(self, str_path):
        """Load from a file tank.h5"""
        if not str_path.endswith('tank.h5'):
            path_h5_file = os.path.join(str_path, 'tank.h5')
        else:
            path_h5_file = str_path

        if not os.path.exists(path_h5_file):
            raise ValueError('The file does not exists.')

        with h5py.File(path_h5_file, 'r') as f:
            self.H = f.attrs['H']
            self.volume_mliter = f.attrs['volume_mliter']

            group = f['surface']
            z = group['z'][...]
            S = group['S'][...]
            self.surface = Surface(z, S)

            group = f['profile']
            z = group['z'][...]
            rho = group['rho'][...]
            self.profile = DensityProfile(z, rho)

    def fill(self, dt=1, pumps=False, hastoplot=True, vol_tube=142.):
        """Fill the tank.

        Parameters
        ----------
        dt : {2, number}, optional
            Time interval (in s) between the change of flow rate.

        pumps : {False, :class:`fluidlab.objects.pumps.MasterFlexPumps`}, optional
            If False, an instance is created.

        hastoplot : {True, False}, optional
            if True, plot the density profile.

        Notes
        -----

        Warning: I would advice not to use the "quick-edit option" of
        the command prompt in Windows since when you click on the
        command prompt window, a charactere is selected and when any
        characteres are selected, the output (and the program!) is
        frozen. This is unbelivable how bug-generating is it! Attaboy
        Windows!

        """

        if isinstance(pumps, (bool)):
            PUMP = pumps
            pumps = MasterFlexPumps(nb_pumps=2)
        elif isinstance(pumps, MasterFlexPumps):
            PUMP = True

        if not PUMP:
            print("""
Warning: can not fill without pumps. It will only perform a test of
the filling. To really fill the tank, set argument pumps to True or to
an instance of class MasterFlexPumps.\n""")
        else:
            to_print = ("""
Warning: Before really fill the tank, the tube have to be filled with
the correct density profile. During the filling of the tube, put the
end of the tube out of the tank. Are you ready?""")
            if not query.query_yes_no(to_print):
                return

        vol_to_pump = self.volume_mliter + vol_tube
        flowrate_tot = 0.8*pumps.flow_rates_max.min()  # (ml/min)
        time_fill = vol_to_pump/flowrate_tot

        print('flowrate_tot: {0:6.2f} ml/min'.format(flowrate_tot))
        print('vol_to_pump: {0:6.2f} ml'.format(vol_to_pump))
        print('time for the filling: {0:5.2f} min'.format(time_fill))

        rhomin = np.min(self.profile.rho)
        rhomax = np.max(self.profile.rho)

        dt_min = dt/60  # (min)
        dvolume = dt_min*flowrate_tot  # (ml)

        t = 0
        vol_pumped = 0

        z_fluid_injected = self.z_max

        h_pumped = 0
        tube_filled = False

        lh_pumped = []
        lrho = []
        lrho_test = []
        lflowrate_rhomax = []

        if PUMP:
            pumps.go()

        timer = Timer(dt)
        while vol_pumped < vol_to_pump - dvolume:

            dh = (dvolume*1e3  # (mm^3)
                  / self.surface(z_fluid_injected)  # (mm^2)
                  )  # (mm)
            h_pumped += dh

            z_fluid_injected = self.z_max - h_pumped

            if z_fluid_injected < 0:
                z_fluid_injected = 0

            rho_fluid_injected = self.profile(z_fluid_injected)

            flowrate_rhomax = (flowrate_tot
                               * (rho_fluid_injected - rhomin)
                               / (rhomax - rhomin)
                               )  # (ml)
            flowrate_rhomin = flowrate_tot - flowrate_rhomax  # (ml)

            if PUMP:
                pumps.set_flow_rate([flowrate_rhomin, flowrate_rhomax])

            rho_test = ((rhomax*flowrate_rhomax + rhomin*flowrate_rhomin)
                        / flowrate_tot)

            t += dt
            vol_pumped += dvolume

            lh_pumped.append(h_pumped)
            lrho.append(rho_fluid_injected)
            lrho_test.append(rho_test)
            lflowrate_rhomax.append(flowrate_rhomax)

            if PUMP:
                timer.wait_tick()

            print('volume pumped / volume to pump = {0:5.4f}'.format(
                vol_pumped/vol_to_pump), end='\r')

            if vol_pumped >= vol_tube and not tube_filled and PUMP:
                tube_filled = True
                pumps.stop()
                to_print = ("""
Now the tube should be filled with the correct density profile. You can
put the end of the tube in the tank! Are you ready?""")
                if not query.query_yes_no(to_print):
                    return
                pumps.go()

        if PUMP:
            pumps.stop()

        print('\nThe filling is finished.')

        if hastoplot:

            h = np.array(lh_pumped)
            t = dt*np.arange(0., len(lh_pumped))
            t /= 60  # (min)

            rho = np.array(lrho)
            rho_test = np.array(lrho_test)
            # flow_rhomax = np.array(lflowrate_rhomax)

            # plot
            figures = figs.Figures()
            size_axe = [0.13, 0.16, 0.84, 0.76]

            fig = figures.new_figure(
                name_file='fig_rho_t',
                fig_width_mm=190, fig_height_mm=150,
                size_axe=size_axe
            )
            ax = fig.gca()

            ax.set_xlabel(r'$\rho$')
            ax.set_ylabel(r'$t$ (min)')
            ax.plot(rho, t, 'k-.')
            ax.plot(rho_test, t, 'r-.')

            fig = figures.new_figure(
                name_file='fig_rho_h',
                fig_width_mm=190, fig_height_mm=150,
                size_axe=size_axe
            )
            ax = fig.gca()

            ax.set_xlabel(r'$\rho$')
            ax.set_ylabel(r'$h$ (mm)')
            ax.plot(rho, h, 'k-.')
            ax.plot(rho_test, h, 'r-.')

            figs.show()


class TaylorCouette(StratifiedTank):
    """Represent a Taylor-Couette tank."""
    def __init__(self,
                 Rin=100, Rout=240, H=520,
                 z=None, rho=None,
                 dico_profile=None,
                 str_path=None):

        self.Rin = Rin
        self.Rout = Rout
        super(TaylorCouette,
              self).__init__(H=H,
                             S=np.pi*(self.Rout**2 - self.Rin**2),
                             z=z, rho=rho,
                             dico_profile=dico_profile,
                             str_path=str_path)


def test_profiles():

    rho_max = 1.084
    rho_min = 1.
    Delta_rho = rho_max - rho_min

    z_max = 500.
    S = 300.

    tankL = StratifiedTank(
        H=z_max+10, S=S,
        dico_profile={'keyword': 'linear',
                      'z_max': z_max, 'depth_homo': 50,
                      'rho_max': rho_max, 'rho_min': rho_min})
    tankS = StratifiedTank(
        H=z_max+10, S=S,
        dico_profile={'keyword': 'step',
                      'z_max': z_max, 'hstep': 200,
                      'rho_max': rho_max, 'rho_min': rho_min})

    tankH = StratifiedTank(
        H=z_max+10, S=S,
        dico_profile={'keyword': 'homo_middle',
                      'z_max': z_max, 'depth_strat': 50,
                      'rho_max': rho_max, 'rho_min': rho_min})

    zs = z_max*np.array([0, 1./3, 2./3, 1])
    rhos = rho_min + Delta_rho*np.array([1., 0.5, 0.5, 0.])

    tank_test = StratifiedTank(H=z_max+10, S=80**2,
                               z=zs, rho=rhos)

    # plot
    figures = figs.Figures()
    fig = figures.new_figure(
        name_file='fig_strat_tank',
        fig_width_mm=190, fig_height_mm=150,
        size_axe=[0.12, 0.19, 0.84, 0.76]
    )
    ax = fig.gca()

    ax.set_xlabel(r'density')
    ax.set_ylabel(r'$z$')

    ax.plot(tankL.profile.rho, tankL.profile.z, 'ko:')
    ax.plot(tankS.profile.rho, tankS.profile.z, 'ro:')
    ax.plot(tankH.profile.rho, tankH.profile.z, 'yo:')

    ax.plot(tank_test.profile.rho, tank_test.profile.z, 'go:')

    for z in np.arange(0, z_max, 10):
        ax.plot(tankL.profile(z), z, 'ks')
        ax.plot(tankS.profile(z), z, 'rs')
        ax.plot(tankH.profile(z), z, 'ys')

        ax.plot(tank_test.profile(z), z, 'ys')

    ax.set_xlim([0.95, 1.2])

    figs.show()


def test_save():

    rho_max = 1.084
    rho_min = 1.
    Delta_rho = rho_max - rho_min

    z_max = 400
    zs = z_max*np.array([0, 1./6, 5./6, 1])
    rhos = rho_min + Delta_rho*np.array([1., 0.5, 0.5, 0.])

    tank = TaylorCouette(Rin=300, Rout=520, z=zs, rho=rhos)

    # tank = StratifiedTank(H=z_max, S=80**2, z=zs, rho=rhos)

    tank.save(os.getcwd())

    return tank


def test_load():

    return TaylorCouette(str_path=os.getcwd())

    # return StratifiedTank(str_path=os.getcwd())


if __name__ == "__main__":

    # test_profiles()
    # tank = test_save()

    tank = test_load()
