"""Experiment classes
=====================

.. _exp:

.. autosummary::
   :toctree:

   session
   octavesession

.. warning::

   Beware, most of the modules of this package (those listed below)
   are depreciated and will be at least rewritten with other base
   class.

Physically, an experiment consists in interacting objects.  The
experimentalist wants to control the actions of the objects with a
good control in space and time and in a reproducible way. The results
are then some measurements about the studied physical phenomenon
produced by the measuring objects.  Usually, after the experiment has
been set up, it is repeted a number of times in order to vary some
parameters.

A experimental set-up is represented in FluidDyn by a class derived
from the class :class:`fluidlab.exp.base.Experiment`.  The
experiment class has attributes that represent the physical objects
interacting in the experimental set-up (composition).

Each realisation of the experimental set-up (with a particular set of
parameters) is represented by an instance of the experiment
class. Each experiment (each realisation) is associated with a
directory.

This package provides:

- some modules defining classes to represent base experiments:

.. autosummary::
   :toctree:

   base
   withtank
   withconductivityprobe

- a package with classes representing Taylor-Couette experiments:

.. autosummary::
   :toctree:

   taylorcouette

- other very simple classes derived from
  :class:`fluidlab.exp.withtank.ExperimentWithTank` and
  :class:`fluidlab.exp.withconductivityprobe.ExpWithConductivityProbe`,
  respectively:

.. autosummary::
   :toctree:

   doublediffusion
   vertduct

"""

from .session import Session
from fluiddyn.util.timer import Timer
