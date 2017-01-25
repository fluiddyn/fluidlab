"""
Toolkit for various tasks (:mod:`fluidlab.util.util`)
=====================================================


"""
from __future__ import print_function

import os
import glob
from importlib import import_module

import numpy as np
import h5py

from fluiddyn import io


def load_exp(str_path=None, *args, **kwargs):
    """Load an experiment from the disk."""
    if str_path is None:
        str_path = os.getcwd()

    path = None
    if os.path.isabs(str_path):
        path = str_path

    depth_path_max = 5
    idepth = -1
    while path is None and idepth < depth_path_max:
        idepth += 1
        paths = glob.glob(io.FLUIDLAB_PATH+'/' +
                          idepth*'*/' + '*' + str_path + '*')
        if len(paths) > 0:
            path = paths[0]

    if path is None:
        raise ValueError(
            """Haven't been able to find a path corresponding to str_path.
You can try to increase the value of the constant depth_path_max
(FLUIDLAB_PATH: {}
str_path: {}).""".format(io.FLUIDLAB_PATH, str_path))

    path_h5_file = path + '/params.h5'

    # temporary... for compatibility
    with h5py.File(path_h5_file, 'r+') as f:
        keys = f.attrs.keys()
        if 'name_class_exp' in keys and 'class_name' not in keys:
            f.attrs['class_name'] = f.attrs['name_class_exp']
        if 'module_exp' in keys and 'module_name' not in keys:
            f.attrs['module_name'] = f.attrs['module_exp']

    with h5py.File(path_h5_file, 'r') as f:
        class_name = f.attrs['class_name']
        module_exp = f.attrs['module_name']

    if isinstance(class_name, np.ndarray):
        class_name = class_name[0]
        module_exp = module_exp[0]

    # fromlist has to be a not-empty so that __import__('A.B',
    # ...)  returns B rather than A.
    # module_exp = __import__(module_exp, fromlist=['not empty str'])

    module_exp = import_module(module_exp)
    Exp = module_exp.__dict__[class_name]

    return Exp(*args, str_path=path, **kwargs)
