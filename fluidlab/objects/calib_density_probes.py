"""
Calibration for density measurement (:mod:`fluidlab.objects.calib_density_probes`)
===================================================================================

.. autosummary::
   :toctree:

.. autoclass:: Calibration
   :members:
   :private-members:

"""
import os
import time

import numpy as np
import h5py
import matplotlib.pyplot as plt

from fluiddyn.io import query


def _isarray(a):
    return isinstance(a, (np.ndarray, np.generic))


def load_calibration(path):
    """Loads the data from the previous calibrations."""
    rho, voltrho, T, voltT, date = [], [], [], [], []

    if not os.path.exists(path):
        print("No calibration file " + path)
    else:
        with h5py.File(path, "r") as f:
            rho = f["rho"].value
            voltrho = f["voltrho"].value

            if "T" in f.keys():
                T = f["T"].value
                voltT = f["voltT"].value
            date = f["date"].value

    return rho, voltrho, T, voltT, date


def prepare_calibration(rho_min=1, rho_max=1.18, nb_solutions=6):
    """Gives indications to prepare a calibration."""

    rhos = np.linspace(rho_min, rho_max, nb_solutions)

    print("Possible densities:")
    print("rhos:", rhos)

    print(
        "These solutions can be prepared by mixing the two "
        "first solutions with extreme densities with the following "
        "volume ratio: \nV_rho_max/V_tot :",
        (rhos - rho_min) / (rho_max - rho_min),
    )


