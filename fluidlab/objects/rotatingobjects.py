"""
Rotating objects (:mod:`fluidlab.objects.rotatingobjects`)
==========================================================

.. currentmodule:: fluidlab.objects.rotatingobjects

Provides:

.. autoclass:: RotatingObject
   :members:

.. autoclass:: InnerCylinderOldTC
   :members:

.. autoclass:: InnerCylinder
   :members:

.. autoclass:: RotatingTable
   :members:

.. autofunction:: create_rotating_objects_kepler

"""


from __future__ import division, print_function

import numpy as np
import numbers
import atexit
import os
import inspect
import glob
import time

from fluidlab.objects.boards import ObjectUsingBoard
from fluidlab.objects.boards import NIDAQBoard
from fluiddyn.util.timer import Timer
from fluiddyn.util import query
from fluiddyn.io import txt

import fluiddyn.output.figs as figs

from fluiddyn.util.deamons import DaemonThread
#  , DaemonProcess
# We can use either a deamon thread or a deamon process...
Daemon = DaemonThread
# Daemon = DaemonProcess


class RotatingObject(ObjectUsingBoard):
    name = 'rotating object'
    rotation_rate_max = 2*np.pi/2.43  # (rad/s)
    voltage_max = 5.
    channel_class = 0

    def __init__(self, rotation_rate, board=None, channel=None):

        if channel is not None:
            self.channel = channel
        else:
            self.channel = self.channel_class

        if board is None:
            board = NIDAQBoard()
        super(RotatingObject, self).__init__(board=board)

        if hasattr(rotation_rate, '__call__'):
            self.rotation_rate_vs_t = rotation_rate
            self.rotation_rate = self.rotation_rate_vs_t(0.)
            if not isinstance(self.rotation_rate, numbers.Number):
                raise ValueError('If rotation_rate is a function, '
                                 'it should return a number.')
        elif isinstance(rotation_rate, numbers.Number):
            self.rotation_rate = rotation_rate
        else:
            raise ValueError('rotation_rate should be a number or a function.')


        self.path_calib = os.path.join(
            os.path.dirname(os.path.abspath(
                inspect.getfile(inspect.currentframe()))),
            'Calib_rotation_objects')

        if hasattr(self, 'name'):
            self.path_calib = os.path.join(
                self.path_calib, self.name.capitalize().replace(' ', '_')
            )

        if not os.path.exists(self.path_calib):
            os.makedirs(self.path_calib)

        # load all saved calibrations
        volts_old, periods_old = self.load_calibrations()

        if len(volts_old)>0:
            cond = 1./periods_old > 0
            volts_old = volts_old[cond]
            periods_old = periods_old[cond]
            self.create_function_from_data(volts_old, periods_old)
        else:
            self.write('This rotating object should first be calibrated.')

        atexit.register(RotatingObject.stop, self)




    def set_rotation_rate(self, rotation_rate):
        self.rotation_rate = rotation_rate
        if self.board.works:
            self.write(
                '{:22s}; rot. rate: {}'.format(self.name, rotation_rate))
            voltage = self._voltage_from_rotation_rate(rotation_rate)
            if voltage < 0:
                voltage = 0
            self._set_voltage(voltage)



    def _set_voltage(self, voltage):
        if self.board.works:
            self.board.out.set_voltage(voltage, channels=self.channel)

    def calibrate(self, voltage=3):
        self.write('calibration with voltage: {0:6.2f}'.format(voltage))
        self._set_voltage(voltage)
        self.write('Please measure the period.')

        yes = False
        while not yes:
            yes = query.query_yes_no(
                'Is it measure now?')
        self._set_voltage(0)
        period = query.query_number('What was the period?')

        self.write('Something else could be implemented here.')
        return period



    def calibrate_with_period(self, period=8):

        self.write('Calibrate with period: {0:6.2f}'.format(period))
        voltage = self._voltage_from_rotation_rate(2*np.pi/period)
        self.write(
            'it should correspond to a voltage of {0:6.2f}'.format(voltage))

        period = self.calibrate(voltage)



    def load_calibrations(self):
        """Loads the data from the previous calibrations."""
        volts, periods = [], []
        cfiles = glob.glob(self.path_calib+'/volts_periods_*')
        cfiles = [cf for cf in cfiles if cf[-1] != '~']

        if len(cfiles) == 0:
            return volts, periods
        for cf in cfiles:
            v, p = txt.quantities_from_txt_file(cf)
            volts.append(v)
            periods.append(p)
        volts = np.concatenate(volts)
        periods = np.concatenate(periods)
        return volts, periods





    def plot_calibrations(self, volts=None, periods=None):
        """Plots the measurements of the saved calibrations."""
        # load all saved calibrations
        volts_old, periods_old = self.load_calibrations()

        # plot
        figures = figs.Figures()
        fig = figures.new_figure(
            name_file='fig_calibration',
            fig_width_mm=190, fig_height_mm=150,
            size_axe=[0.13, 0.14, 0.83, 0.82]
        )
        ax = fig.gca()

        ax.set_xlabel(r'$U$ (V)')
        ax.set_ylabel(r'$\Omega$ (rad/s)')

        # ax.set_xlim([0.95, 1.25])

        Omegas_old = 2*np.pi/periods_old


        if len(volts_old) > 2:
            ax.plot(volts_old, Omegas_old, 'xg')

            cond = 1./periods_old > 0
            volts_old = volts_old[cond]
            periods_old = periods_old[cond]

            if len(volts_old)>0:
                self.create_function_from_data(volts_old, periods_old)

            rr_for_plot = np.linspace(0., self.rotation_rate_max, 200)
            volts_for_plot = self._voltage_from_rotation_rate(rr_for_plot)

            ax.plot(volts_for_plot,
                    rr_for_plot,
                    'k-')

        if periods is not None and volts is not None:
            Omegas = 2*np.pi/periods
            ax.plot(volts, Omegas, 'xr')

        figs.show(block=True)

    def create_function_from_data(self, volts, periods):
        """Creates a function from data."""
        Omegas = 2*np.pi/periods

        coeffs = np.polyfit(Omegas, volts, deg=2)
        self._voltage_from_rotation_rate = np.poly1d(coeffs)

    # def _voltage_from_rotation_rate(self, rotation_rate):
    #     return rotation_rate/self.rotation_rate_max*self.voltage_max

    def stop(self):
        if self.board is not False:
            self._set_voltage(0.)

    def write(self, string):
        print(string)




