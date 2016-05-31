"""
Exp with a conductivity probe (:mod:`fluidlab.exp.withconductivityprobe`)
==============================================================================

.. currentmodule:: fluidlab.exp.withconductivityprobe

Provides:

.. autoclass:: ExpWithConductivityProbe
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: Profiles
   :members:
   :private-members:

"""

from __future__ import division, print_function

import numpy as np
import os

import datetime
import time

import glob
import h5py
import matplotlib.pyplot as plt

import fluiddyn as fld

from fluiddyn.io.hdf5 import H5File

from fluiddyn.util import time_as_str
from fluiddyn.util.signal import decimate
from fluiddyn.util.timer import Timer

from fluiddyn.output.util import gradient_colors

from fluidlab.exp.withtank import ExperimentWithTank

from fluidlab.objects.boards import PowerDAQBoard
from fluidlab.objects.probes import MovingConductivityProbe

import fluiddyn.output.figs as figs


from fluiddyn.util.daemons import DaemonThread as Daemon


class DaemonMeasureProfiles(Daemon):
    def __init__(self, exp, **kargs):
        super(DaemonMeasureProfiles, self).__init__()
        self._exp = exp
        self.kargs = kargs

    def run(self):
        self._exp.profiles.measure(**self.kargs)


class Profiles(object):
    """Represent a set of profiles.

    Parameters
    ----------
    (for the __init__ method)

    exp : :class:`ExpWithConductivityProbe`
        An object representing an experiment with a conductivity probe.

    Attributes
    ----------
    _exp : :class:`ExpWithConductivityProbe`
        The associated experiment.
    path_save : str
        The absolute path of the directory associated with the experiment.
    sprobe : :class:`fluidlab.objects.probes.MovingConductivityProbe`
        For controlling the conductivity probe and the traverse.

    """
    def __init__(self, exp):
        self.name = 'Profiles'
        self._exp = exp
        self.path_save = os.path.join(exp.path_save, self.name)

    def measure(self, duration, period=60,
                deltaz=300, speed_measurements=40,
                speed_up=10,
                give_n_jump_by_modulo=None,
                inner_cylinder=None):
        """Measure some density profiles.

        Parameters
        ----------
        duration : number
            The total duration of the measurement.

        period : {600, number}, optional
            Period between the ticks.

        deltaz=300, optional
            Distance by which the probe is moved.

        speed_measurements : {40, number}, optional
            Speed during the measurements

        speed_up : {10, number}, optional
            Speed when the probe come back to its initial place.

        give_n_jump_by_modulo : {None, function}, optional
            Function of time returning an integer equal to one plus
            the number of "periods" skipped (for which no profile is
            measured).

        inner_cylinder : {None, :class:`fluidlab.objects.rotatingobject.RotatingObject`}, optional
            Object representing a rotating inner cylinder. Is given to
            obtain and save the rotation rate when a profile is saved.

        """

        # just for developing and testing
        try_without_probe = False

        if give_n_jump_by_modulo is None:
            give_n_jump_by_modulo = lambda x: 1

        if inner_cylinder is None:
            rotation_rate = None

        time_probe_moving = deltaz*(1./speed_measurements+1./speed_up)
        if time_probe_moving > period:
            raise ValueError(
                'period is too short. time_probe_moving: '+
                '{0:5.2f} s'.format(time_probe_moving))

        path_dir =self.path_save

        if not os.path.exists(path_dir):
            os.mkdir(path_dir)

        path_file = (path_dir+'/profiles_'+time_as_str()+'.h5')

        deltaz = abs(deltaz)
        with h5py.File(path_file, 'w') as f:
            f.attrs['time start'] = str(datetime.datetime.now())
            f.attrs['name_dir'] = self._exp.name_dir
            f.attrs['speed_measurements'] = speed_measurements
            f.attrs['speed_up'] = speed_up
            try:
                f.attrs['sample_rate'] = self._exp.sprobe.sample_rate
                f.attrs['pos_start'] = self._exp.sprobe.position
            except AttributeError as e:
                if not try_without_probe:
                    fld.io._write_warning(
                        'Warning:\    '
                        'Using the flag try_without_probe '
                        'in withconductivityprobe.py.')
                    raise e

        nb_loops = int(duration/period)

        if nb_loops == 0:
            raise ValueError('duration < period !')

        self.write(
            'total duration for the measurements: {0:8.1f} min'.format(
                float(nb_loops)*period/60))

        t0 = time.time()
        timer = Timer(period)
        for il in range(nb_loops):
            time_now = time.time()
            time_since_start = time_now-t0
            n_jump_by_modulo = int(give_n_jump_by_modulo(time_since_start))

            if il % n_jump_by_modulo == 0:

                if inner_cylinder is not None:
                    rotation_rate = inner_cylinder.rotation_rate

                self.write(
                    'index profile loop: {0:5d} ;  '.format(il)+
                    'time - t0: '+
                    str(datetime.timedelta(seconds=time_since_start)))

                try:
                    self._exp.sprobe.valve.open()
                    time.sleep(1.0)
                    profile = self._exp.sprobe.move_measure(
                        deltaz=-deltaz,
                        speed=speed_measurements)
                    self._exp.sprobe.move(deltaz=deltaz, speed=speed_up)
                    self.save_one(
                        path_file, profile, time_since_start, rotation_rate)
                except AttributeError as e:
                    if not try_without_probe:
                        raise e

            if il < nb_loops-1:
                timer.wait_tick()

    def save_one(self, path_file, profile, time_now,
                 rotation_rate=None):
        """Save one profile in a file."""
        profile = profile.reshape([1, profile.size])

        dicttosave = {'profiles': profile,
                      'times': time_now}

        if rotation_rate is not None:
            dicttosave.update({'rotation_rates': rotation_rate})

        with H5File(path_file, 'r+') as f:
            f.save_dict_of_ndarrays(dicttosave)

    def load_one_file(self, ind_file_profiles=-1, times_slice=None):
        """Load the profiles contained in a file."""
        path_dir =self.path_save

        path_files = glob.glob(path_dir+'/profiles_*.h5')
        path_files.sort()

        path_file = path_files[ind_file_profiles]

        with H5File(path_file, 'r') as f:
            return f.load(times_slice=times_slice)

    def plot(self, ind_file_profiles=-1, times_slice=None,
             hastosave=False):
        """Plot profiles."""
        figures = figs.Figures(
            hastosave=hastosave,
            path_save=self.path_save
        )
        fig = figures.new_figure(
            name_file='fig_rho_z',
            fig_width_mm=190, fig_height_mm=150,
            size_axe=[0.12, 0.16, 0.84, 0.76]
        )
        ax = fig.gca()

        ax.set_xlabel(r'$\rho$')
        ax.set_ylabel(r'$z$ (mm)')

        ax.plot(self._exp.tank.profile.rho, self._exp.tank.profile.z, 'k:')


        if not isinstance(ind_file_profiles, (list, np.ndarray)):
            ind_file_profiles = [ind_file_profiles]


        for ifp in ind_file_profiles:

            dict_profiles = self.load_one_file(ind_file_profiles=ifp,
                                               times_slice=times_slice)
            times = dict_profiles['times']
            profiles = dict_profiles['profiles']

            nbt, nbz = profiles.shape

            pos_start = dict_profiles['pos_start']
            speed_measurements = dict_profiles['speed_measurements']
            self.write('speed_measurements: {}'.format(speed_measurements))

            sample_rate = dict_profiles['sample_rate']
            self.write('sample_rate: {}'.format(sample_rate))

            deltaz = speed_measurements/sample_rate
            zTaylor = pos_start + deltaz*np.linspace(0, -nbz, nbz)


            colors = gradient_colors(len(profiles))

            for ip, profile in enumerate(profiles):
                ax.plot(profile, zTaylor, c=colors[ip])

        fig.saveifhasto(format='pdf')
        figs.show()




    def plot_2d(self, ind_file_profiles=-1, times_slice=None,
                hastosave=False):
        """Plot a spatio-temporal figure from profiles."""

        figures = figs.Figures(
            hastosave=hastosave,
            path_save=self.path_save
        )
        fig = figures.new_figure(
            name_file='fig_rho_t_z',
            fig_width_mm=190, fig_height_mm=150,
            size_axe=[0.12, 0.13, 0.84, 0.75]
        )
        ax = fig.gca()



        # ax.set_title(r'$\rho$')
        # ax.set_xlabel(r'$t \Omega$')
        ax.set_xlabel(r'$t$ (min)')
        ax.set_ylabel(r'$z$ (mm)')

        dict_profiles = self.load_one_file(
            ind_file_profiles=ind_file_profiles, times_slice=times_slice)

        times = dict_profiles['times']
        profiles = dict_profiles['profiles']

        nbt, nbz = profiles.shape


        pos_start = dict_profiles['pos_start']
        speed_measurements = dict_profiles['speed_measurements']
        self.write('speed_measurements: {}'.format(speed_measurements))

        sample_rate = dict_profiles['sample_rate']
        self.write('sample_rate: {}'.format(sample_rate))

        deltaz = speed_measurements/sample_rate

        DECIMATE = True
        if DECIMATE:
            self.write('decimate')
            q = 30
            # profiles = scipy.signal.decimate(profiles, q=q,
            #                                 n=None, ftype='iir', axis=-1)
            profiles = decimate(profiles, q=q, nwindow=10, axis=1)
            self.write(' ended')
            nbz = int(nbz/q)
            deltaz *= q


        DECIMATE = False
        if DECIMATE:
            q = 2
            nwindow = 1
            self.write('decimate time')
            profiles = decimate(profiles, q=q, nwindow=nwindow, axis=0)
            times = decimate(times, q=q, nwindow=nwindow)
            self.write(' ended')



        self.write('nbz: {}'.format(nbz))

        zTaylor = pos_start + deltaz*np.linspace(0, -nbz, nbz)

        CONTOUR = False
        if CONTOUR:
            contours = ax.contourf(
                times/60,
                zTaylor,
                profiles.transpose(),
                50,
                cmap=plt.cm.jet)

            ax.contour(contours, levels=contours.levels[::1],
                        colors = 'k',
                        # origin=origin,
                        hold='on')

            fig.colorbar(contours)
        else:
            pc = ax.pcolormesh(
                times/60,
                zTaylor,
                profiles.transpose(),
                # cmap=plt.cm.jet,
                cmap=plt.cm.Accent,
                shading='flat'
                )

            fig.colorbar(pc)


        ax.set_ylim([0, self._exp.tank.z_max])
        ax.set_xlim([times[0]/60, times[-1]/60])

        ax2 = ax.twiny()
        tOmega = 1000*np.arange(10.)
        t_inmin = tOmega/self._exp.params['Omega1']/60
        ax2.set_xlabel('$t\Omega_1/1000$')
        ax2.set_xticks(t_inmin)
        labs = ['{0:3.0f}'.format(number/1000) for number in tOmega]
        ax2.set_xticklabels(labs)
        ax2.set_xlim(ax.get_xlim())




        fig.saveifhasto(format='pdf')
        figs.show()


    def write(self, string):
        print(string)








