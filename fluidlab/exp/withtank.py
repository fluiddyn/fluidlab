"""
Experiments with a tank (:mod:`fluidlab.exp.withtank`)
==========================================================

.. currentmodule:: fluidlab.exp.withtank

Provides:

.. autoclass:: ExperimentWithTank
   :members:
   :private-members:
   :show-inheritance:

"""

from __future__ import division, print_function

import numpy as np
import os

import datetime
import time

import glob
import json
import h5py
import inspect
from importlib import import_module

import fluiddyn
from fluiddyn.io.hdf5 import H5File

from fluiddyn.util import query
from fluiddyn.util.timer import Timer

from fluidlab.objects.tanks import StratifiedTank

from fluidlab.exp.base import Experiment

import fluiddyn.output.figs as figs

nu_pure_water = fluiddyn.constants.nu_pure_water



import sys
if sys.platform.startswith('win'):
    import win32api, thread
    def handler(sig, hook=thread.interrupt_main):
        hook()
        return 1


class ExperimentWithTank(Experiment):
    """Represent an experiment with a tank.

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
    There are two modes of creating an :class:`ExperimentWithTank`:

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
    _base_dir = 'With_tank'

    def __init__(self, rhos=None, zs=None,
                 params=None, description=None,
                 str_path=None):

        # start the init. and find out if it is the first creation
        self._init_from_str(str_path)

        if self.first_creation:

            # initialise `params` with `params` and the other parameters
            if params is None:
                params = {}
            if rhos is not None:
                params['rhos'] = rhos
            if zs is not None:
                params['zs'] = zs

            # verify if enough params have been given for the first creation
            self._verify_params_first_creation(
                params, 
                keys_needed=['rhos', 'zs']
            )

        # call the __init__ function of the inherited class
        super(ExperimentWithTank, self).__init__(
            params=params, description=description,
            str_path=str_path
            )

        # then, the tank!
        if self.first_creation:
            self._create_tank()
            self._save_tank()
        else:
            self._load_tank()









    def _create_self_params(self, params):
        r"""Calculate some parameters.

        First, call the function `_create_self_params` of the
        inherited class.  Then, update the instance variable `params`
        with the viscosity :math:`\nu` (m^2/s) and the maximum density
        difference :math:`\Delta \rho = \max\rho - \min\rho` (g/cm^3).

        Parameters
        ----------
        params : dict
            Containing parameters.

        """
        super(ExperimentWithTank, self)._create_self_params(params)

        if len(params) == 0:
            return

        rhos = params['rhos']
        Delta_rho = rhos[0] - rhos[-1]

        self.params.update({
            'nu':nu_pure_water,
            'Delta_rho':Delta_rho
        })





    def _create_tank(self):
        """Create the instance variable representing the tank.

        Here, `tank` represents a simple stratified tank
        (:class:`fluidlab.objects.tanks.StratifiedTank`).

        """
        if 'H' in self.params:
            H = dict_tank['H']
        else:
            H = 460

        if 'S' in self.params:
            S = dict_tank['S']
        else:
            S = 80**2

        if 'zs' in self.params:
            zs = self.params['zs']
            rhos = self.params['rhos']
        else:
            zs = [0, H]
            rhos = [1.2, 1.]

        self.tank = StratifiedTank(H=450, S=80**2, z=zs, rho=rhos)


    def _save_tank(self):
        """Save the object representing the tank."""
        self.tank.save(self.path_save)
        path_h5_file = self.path_save+'/params.h5'
        with H5File(path_h5_file, 'r+') as f:
            f.update_dict(
                'classes', 
                dicttosave={'tank': self.tank.__class__.__name__})
            f.update_dict(
                'modules', 
                dicttosave={'tank': self.tank.__module__})


    def _load_tank(self, verbose=False):
        """Load the object representing the tank."""
        path_h5_file = self.path_save+'/tank.h5'
        if os.path.exists(path_h5_file):
            self.tank = fluiddyn.create_object_from_file(path_h5_file)
        else:
            raise ValueError(
"""WithTank experiment without tank.h5 file. path_save:
"""+self.path_save)













if __name__ == '__main__':


    def test_fill_tank():

        rho_max = 1.084
        rho_min = 1.
        Delta_rho = rho_max - rho_min

        z_max = 400
        zs = z_max*np.array([0, 1./6, 5./6, 1])
        rhos = rho_min + Delta_rho*np.array([1., 0.5, 0.5, 0.])


        exp = ExperimentWithTank(
            description='Test fill tank.', params={}, 
            str_path='Test'
            )

        exp.tank.fill()

        return tank




    # exp = ExperimentWithTank(
    #     rhos=[1.1, 1], zs=[0, 200],
    #     description='Test fill tank.', params={'a':2}, 
    #     )

    # test_fill_tank()

    exp = fluiddyn.load_exp('Exp_2014-08-16_20-39-13')