class InnerCylinderOldTC(RotatingObject):
    rotation_rate_max = 2*np.pi/2.43  # (rad/s)
    voltage_max = 5.
    name = 'Inner cylinder old TC'


class InnerCylinder(RotatingObject):
    rotation_rate_max = 1.18  # (rad/s)
    voltage_max = 5.
    name = 'Inner cylinder new TC'


class RotatingTable(RotatingObject):
    rotation_rate_max = 2.5  # (rad/s)
    voltage_max = 5.
    name = 'Rotating table'
    channel_class = 1






class DaemonRunningRotatingObject(Daemon):
    def __init__(self, rotating_object):
        super(DaemonRunningRotatingObject, self).__init__()
        self.ro = rotating_object

    def run(self):
        ro = self.ro
        ro.running = True
        ro.set_rotation_rate(ro.rotation_rate)
        if hasattr(ro, 'rotation_rate_vs_t'):
            self._loop_time()

    def _loop_time(self, dt=0.2):
        ro = self.ro
        ro.write('start _loop_time '+self.ro.name)
        tstart = time.time()
        timer = Timer(dt)
        while self.keepgoing.value:
            tnow = time.time()
            t = tnow-tstart
            rr = ro.rotation_rate_vs_t(t)
            ro.set_rotation_rate(rr)
            timer.wait_till_tick()
        ro.write('exit loop')

    def stop(self):
        super(DaemonRunningRotatingObject, self).stop()



def create_rotating_objects_pseudokepler(Omega_i, R_i, R_o, gamma):
    """Return two rotating objects related with the Kepler scaling law.

    Parameters
    ----------
    Omega_i : number
        The rotation rate of the inner cylinder (in rad/s)

    R_i : number
        Radius of the inner cylinder.

    R_o : number
        Radius of the outer cylinder (same units as *R_i*).

    """
    alpha_i = R_i / R_o
    mu_o = alpha_i**gamma

    def Omega_o(t):
        return mu_o*Omega_i(t)

    inner_cylinder = InnerCylinder(rotation_rate=Omega_i)
    rotating_table = RotatingTable(
        rotation_rate=Omega_o, board=inner_cylinder.board)

    return inner_cylinder, rotating_table





def create_rotating_objects_kepler(Omega_i, R_i, R_o):
    """Return two rotating objects related with the Kepler scaling law.

    Parameters
    ----------
    Omega_i : number
        The rotation rate of the inner cylinder (in rad/s)

    R_i : number
        Radius of the inner cylinder.

    R_o : number
        Radius of the outer cylinder (same units as *R_i*).

    """
    alpha_i = R_i / R_o
    mu_o = alpha_i**(3/2)

    def Omega_o(t):
        return mu_o*Omega_i(t)

    inner_cylinder = InnerCylinder(rotation_rate=Omega_i)
    rotating_table = RotatingTable(
        rotation_rate=Omega_o, board=inner_cylinder.board)

    return inner_cylinder, rotating_table



if __name__ == '__main__':

    import time

    inner_cylinder = InnerCylinder(rotation_rate=0)



    # def Omega_i(t):
    #     Omega = 0.2
    #     time_rampe = 10
    #     t = t/time_rampe
    #     if t < Omega:
    #         ret = t*Omega
    #     # elif t < 2*Omega:
    #     #     ret = Omega*(2-t)
    #     else:
    #         ret = 0
    #         # ret = Omega
    #     return ret

    # R_i = 100
    # R_o = 482/2

    # rc, rt = create_rotating_objects_kepler(Omega_i, R_i, R_o)

    # ro.calibrate(1)

    # ro.calibrate(5)

    # ro.calibrate(4)

    # ro.calibrate_with_period(8)

    # ro.plot_calibrations()


    # daemon_rc = DaemonRunningRotatingObject(rc)
    # daemon_rt = DaemonRunningRotatingObject(rt)

    # daemon_rc.start()
    # daemon_rt.start()

    # time.sleep(100)
    # daemon_rc.stop()
    # daemon_rt.stop()





    # daemon.start()
    # time.sleep(22)
    # daemon.stop()

    # time.sleep(1)

    # daemon = DaemonRunningRotatingObject(ro)
    # daemon.start()
    # time.sleep(2)
