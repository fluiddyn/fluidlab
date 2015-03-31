"""
Probes (:mod:`fluidlab.objects.probes`)
=======================================

.. currentmodule:: fluidlab.objects.probes

Provides:

.. autoclass:: ConductivityProbe
   :members:

.. autoclass:: MovingConductivityProbe
   :members:


"""
from __future__ import division, print_function

import numpy as np
import os
import inspect
import glob

from fluiddyn.io import txt

from fluiddyn.util import time_as_str
from fluiddyn.util import query
from fluidlab.objects.traverse import Traverse

from fluidlab.objects.boards import ObjectUsingBoard

import fluiddyn.output.figs as figs

from fluidlab.objects.pinchvalve import PinchValve, tube_as_opened_as_possible

# class TemperatureProbe(ObjectUsingBoard):
#     """A class handling the temperature probe."""
#     def __init__(self, board=None):

#         super(TemperatureProbe, self).__init__(board=board)



class ConductivityProbe(ObjectUsingBoard):
    """Represent a conductivity probe.

    This is an example of modification.

    Parameters
    ----------
    board : ???
        Object representing a board.

    channel : number
        The channel index.


    """
    def __init__(self, board=None, channel=1, sample_rate=1000,
                 has_to_config_board=True, VALVE=True):

        super(ConductivityProbe, self).__init__(board=board)

        self.channel = channel

        if (has_to_config_board and board is not None
                and self.board is not False):

            self.board.ain.configure(
                sample_rate,
                channels=self.channel,
                range10V=True,
                bipolar=True,  # False,
                gain_channels=1,
                differential=False)

            self.sample_rate = self.board.ain.freq_used

        if self.board is not None and self.board is not False:
            self.ind_channel = self.board.ain.channels.index(self.channel)

        if VALVE and self.board is not None and self.board is not False:
            self.valve = PinchValve(board, channel=0)
        else:
            self.valve = None

        self.path_calib = (
            os.path.dirname(os.path.abspath(
                inspect.getfile(inspect.currentframe())
            ))
            +'/Calib_conductivity_probe')

        # load all saved calibrations
        rhos_old, volts_old = self.load_calibrations()

        if len(rhos_old) > 0:
            self.create_function_from_data(rhos_old, volts_old)



    def prepare_calibration(self, rho_min=1, rho_max=1.18, nb_solutions=6):
        """Gives indications to prepare a calibration."""

        rhos = np.linspace(rho_min, rho_max, nb_solutions)

        print('Possible densities:')
        print('rhos:', rhos)

        print(
"""These solutions can be prepared by mixing the two first solutions
with extreme densities with the following volume ratio: """
        )

        print('V_rho_max/V_tot :', (rhos-rho_min)/(rho_max-rho_min))





    def calibrate(self, rhos, duration_1measure=4.):
        r"""Calibrates the probe.

        Parameters
        ----------
        rhos : array_like
           The density :math:`\rho` of the samples (in kg/l).

        duration_1measure : number
           The duration of one measurement (in s).

        Notes
        -----

        :math:`\rho(C)` and :math:`U(C, T)`, where :math:`C` the
        concentration, :math:`U` the voltage and :math:`T` the
        temperature.
        """
        sample_rate_old = self.sample_rate

        self.set_sample_rate(1000.)

        voltages = np.empty(rhos.shape)

        for ir, rho in enumerate(rhos):
            # measure voltages

            answer = query.query(
                '\nPut the probe in solution with rho = {0}\n'.format(rho)+
                'Ready? [Y / no, cancel the calibration] '
            )

            if answer.startswith('n'):
                print('Calibration cancelled...')
                self.set_sample_rate(sample_rate_old)
                return


            happy = False
            while not happy:
                volts = self.measure_volts(duration_1measure)
                with open(self.path_calib+'/temp', 'w') as f:
                    f.write(repr(volts))
                volt = np.median(volts)
                voltages[ir] = volt
                print('solution rho: {0} ; voltage: {1}'.format(rho, volt))
                happy = query.query_yes_no(
                    'Are you happy with this measurement?')

        # load all saved calibrations
        rhos_old, volts_old = self.load_calibrations()

        # plot
        figures = figs.Figures()
        fig = figures.new_figure(
            name_file='fig_calibration',
            fig_width_mm=190, fig_height_mm=150,
            size_axe=[0.13, 0.14, 0.83, 0.82]
        )
        ax = fig.gca()

        ax.set_xlabel(r'$\rho$')
        ax.set_ylabel(r'$U$ (V)')

        ax.set_xlim([0.95, 1.25])

        ax.plot(rhos, voltages, 'or')

        if len(volts_old) > 2:
            ax.plot(rhos_old, volts_old, 'xg')

            self.create_function_from_data(rhos_old, volts_old)
            volts_for_plot = np.linspace(0., 10., 200)
            ax.plot(self.rho_from_volt(volts_for_plot),
                    volts_for_plot,
                    'k-')

        print('rhos:\n', rhos)
        print('volts:\n', voltages)

        try:
            print('rhos computed from the voltages '
                  'and from previous calibrations:\n',
                  self.rho_from_volt(voltages))
        except AttributeError:
            pass

        print('Warning: bug with anaconda and non-blocking show().\n'
              'Close the windows to continue.')
        figs.show(block=True)

        # save the measures done before
        if query.query_yes_no('Do you want to save these measurements?'):
            self.save_calibration(rhos, voltages)

            volts = np.concatenate([volts_old, voltages])
            rhos = np.concatenate([rhos_old, rhos])

            self.create_function_from_data(rhos, volts)

        self.set_sample_rate(sample_rate_old)



    def plot_calibrations(self, rhos=None, volts=None, rho_real=None):
        """Plots the measurements of the saved calibrations."""
        # load all saved calibrations
        rhos_old, volts_old = self.load_calibrations()

        # plot
        figures = figs.Figures()
        fig = figures.new_figure(
            name_file='fig_calibration',
            fig_width_mm=190, fig_height_mm=150,
            size_axe=[0.13, 0.14, 0.83, 0.82]
        )
        ax = fig.gca()


        ax.set_xlabel(r'$\rho$')
        ax.set_ylabel(r'$U$ (V)')

        ax.set_xlim([0.95, 1.25])

        if len(volts_old) > 2:
            ax.plot(rhos_old, volts_old, 'xg')
            volts_for_plot = np.linspace(0., volts_old.max(), 200)
            ax.plot(self.rho_from_volt(volts_for_plot),
                    volts_for_plot,
                    'k-')

        if rhos is not None and volts is not None:
            ax.plot(rhos, volts, 'xr')

        if rho_real is not None:
            ax.plot(rho_real, volts.mean(), 'ob')


        figs.show(block=True)




    def save_calibration(self, rhos, voltages):
        """Saves the results of a calibration."""

        name_file = 'rhos_voltages_'+time_as_str()
        print('Save the results of the calibration in file:', name_file)

        txt.save_quantities_in_txt_file(
            self.path_calib+'/'+name_file,
            (rhos, voltages))





    def load_calibrations(self):
        """Loads the data from the previous calibrations."""
        rhos, volts = [], []
        cfiles = glob.glob(self.path_calib+'/rhos_voltages_*')
        cfiles = [cf for cf in cfiles if cf[-1] != '~']
        if len(cfiles) == 0:
            return rhos, volts
        for cf in cfiles:
            rho, volt = txt.quantities_from_txt_file(cf)
            rhos.append(rho)
            volts.append(volt)
        rhos = np.concatenate(rhos)
        volts = np.concatenate(volts)
        return rhos, volts


    def create_function_from_data(self, rhos, volts):
        """Creates a function from data."""
        coeffs = np.polyfit(volts, rhos, deg=3)
        self.rho_from_volt = np.poly1d(coeffs)




    def set_sample_rate(self, sample_rate):
        """Sets the sample rate."""
        self.board.ain.configure(sample_rate)
        self.sample_rate = self.board.ain.freq_used



    def measure_volts(self, duration, sample_rate=None,
                      return_time=False, verbose=False):
        """Measure and return the times and voltages.

        Parameters
        ----------

        duration :
          (in s)

        """
        if sample_rate is not None and sample_rate != self.sample_rate:
            self.set_sample_rate(sample_rate)

        nb = abs(np.round(duration*self.sample_rate))

        with tube_as_opened_as_possible(self.valve):
            volts = self.board.ain(nb)

        volts = volts[self.ind_channel].transpose()

        if verbose:
            print('volts:\n', volts)
            print('volts.mean():', volts.mean())

        if return_time:
            ts = 1./self.sample_rate*np.arange(1, nb+1)
            return ts, volts
        else:
            return volts



    def measure(self, duration, sample_rate=None,
                return_time=False, verbose=False):
        """Measure and return the times and density.

        Parameters
        ----------

        duration : number
          (in s)

        sample_rate : number
          (in Hz)

        """
        if not hasattr(self, 'rho_from_volt'):
            raise ValueError(
"""Since no data from previous calibrations has been found the
function measure can not be used.  The function measure_volts can be
used instead.""")

        results = self.measure_volts(
            duration, sample_rate=sample_rate, verbose=verbose)

        if return_time:
            ts, volts = results
        else:
            volts = results

        rhos = self.rho_from_volt(volts)
        if verbose:
            print('rhos:\n', rhos)
            print('rhos.mean():', rhos.mean())

        if return_time:
            return ts, rhos
        else:
            return rhos



    def test_measure(self, duration=2, hastoplot=True, rho_real=None):
        """Test the measurement."""
        volts = self.measure_volts(duration=duration)
        rhos = self.rho_from_volt(volts)
        volt = volts.mean()
        rho = rhos.mean()
        print('    rho_real: {:7.5f},\n'.format(rho_real)+
              'mean measurement;\n'+
              '    rho: {:7.5f}, volt: {:7.5f}\n'.format(rho, volt)+
              'For the calibration file:\n'+
              '    {:7.5f} {:7.5f}'.format(rho_real, volt)
)

        if hastoplot:
            self.plot_calibrations(rhos, volts, rho_real=rho_real)