class ExpWithConductivityProbe(ExperimentWithTank):
    """Represent an experiment with a moving conductivity probe and a tank.

    Parameters
    ----------
    (for the __init__ method)

    rhos : array_like, optional
        Density array.

    zs : array_like, optional
        Position array.

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

    tank : :class:`fluidlab.objects.tanks.StratifiedTank`
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

    _base_dir = 'With_conductivity_probe'

    def __init__(self,
                 rhos=None, zs=None, params=None,
                 description=None,
                 str_path=None,
                 position_start=300., position_max=None, Deltaz=400.,
                 need_board=True
                 ):

        # call the __init__ function of the inherited class
        super(ExpWithConductivityProbe, self).__init__(
            rhos=rhos, zs=zs, params=params,
            description=description,
            str_path=str_path)

        # add the board handler
        if need_board:
            self.board = PowerDAQBoard()
            if self.board.works:
                self.sprobe = MovingConductivityProbe(
                    board=self.board,
                    sample_rate=1000,
                    position_start=position_start,
                    position_max=position_max,
                    Deltaz=Deltaz
                )

        # add the `profiles` attribute
        self.profiles = Profiles(self)



    def __getattr__(self, key):
        if key == 'sprobe':
            raise AttributeError(
"""'ILSTaylorCouetteExp' object has no attribute 'sprobe' since no
working powerdaq board seems to be available."""
)
        else:
            raise AttributeError()






if __name__ == '__main__':

    import fluiddyn

    # exp = ExpWithConductivityProbe(
    #     rhos=[1.1, 1], zs=[0, 1])

    exp = fluiddyn.load_exp('Exp_Omega=0.73_N0=1.83_2014-04-10_09-55-39')

    # exp.profiles.measure(duration=30, period=2,
    #                      deltaz=300, speed_measurements=4000,
    #                      speed_up=10000)
