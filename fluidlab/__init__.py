"""
Laboratory experiments (:mod:`fluidlab`)
========================================

.. _lab:
.. currentmodule:: fluidlab

The package :mod:`fluidlab` contains:

.. autosummary::
   :toctree: generated/

   objects
   exp
   postproc
   output

"""

from __future__ import print_function

from fluidlab._version import __version__

try:
    from fluidlab.util import load_exp
    
    import fluiddyn as fld
    fld.load_exp = load_exp
    del fld
except AttributeError:
    # Some older Python versions do not have os.getppid() and
    # therefore load_exp import fails.
    # Not all setups require load_exp, therefore issue a warning
    # here instead of raising an uncaught exception.
    print('Warning: load_exp is not available.')