class Calibration:
    """Calibrate density"""
    def __init__(self, path_rho, path_temp=None):
        self.path_rho = path_rho

        rho_old, voltrho_old, T_old, voltT_old, date_old = self._load("rho")
        self._fit_rho_vs_voltrho(rho_old, voltrho_old)

        self.path_temp = path_temp
        if path_temp is not None:
            # tension when temperature probe is unplugged
            # (constructor info)
            self.voltToff = -4.9962

    def _path_from_kind(self, kind_of_calib):

        if kind_of_calib == "rho":
            path = self.path_rho
        elif kind_of_calib == "T":
            path = self.path_temp
        else:
            raise ValueError

        return path

    def _load(self, kind_of_calib):
        """Loads the data from the previous calibrations."""

        path = self._path_from_kind(kind_of_calib)

        return load_calibration(path)

    def plot_rho(self, rho=None, voltrho=None):
        """Plots the measurements of the saved calibrations for rho."""

        fig = plt.figure()
        ax = fig.gca()

        ax.set_xlabel(r"$\rho$")
        ax.set_ylabel(r"$U$ (V)")

        # load all saved calibrations
        rho_old, voltrho_old, T_old, voltT_old, date_old = self._load("rho")
        if _isarray(rho_old) and rho_old.size >= 1:
            ax.plot(rho_old, voltrho_old, "xg")
        if _isarray(rho_old) and rho_old.size > 1:
            self._fit_rho_vs_voltrho(rho_old, voltrho_old)
            volts_for_plot = np.linspace(
                voltrho_old.min(), voltrho_old.max(), 200
            )
            ax.plot(self.rho_from_voltrho(volts_for_plot), volts_for_plot, "k-")

        if rho is not None and voltrho is not None:
            ax.plot(rho, voltrho, "xr")

        plt.show()

    def plot_temp(self, T=None, voltT=None):
        """Plots the measurements of the saved calibrations for T."""

        if self.path_temp is None:
            print("No calibration for temperature.")
            return

        fig = plt.figure()
        ax = fig.gca()
        ax.set_xlabel(r"$T (C)$")
        ax.set_ylabel(r"$U$ (V)")

        # load all saved calibrations
        rho_old, voltrho_old, T_old, voltT_old, date_old = self._load("T")
        if _isarray(T_old) and T_old.size >= 1:
            ax.plot(T_old, voltT_old, "xg")
        if _isarray(T_old) and T_old.size > 1:
            self._fit_T_vs_voltT(T_old, voltT_old)
            ax.plot(T_old, voltT_old, "xg")
            volts_for_plot = np.linspace(voltT_old.min(), voltT_old.max(), 200)
            ax.plot(self.T_from_voltT(volts_for_plot), volts_for_plot, "k-")

        if T is not None and voltT is not None:
            ax.plot(T, voltT, "xr")

        plt.show()

    def _fit_rho_vs_voltrho(self, rho, voltrho):
        """Creates a function from data."""
        if len(rho) < 4:
            deg = 1
        elif len(rho) < 5:
            deg = 2
        else:
            deg = 3
        coeffs = np.polyfit(voltrho, rho, deg=deg)
        self.rho_from_voltrho = np.poly1d(coeffs)
        self.coeffs_rho = coeffs

    def T_from_voltT(self, voltT):
        if self.path_temp is None:
            print("No calibration for temperature.")
            return

        if not hasattr(self, "coeffs_temp"):
            raise Exception("First use the function _fit_T_vs_voltT")

        tmp = (
            np.log(voltT - self.voltToff) - self.coeffs_temp[1]
        ) / self.coeffs_temp[0]
        Ti = 1.0 / tmp - 273.15
        return Ti

    def _fit_T_vs_voltT(self, T, voltT):
        """Creates a function from data."""
        print("_fit_T_vs_voltT")
        y = np.log(voltT - self.voltToff)
        x = 1.0 / (T + 273.15)
        self.coeffs_temp = np.polyfit(x, y, deg=1)

    def add_point_rho(self, rho, T, duration=2.0):
        r"""Calibrates the probe.

        Parameters
        ----------
        rho :
           The density :math:`\rho` of the sample (in kg/l)).

        T :
           Temperature in C

        duration : number
           The duration of one measurement (in s).

        Notes
        -----

        :math:`\rho(C)` and :math:`U(C, T)`, where :math:`C` the
        concentration, :math:`U` the voltage and :math:`T` the
        temperature.
        """
        if not hasattr(self, "probe"):
            print("No probe, can not add calibration point.")
            return

        answer = query.query(
            f"\nPut the probe in solution with rho = {rho}\n"
            + "Ready? [Y / no, cancel the calibration] "
        )

        if answer.startswith("n"):
            print("Calibration cancelled...")
            return

        happy = False
        while not happy:
            volts = self.probe.measure_volts(duration, return_time=False)
            # header = ('calibration for rho='
            #           '{}, T= {}\nVolt rho, Volt T'.format(rho, T))
            # np.savetxt('tmp_calib.txt', volts.transpose(), header=header)
            voltages = volts.mean(axis=1)
            print("solution rho: {} kg/l; voltage: {}".format(rho, voltages[0]))
            # print('solution T: {} ; voltage: {} V'.format(T, voltages[1]))
            happy = query.query_yes_no("Are you happy with this measurement?")

        self.plot_rho(rho=rho, voltrho=voltages[0])

        if query.query_yes_no("Should the new point be saved?"):
            self._save_new_point(rho, T, voltages, "rho")

    def _save_new_point(self, rho, T, volts, kind_of_calib):
        """Saves the results of a calibration."""

        path = self._path_from_kind(kind_of_calib)

        print("Save the results of the calibration in file:", path)

        rho_old, voltrho_old, T_old, voltT_old, date_old = self._load(
            kind_of_calib
        )

        if _isarray(rho_old) and rho_old.size >= 1:
            rho = np.append(rho_old, rho)
            voltrho = np.append(voltrho_old, volts[0])
            if volts.shape[0] > 1:
                T = np.append(T_old, T)
                voltT = np.append(voltT_old, volts[1])
            date = np.append(date_old, time.ctime(int(time.time())))
        else:
            rho = np.array(rho)
            voltrho = np.array(volts[0])
            if volts.shape[0] > 1:
                T = np.array(T)
                voltT = np.array(volts[1])
            date = np.array(time.ctime(int(time.time())))
        if not os.path.exists(path):
            mode = "a"
        else:
            mode = "w"

        with h5py.File(path, mode) as f:
            f["rho"] = rho
            f["voltrho"] = voltrho
            if volts.shape[0] > 1:
                f["T"] = T
                f["voltT"] = voltT
            f["date"] = date


if __name__ == "__main__":

    path = (
        "/fsnet/project/watu/2017/17MILESTONE/Calibrations/Probes/"
        "2017-06-29_calib_mscti_probe0_rho.h5"
    )

    calib = Calibration(path)
    calib.plot_calibration()

    calib2 = Calibration(path, path)
