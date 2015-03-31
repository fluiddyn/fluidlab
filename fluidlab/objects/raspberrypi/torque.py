"""Torque measurements (:mod:`fluidlab.objects.raspberrypi.torque`)
===================================================================

Handle measurement, saving, loading and plotting of torque measured by
a gain strain using a Raspberry Pi.

"""


from __future__ import division, print_function

import os
import numpy as np
import datetime
try:
    import rpyc
except ImportError:
    pass

from glob import glob
import shutil

import socket
hostname = socket.gethostname()
hostnames_measuring = ['raspberrypi']


from fluiddyn.util.timer import Timer
from fluiddyn.util import time_as_str
from fluiddyn.io import FLUIDDYN_PATH_EXP
from fluiddyn.io.hdf5 import H5File
import fluiddyn.output.figs as figs

from fluidlab.objects.boards import FalseBoard
if hostname in hostnames_measuring:
    try:
        from fluidlab.objects.raspberrypi.daq import MCP3008SPI
        board = MCP3008SPI(differential=False)
    except (ImportError) as Error:
        print('Warning: ImportError '
              'fluidlab.objects.raspberrypi.daq (use FalseBoard).')
        board = FalseBoard()
        board.Error = Error


class Torque(object):
    """A `Torque` object handles torque measurements."""
    def __init__(self, path_exp=None, name_exp=None):

        if path_exp is None:
            path_exp = FLUIDDYN_PATH_EXP
        self.path_exp = path_exp
        self.path_save = os.path.join(path_exp, 'Torque')

        if not os.path.exists(self.path_save):
            os.makedirs(self.path_save)

        if name_exp is None:
            name_exp = 'No name experiment given.'
        self.name_exp = name_exp






    def load(self, indice_file=-1, times_slice=None):
        """Load the torque measurements contained in a file."""
        path_files = glob(self.path_save+'/torque_*.h5')
        path_files.sort()
        path_file = path_files[indice_file]
        with H5File(path_file, 'r') as f:
            # warning: times_slice can not work!!!
            return f.load(times_slice=times_slice)






    def _plot_in_axis(self, ax, indice_files=-1, times_slice=None):
        if isinstance(indice_files, (list, np.ndarray, tuple)):
            for ind in indice_files:
                self._plot_in_axis(ind)
        else:
            results = self.load(indice_files, times_slice=times_slice)

            volts = results['volts']
            nb_pts = len(volts)
            sample_rate = results['sample_rate']
            ts = np.arange(nb_pts)/sample_rate
            ax.plot(ts, volts, 'x')





    def plot(self, indice_files=-1, in_different_figs=False, 
             times_slice=None):
        if (in_different_figs and 
            isinstance(indice_files, (list, np.ndarray, tuple))
        ):
            for ind in indice_files:
                self.plot(ind)
        else:
            figures = figs.Figures(hastosave=False, 
                                   path_save=self.path_save,
                                   for_beamer=False, 
                                   fontsize=18)

            fig = figures.new_figure(
                fig_width_mm=180, fig_height_mm=135,
                size_axe=[0.135, 0.14, 0.82, 0.81], 
                name_file='fig_torque')

            ax = fig.gca()
            ax.set_xlabel(r'$t$')
            ax.set_ylabel(r'torque')

            self._plot_in_axis(ax, indice_files, times_slice=times_slice)

            # the measured torque is always positive
            xlim = ax.get_ylim()
            ax.set_ylim([0, xlim[1]])
            fig.saveifhasto(format='pdf')
            figs.show()