class MovingConductivityProbe(ConductivityProbe, Traverse):
    """Represent a conductivity probe that can be deplaced by a traverse.

    Parameters
    ----------
    (for the __init__ method)

    board : , optional
        Acquisition board.

    channel : {1, int}, optional
        Indice of the channel in the acquisition board.

    sample_rate : {100, number}, optional
        Sample rate of the probe.


    has_to_config_board : {True, bool}, optional
        Has to configure the board.

    position_start : {300., number}, optional
        Position when created (in mm).

    position_max : {None, number}, optional
        ???

    Deltaz : {400, number}, optional
        Distance between extremal points.


    """

    def __init__(self, board=None, channel=1, sample_rate=100,
                 has_to_config_board=True,
                 position_start=300.,
                 position_max=None,
                 Deltaz=400.):

        ConductivityProbe.__init__(self, board=board, channel=channel,
                                   sample_rate=sample_rate,
                                   has_to_config_board=has_to_config_board)

        Traverse.__init__(self, board=board,
                          position_start=position_start,
                          position_max=position_max,
                          Deltaz=Deltaz)





    def move_measure(self, deltaz=100, speed=100, sample_rate=None,
                     return_time=False):
        """Move the probe while measuring.

        Parameters
        ----------
        deltaz: number
           Distance to move (in mm).

        speed: number
           (in mm/s)

        sample_rate: number
           (in Hz)
        """

        duration = abs(deltaz/speed)

        super(MovingConductivityProbe, self).move(deltaz=deltaz, speed=speed)

        return super(MovingConductivityProbe, self).measure(
            duration, sample_rate=sample_rate, return_time=return_time)















if __name__ == '__main__':

#     from fluiddyn.util.timer import Timer

    from fluidlab.objects.boards import PowerDAQBoard

    board = PowerDAQBoard()
    sprobe = MovingConductivityProbe(board=board)

    # sprobe.prepare_calibration(rho_max=1.18)

    # rhos = np.array([0.9987,
    #                  1.0207, 1.0394, 1.0753,
    #                  1.1108, 1.1315, 1.1504])
    # sprobe.calibrate(rhos=rhos)



    # distance = 200.
    # sprobe.set_sample_rate(5)
    # timer = Timer(4)
    # for i in xrange(4):
    #     print(sprobe.move_measure(deltaz=-distance, speed=300))
    #     time.sleep(0.2)
    #     sprobe.move(deltaz=distance, speed=100, bloquing=True)
    #     timer.wait_till_tick()


    # sprobe.test_measure(rho_real=1.097727)


    # time.sleep(2)

    # volts = sprobe.measure_volts(duration=4)
    # print(volts.mean())



    # print(len(rhos))




    # sprobe.plot_calibrations()
