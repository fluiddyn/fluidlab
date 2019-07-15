"""Probes (:mod:`fluidlab.objects.mscti_probes`)
=================================================

.. autosummary::
   :toctree:


.. autoclass:: MSCTIProbe
   :members:
   :undoc-members:


"""

from __future__ import division, print_function

import numpy as np
import os
import matplotlib.pyplot as plt

from fluiddyn.io import query
from fluidlab.daq.daqmx import read_analog

import h5py

import time


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


class MSCTIProbe:
    """Represent a MSCTI conductivity (+ temperature) probe.

    Parameters
    ----------

    """

    def __init__(
        self,
        channels=["Dev1/ai1", "Dev1/ai2"],
        sample_rate=100,
        Vmin=-5,
        Vmax=5,
        mode="Diff",
        files_calib=None,
    ):

        if files_calib is None:
            files_calib = ["calib_mscti_rho", "calib_mscti_temp"]

        self.channels = channels
        self.sample_rate = sample_rate
        self.Vmin = Vmin
        self.Vmax = Vmax
        self.mode = mode
        self.files_calib = files_calib
        self.voltToff = -4.9962  # tension when temperature probe is unplugged
        # (constructor info)

        self._has_temp = len(files_calib) > 1

        # load saved calibration
        rho_old, voltrho_old, T_old, voltT_old, date_old = self.load_calibration(
            "rho"
        )

        if _isarray(rho_old) and rho_old.size > 1:
            self.fit_rho_vs_voltrho(rho_old, voltrho_old)

        if self._has_temp:
            rho_old, voltrho_old, T_old, voltT_old, date_old = self.load_calibration(
                "T"
            )

            if _isarray(rho_old) and rho_old.size > 1:
                self.fit_T_vs_voltT(T_old, voltT_old)

    def set_sample_rate(self, sample_rate):
        """Sets the sample rate."""
        self.sample_rate = sample_rate

    def set_mode(self, mode):
        """Sets the mode."""
        self.mode = mode

    def set_Vmin(self, Vmin):
        """Sets Vmin."""
        self.Vmin = Vmin

    def set_Vmax(self, Vmax):
        """Sets Vmin."""
        self.Vmax = Vmax

    def set_files_calib(self, files_calib):
        """Sets the file calib."""
        self.files_calib = files_calib

    # ##########################################################################
    # MEASUREMENTS

    def measure_volts(
        self,
        duration,
        path_save=None,
        sample_rate=None,
        return_time=True,
        verbose=False,
    ):
        """Measure and return the times and voltages.

        Parameters
        ----------

        duration :
          (in s)

        """
        if path_save is None:
            save = False
        else:
            save = True

        if not return_time and save:
            print(
                "the times are important for acquisition, "
                "return_time is set to True automatically"
            )
            return_time = True

        if sample_rate is not None and sample_rate != self.sample_rate:
            self.set_sample_rate(sample_rate)

        nb = int(abs(np.round(duration * self.sample_rate)))

        volts = read_analog(
            self.channels, self.mode, self.Vmin, self.Vmax, nb, self.sample_rate
        )

        if verbose:
            print("conductivity volts:\n", volts[0])
            print("mean of conductictivity volts:", volts[0].mean())

            if self._has_temp:
                print("temperature volts:\n", volts[1])
                print("mean of temperature volts:", volts[1].mean())

        if return_time:
            ts = 1.0 / self.sample_rate * np.arange(1, nb + 1)
            if save:
                if not path_save.endswith(".h5"):
                    path_save += ".h5"
                self.save_volts(path_save, ts, volts)
            return ts, volts

        else:
            return volts

    def save_volts(self, path, times, volts):

        if os.path.exists(path):
            raise ValueError("file already exist, give an other name file")

        with h5py.File(path, "w-") as f:
            f["t"] = times
            f["voltrho"] = volts[0]
            if self._has_temp:
                f["voltT"] = volts[1]
            f["date"] = time.ctime(int(time.time()))

            if os.path.exists(self.files_calib[0] + ".h5"):
                f["calibration/file_calibration_rho"] = self.files_calib[0]
                if not hasattr(self, "coeffs_rho"):
                    rho_old, voltrho_old, T_old, voltT_old, date_old = self.load_calibration(
                        "rho"
                    )
                    if _isarray(rho_old) and rho_old.size >= 1:
                        self.fit_rho_vs_voltrho(rho_old, voltrho_old)
                        f["calibration/coeffsrho"] = self.coeffsrho
                    else:
                        f["calibration/coeffsrho"] = self.coeffsrho

            if self._has_temp and os.path.exists(self.files_calib[1] + ".h5"):
                f["calibration/file_calibration_T"] = self.files_calib[1]
                if not hasattr(self, "coeffs_T"):
                    rho_old, voltrho_old, T_old, voltT_old, date_old = self.load_calibration(
                        "T"
                    )
                    if _isarray(rho_old) and rho_old.size >= 1:
                        self.fit_T_vs_voltT(T_old, voltT_old)
                        f["calibration/coeffsT"] = self.coeffsT
                    else:
                        f["calibration/coeffsT"] = self.coeffsT

    def measure_density(self):

        time, voltages = self.measure_volts(duration=2)
        voltrho = np.mean(voltages[0])
        rho = self.rho_from_voltrho(voltrho)

        return rho

    #################################################
    # PROFILE DENSITE

    def profile_by_hand(self, file_profile, z, duration=2):

        voltages = np.empty(2)

        # measure voltages

        answer = query.query(
            f"\nPut the probe at z= {z}\n"
            + "Ready? [Y / no, cancel the calibration] "
        )

        if answer.startswith("n"):
            print("Calibration cancelled...")
            return

        volts = self.measure_volts(duration, return_time=False)
        print(volts)
        header = f"profile for z={z}"
        np.savetxt("temp_calib.txt", volts.transpose(), header=header)
        voltages = np.mean(volts, axis=1)
        print("voltrho= {} ; at z=: {} kg/m3".format(volts[0], z))

        self.plot_profile(file_profile, z=z, voltrho=voltages[0])

        if query.query_yes_no("Are you happy with this measurement?"):
            self.save_profile_by_hand(file_profile, z, voltages)

    def save_profile_by_hand(self, file_profile, z, volts):
        """Saves the results of a calibration."""

        print("Save the results of the profile in file:", file_profile)

        z_old, voltrho_old, voltT_old, date_old = self.load_profile(file_profile)

        if _isarray(z_old) and z_old.size >= 1:
            z = np.append(z_old, z)
            voltrho = np.append(voltrho_old, volts[0])
            voltT = np.append(voltT_old, volts[1])
            date = np.append(date_old, time.ctime(int(time.time())))
        else:
            z = np.array(z)
            voltrho = np.array(volts[0])
            voltT = np.array(volts[1])
            date = np.array(time.ctime(int(time.time())))
        if not os.path.exists(file_profile + ".h5"):
            mode = "a"
        else:
            mode = "w"

        with h5py.File(file_profile + ".h5", mode) as f:
            f["z"] = z
            f["voltrho"] = voltrho
            f["voltT"] = voltT
            f["date"] = date

    def load_profile(self, file_profile):
        """Loads the data from the previous profile."""
        z, voltrho, voltT, date = [], [], [], []

        if not file_profile.endswith(".h5"):
            file_profile += ".h5"

        if not os.path.exists(file_profile):
            return z, voltrho, voltT, date

        else:
            with h5py.File(file_profile, "r") as f:
                z = f["z"].value
                voltrho = f["voltrho"].value
                voltT = f["voltT"].value
                date = f["date"].value

        return z, voltrho, voltT, date

    def plot_profile(self, file_profile, z=None, voltrho=None):
        """Plots the measurements of the save profile."""

        # plot
        fig = plt.figure()
        ax = fig.gca()
        ax.set_xlabel(r"$\rho (kg/l)$")
        ax.set_ylabel(r"$z$ (m)")

        # ax.set_xlim([0.95, 1.25])
        z_old, voltrho_old, voltT_old, date_old = self.load_profile(file_profile)
        rho_old = self.rho_from_voltrho(voltrho_old)
        # load all saved profile
        if _isarray(z_old) and z_old.size >= 1:
            ax.plot(rho_old, z_old, "xg")
        if _isarray(z_old) and z_old.size > 1:
            self.fit_profile(rho_old, z_old)
            rhos_for_plot = np.linspace(rho_old.min(), rho_old.max(), 200)
            ax.plot(rhos_for_plot, self.z_from_rho(rhos_for_plot), "k-")

        if z is not None and voltrho is not None:
            ax.plot(self.rho_from_voltrho(voltrho), z, "xr")

        plt.show()

    def plot_profiles(self, file_profiles):
        # file_profile is an array of strings

        for profile in file_profiles:
            z, voltrho, voltT, date = self.load_profile(profile)
            rho = self.rho_from_voltrho(voltrho)
            plt.plot(rho, z)

        plt.title("Density profile")
        plt.xlabel("Density")
        plt.ylabel("Vertical position z")
        plt.grid(True)
        plt.legend(file_profiles)
        plt.show()

    def fit_profile(self, z, rho):
        """Creates a function from data."""
        coeffs = np.polyfit(z, rho, deg=1)
        self.z_from_rho = np.poly1d(coeffs)
        self.coeffsprofile = coeffs

    ###########################################################################
    # CALIBRATION

    def prepare_calibration(self, rho_min=1, rho_max=1.18, nb_solutions=6):
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

    def calibrate(self, rho, T, duration=2.0):
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

        answer = query.query(
            f"\nPut the probe in solution with rho = {rho}\n"
            + "Ready? [Y / no, cancel the calibration] "
        )

        if answer.startswith("n"):
            print("Calibration cancelled...")
            return

        happy = False
        while not happy:
            volts = self.measure_volts(duration, return_time=False)
            header = "calibration for rho=" "{}, T= {}\nVolt rho, Volt T".format(
                rho, T
            )
            np.savetxt("tmp_calib.txt", volts.transpose(), header=header)
            voltages = volts.mean(axis=1)
            print("solution rho: {} kg/l; voltage: {}".format(rho, voltages[0]))
            # print('solution T: {} ; voltage: {} V'.format(T, voltages[1]))
            happy = query.query_yes_no("Are you happy with this measurement?")

        self.plot_calibration(rho=rho, voltrho=voltages[0])

        if query.query_yes_no("Should the new point be saved?"):
            self.save_calibration(rho, T, voltages, "rho")

    def calibrate_temperature(self, rho, T, duration=2.0):
        r"""Calibrates the temperature probe.

        Parameters
        ----------
        rho :
           The density :math:`\rho` of the sample (in kg/l).

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

        answer = query.query(
            f"\nPut the probe in solution at T = {T}\n"
            + "Ready? [Y / no, cancel the calibration] "
        )

        if answer.startswith("n"):
            print("Calibration cancelled...")
            return

        happy = False
        while not happy:
            volts = self.measure_volts(duration, return_time=False)
            header = (
                "calibration for rho="
                "{}, T= {} \n Volt rho, Volt T".format(rho, T)
            )
            np.savetxt("tmp_calib.txt", volts.transpose(), header=header)
            voltages = np.mean(volts, axis=1)
            print("solution T: {} ; voltage: {} V".format(T, voltages[1]))
            happy = query.query_yes_no("Are you happy with this measurement?")

        self.plot_calibration_T(T=T, voltT=voltages[1])

        if query.query_yes_no("Should the new point be saved?"):
            self.save_calibration(rho, T, voltages, "T")

    def save_calibration(self, rho, T, volts, kind_of_calib):
        """Saves the results of a calibration."""

        if kind_of_calib == "rho":
            file_calib = self.files_calib[0]
        elif kind_of_calib == "T":
            file_calib = self.files_calib[1]
        file_calib += ".h5"

        print("Save the results of the calibration in file:", file_calib)

        rho_old, voltrho_old, T_old, voltT_old, date_old = self.load_calibration(
            kind_of_calib
        )

        if _isarray(rho_old) and rho_old.size >= 1:
            rho = np.append(rho_old, rho)
            voltrho = np.append(voltrho_old, volts[0])
            if self._has_temp:
                T = np.append(T_old, T)
                voltT = np.append(voltT_old, volts[1])
            date = np.append(date_old, time.ctime(int(time.time())))
        else:
            rho = np.array(rho)
            voltrho = np.array(volts[0])
            if self._has_temp:
                T = np.array(T)
                voltT = np.array(volts[1])
            date = np.array(time.ctime(int(time.time())))
        if not os.path.exists(file_calib):
            mode = "a"
        else:
            mode = "w"

        with h5py.File(file_calib, mode) as f:
            f["rho"] = rho
            f["voltrho"] = voltrho
            if self._has_temp:
                f["T"] = T
                f["voltT"] = voltT
            f["date"] = date

    def load_calibration(self, kind_of_calib):
        """Loads the data from the previous calibrations."""

        if kind_of_calib == "rho":
            file_calib = self.files_calib[0]
        elif kind_of_calib == "T":
            file_calib = self.files_calib[1]
        file_calib += ".h5"

        return load_calibration(file_calib)

    def plot_calibration(self, rho=None, voltrho=None):
        """Plots the measurements of the saved calibrations for rho."""

        # plot
        fig = plt.figure()
        ax = fig.gca()

        ax.set_xlabel(r"$\rho$")
        ax.set_ylabel(r"$U$ (V)")

        # ax.set_xlim([0.95, 1.25])

        # load all saved calibrations
        rho_old, voltrho_old, T_old, voltT_old, date_old = self.load_calibration(
            "rho"
        )
        if _isarray(rho_old) and rho_old.size >= 1:
            ax.plot(rho_old, voltrho_old, "xg")
        if _isarray(rho_old) and rho_old.size > 1:
            self.fit_rho_vs_voltrho(rho_old, voltrho_old)
            volts_for_plot = np.linspace(
                voltrho_old.min(), voltrho_old.max(), 200
            )
            ax.plot(self.rho_from_voltrho(volts_for_plot), volts_for_plot, "k-")

        if rho is not None and voltrho is not None:
            ax.plot(rho, voltrho, "xr")

        plt.show()

    def plot_calibration_T(self, T=None, voltT=None):
        """Plots the measurements of the saved calibrations for T."""

        fig = plt.figure()
        ax = fig.gca()
        ax.set_xlabel(r"$T (C)$")
        ax.set_ylabel(r"$U$ (V)")

        # ax.set_xlim([0.95, 1.25])

        # load all saved calibrations
        rho_old, voltrho_old, T_old, voltT_old, date_old = self.load_calibration(
            "T"
        )
        if _isarray(rho_old) and rho_old.size >= 1:
            ax.plot(T_old, voltT_old, "xg")
        if _isarray(rho_old) and rho_old.size > 1:
            self.fit_T_vs_voltT(T_old, voltT_old)
            ax.plot(T_old, voltT_old, "xg")
            volts_for_plot = np.linspace(voltT_old.min(), voltT_old.max(), 200)
            ax.plot(self.T_from_voltT(volts_for_plot), volts_for_plot, "k-")

        if T is not None and voltT is not None:
            ax.plot(T, voltT, "xr")

        plt.show()

    # fits of calibration data points

    def fit_rho_vs_voltrho(self, rho, voltrho):
        """Creates a function from data."""
        if len(rho) < 3:
            deg = 1
        elif len(rho) < 5:
            deg = 2
        else:
            deg = 3
        coeffs = np.polyfit(voltrho, rho, deg=deg)
        self.rho_from_voltrho = np.poly1d(coeffs)
        self.coeffsrho = coeffs

    def T_from_voltT(self, voltT):
        tmp = (np.log(voltT - self.voltToff) - self.coeffsT[1]) / self.coeffsT[0]
        Ti = 1.0 / tmp - 273.15
        return Ti

    def fit_T_vs_voltT(self, T, voltT):
        """Creates a function from data."""
        y = np.log(voltT - self.voltToff)
        x = 1.0 / (T + 273.15)
        self.coeffsT = np.polyfit(x, y, deg=1)
