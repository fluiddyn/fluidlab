"""
Laboratory experiments (:mod:`fluidlab`)
============================================

.. _lab:
.. currentmodule:: fluidlab

The package :mod:`fluidlab` contains:

- a package gathering the experiment classes:

.. autosummary::
   :toctree:

   exp

- a package to use some acquisition boards:

.. autosummary::
   :toctree:

   boards

- some modules to represent and control devices:

.. autosummary::
   :toctree:

   tanks
   pumps
   probes
   pinchvalve
   traverse
   rotatingobjects

- a package to use a `Raspberry Pi <http://www.raspberrypi.org>`_:

.. autosummary::
   :toctree:

   raspberrypi


"""

from fluidlab._version import __version__

from fluiddyn.util.util import load_exp
