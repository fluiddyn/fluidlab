"""
Base Experiments (:mod:`fluidlab.exp.base`)
===============================================

.. currentmodule:: fluidlab.exp.base

Provides:

.. autoclass:: Experiment
   :members:
   :private-members:

"""

from __future__ import division, print_function

import numpy as np
import os
import shutil

import datetime
# import time

# import glob
import json
# import h5py
import inspect
# from importlib import import_module

import fluiddyn
from fluiddyn.io import FLUIDLAB_PATH
from fluiddyn.io.hdf5 import H5File

from fluiddyn.util import time_as_str


import sys
if sys.platform.startswith('win'):
    import win32api, thread

    def handler(sig, hook=thread.interrupt_main):
        hook()
        return 1


class NumpyAwareJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray) and obj.ndim == 1:
                return [x for x in obj]
        return json.JSONEncoder.default(self, obj)


class Experiment(object):
    """Base class for classes representing an experiment.

    Parameters
    ----------
    (for the __init__ method)

    params : dict, optional
        Contain parameters.

    description : str, optional
        A description of the experiment.

    str_path : str, optional
        A string related to the path where the experiment is saved
        or will be saved.

    Notes
    -----
    There are two modes of creating an :class:`Experiment`:

    1. if `str_path` doesn't point on an already saved experiment, a
       new experiment is created (the instance variable
       `first_creation` is True).

    2. if `str_path` points on an already saved experiment, the instance
       variable `first_creation` is False and the experiment is loaded.

    Note that if you want to load an already saved experiment, it is
    more convenient to use the function :func:`fluiddyn.load_exp` like
    so::

        exp = fld.load_exp('Omega=0.73_N0=1.83_2014-03-25_12-43-48')

    Attributes
    ----------
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
    _base_dir = 'Base_exp'

    def __init__(self, params=None,
                 description=None,
                 str_path=None
                 ):

        # start the init. and find out if it is the first creation
        self._init_from_str(str_path)

        if self.first_creation:
            # create self.params from params
            self._create_self_params(params)
            # init self.description
            if description is not None:
                self.description = description
            else:
                self.description = 'Experiment'
            # init name from self.params
            self._init_name_dir()
            # end init and save on the hard disk
            self._save_basic_infos()
        else:
            # load from hard disk
            self._load_basic_infos()
            # recompute the parameters...
            self._create_self_params(self.params)

        # This corrects a bug that I do not understand...
        if sys.platform.startswith('win'):
            win32api.SetConsoleCtrlHandler(handler, 1)

    def _init_from_str(self, str_path):
        """Basic initialisation (begin of path_save and first_creation).

        This function can be run at the beginning of the __init__
        function of all classes representing experiments. If the
        instance has no attribute first_creation, it finds out if it
        is the first creation of the experiment or if it has to be
        loaded from the disk.

        Parameters
        ----------
        str_path : str
            A string related to the path where the experiment is saved
            or will be saved.

        """
        if not hasattr(self, 'first_creation'):
            join = os.path.join
            if str_path is not None:
                str_path = os.path.expanduser(str_path)
            if str_path is None:
                self.path_save = join(FLUIDLAB_PATH, self._base_dir)
            elif os.path.isabs(str_path):
                self.path_save = str_path
            elif not str_path.startswith(self._base_dir):
                self.path_save = join(FLUIDLAB_PATH,
                                      self._base_dir, str_path)
            else:
                self.path_save = join(FLUIDLAB_PATH, str_path)
            self.first_creation = not os.path.exists(
                join(self.path_save, 'params.h5'))

    def _create_self_params(self, params):
        """Initialise the dictionary params.

        This function can be overridden in children classes. Then, the
        function should call ... ???

        """
        if params is None:
            self.params = {}
        else:
            self.params = params

    def _verify_params_first_creation(self, params, keys_needed):
        """Verify the parameters during the first creation.

        Parameters
        ----------
        params : dict
            A dictionary with parameters.

        keys_needed : list
            The keys needed for a class.

        """
        for k in keys_needed:
            if k not in params:
                raise AttributeError(
                    'This class needs the key "{}".'.format(k))

    def _init_name_dir(self):
        """Initialise the name of the directory where the data are saved.

        Initialises `name_dir` as `begin+end`, with `begin = 'Exp_'`
        and `end` codes the time of creation, then returns (`begin`,
        `end`).

        This function can be overridden in children classes.

        Returns
        -------
        begin : str
            equal to `'Exp_'`.
        end : str
            coding the time of creation.

        """
        begin = 'Exp_'
        end = time_as_str()
        self.name_dir = begin+end
        return begin, end

    def _complete_description(self, description_class, description=None):
        """Complete or create a descrition.

        If `description` is None, returns `description_class`;
        otherwise, retruns the concatenation of the two strings.

        Parameters
        ----------
        description_class : str
            A description.

        description : str, optional
            Another description.

        """
        if description is None:
            return description_class
        else:
            return description_class+description

    def _save_basic_infos(self):
        """Save some basic information on the experiment."""
        self.path_save = os.path.join(self.path_save, self.name_dir)
        self.time_start = str(datetime.datetime.now())
        if not os.path.exists(self.path_save):
            os.makedirs(self.path_save)

        path_h5_file = self.path_save+'/params.h5'
        path_txt_file = self.path_save+'/description.txt'

        if (os.path.exists(path_h5_file) or
                os.path.exists(path_txt_file)):
            raise ValueError(
                'Cannot save in the directory\n' + self.path_save +
"""because at least one file where the data should be saved already
exists.""")

        with H5File(path_h5_file, 'w') as f:
            f.attrs['class_name'] = self.__class__.__name__

            module_exp = self.__module__
            if module_exp == '__main__':
                # if the module where the class is defined has been
                # run as a script, module_exp == '__main__' and this
                # is not an useful information to save.
                path_mod = os.path.abspath(inspect.getsourcefile(
                    self.__class__))
                namep = 'fluiddyn'
                if namep in path_mod:
                    pypath_mod = namep+path_mod.split(namep, 1)[1][:-3]
                    module_exp = pypath_mod.replace(
                        '/', '.').replace('\\', '.')
                else:
                    raise ValueError(
"""Experiment classes has to be defined in the package, otherwise they
can not be loaded automatically. Otherwise, you can properly import
the module (such as __name__ != '__main__') and it should work.""")

            f.attrs['module_name'] = str(module_exp)

            f.attrs['time start'] = self.time_start
            f.attrs['name_dir'] = self.name_dir
            f.attrs['description'] = self.description

            f.save_dict('params', self.params)

            f.save_dict('classes', {})
            f.save_dict('modules', {})

        with open(path_txt_file, 'w') as f:
            f.write(
"""This file was created by the Python software FluidDyn {}.\n
""".format(fluiddyn.__version__))

            f.write('description = """'+self.description+'"""')
            f.write('\n\nparameters = ')
            f.write(json.dumps(
                self.params, sort_keys=True,
                cls=NumpyAwareJSONEncoder, indent=2
            )+'\n')

    def _load_basic_infos(self, verbose=False):
        """Load some basic information on the experiments."""
        path_h5_file = self.path_save+'/params.h5'
        with H5File(path_h5_file, 'r') as f:
            self.time_start = f.attrs['time start']
            self.name_dir = f.attrs['name_dir']
            self.description = f.attrs['description']
            self.params = f.load_dict('params')

    def save_script(self):
        """Save the file from where this function is called."""
        dest = os.path.join(self.path_save, 'Saved_scripts')
        if not os.path.exists(dest):
            os.mkdir(dest)
        stack = inspect.stack()
        path_caller = stack[1][1]
        name_file = os.path.basename(path_caller)
        name_file_dest = name_file+'_'+time_as_str()
        shutil.copyfile(path_caller, os.path.join(dest, name_file_dest))


if __name__ == '__main__':

    exp = Experiment(
        params=None,
        description=None,
        str_path=None)

    # exp = fluiddyn.load_exp('Exp_2014-08-16_15-47-00')