freq_max = 1e4
class TorqueRaspberryPi(Torque):
    volt_max = 3.26
    volt_per_raw = volt_max/1024
    def __init__(self, path_exp=None, name_exp=None, channel=0,
                 path_exp_client=None, open_client=None):
        if hostname not in hostnames_measuring:
            raise ValueError(
                'A TorqueRaspberryPi should be created on a Raspberry Pi.')

        self.path_exp_client = path_exp_client
        self.open_client = open_client

        if isinstance(board, (FalseBoard)):
            raise board.Error

        self.board = board
        self.channel = channel

        if path_exp is None:
            wdir = os.getcwd()
            if wdir.endswith('Torque'):
                path_exp = wdir.split()[0]

        super(TorqueRaspberryPi, self).__init__(
            path_exp=path_exp, name_exp=name_exp)


    def measure(self, duration, sample_rate, hastosave=True):

        if sample_rate > freq_max:
            print('Warning... danger!')

        nb_pts = int(duration*sample_rate)
        results = np.empty([nb_pts])

        if hastosave:
            if not os.path.exists(self.path_save):
                os.makedirs(self.path_save)

            path_file = (self.path_save+'/torque_'+
                         time_as_str()+'.h5')

            with H5File(path_file,'w') as f:
                f.attrs['time start'] = str(datetime.datetime.now())
                f.attrs['name_dir'] = self.name_exp
                f.attrs['sample_rate'] = sample_rate

        timer = Timer(1/sample_rate)
        for ip in range(nb_pts):
            results[ip] = self.board.convert(self.channel)
            # print('result:', results[ip]*self.volt_per_raw)
            if ip < nb_pts:
                timer.wait_till_tick()

        results *=  self.volt_per_raw # (in volt)

        if hastosave:
            dicttosave = {'volts': results}
            with H5File(path_file, 'r+') as f:
                f.save_dict_of_ndarrays(dicttosave)

        return results


    def copy_files_in_client(self, indice_files=None):
        if self.path_exp_client is None or self.open_client is None:
            raise ValueError(
                'Can not save at client since '
                'path_exp_client or open_client have not been given.')

        if indice_files is None:
            path_files = glob(self.path_save+'/torque_*.h5')
            indice_files = list(range(len(path_files)))
        if isinstance(indice_files, (list, np.ndarray, tuple)):
            for ind in indice_files:
                self.copy_files_in_client(ind)
        else:
            path_files = glob(self.path_save+'/torque_*.h5')
            path_file = path_files[indice_files]

            name_file = os.path.split(path_file)[1]

            path_file_client = os.path.join(
                self.path_exp_client, 'Torque', name_file)

            with open(path_file, 'rb') as flocal:
                with self.open_client(path_file_client, 'wb') as f:
                    shutil.copyfileobj(flocal, f)





class TorqueClient(Torque):
    """"""
    
    def __init__(self, path_exp=None, name_exp=None, 
                 connect=True):

        super(TorqueClient, self).__init__(
            path_exp=path_exp, name_exp=name_exp
            )
            

        if connect:
            # host = 'localhost'
            # host = 'emperor.dampt.cam.ac.uk'
            host = '131.192.168.167'
            self.conn = rpyc.classic.connect(host, 18861)

            self.conn.root.init_with_client(
                FLUIDDYN_PATH_EXP_client=FLUIDDYN_PATH_EXP,
                name_exp=name_exp,
                path_exp_client=path_exp,
                open_client=open
               )

            self.remote_measure = self.conn.root.measure
            self.transfer_from_raspberrypi = self._transfer_from_raspberrypi

    def _transfer_from_raspberrypi(self, indice_files=None):
        if not os.path.exists(self.path_save):
            os.makedirs(self.path_save)

        self.conn.root.torque.copy_files_in_client(
            indice_files=indice_files)

    def __getattr__(self, key):
        if key in ['remote_measure', 'transfer_from_raspberrypi']:
            raise ValueError(
                'Since the argument of the constructor `connect` was False. '
                'You can not use the function '+key+
                ' that needs the connection.')













if __name__ == '__main__':

    if hostname in hostnames_measuring:
        torque = TorqueRaspberryPi()
        # volts = torque.measure(duration=5, sample_rate=2)
        # print(volts)
    else:

        from fluidlab.utils import load_exp
        str_path_save = 'Exp_Omega=0.75_N0=1.83_2014-06-25'
        exp = load_exp(str_path_save=str_path_save, 
                       NEED_BOARD=False)

        torque = TorqueClient(
            path_exp=exp.path_save, name_exp=exp.name_dir, 
            connect=True)




