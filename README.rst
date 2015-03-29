========
FluidDyn
========

*Framework for studying fluid dynamics by experiments and simulations.*

`Package Documentation <http://pythonhosted.org/fluiddyn>`__

FluidDyn is a framework for studying fluid dynamics by experiments and
numerical simulations using Python.  The project is still in a testing
stage so it is still pretty unstable and many of its planned features
have not yet been implemented.

It is the evolution of two other projects previously developed by
`Pierre Augier
<http://www.legi.grenoble-inp.fr/people/Pierre.Augier/>`_ (CNRS
researcher at `LEGI <http://www.legi.grenoble-inp.fr>`_, Grenoble):
Solveq2d (a numerical code to solve fluid equations in a periodic
two-dimensional space with a pseudo-spectral method, developed at KTH,
Stockholm) and FluidLab (a toolkit to do experiments, developed in
the G. K. Batchelor Fluid Dynamics Laboratory at DAMTP, University of
Cambridge).

*Key words and ambitions*: fluid dynamics research with Python (2.7 or
>= 3.3); modular, object-oriented, collaborative, tested and
documented, free and open-source software.

License
-------

FluidDyn is distributed under the CeCILL_ License, a GPL compatible
french license.

.. _CeCILL: http://www.cecill.info/index.en.html

Installation
------------

You can get the source code from `Bitbucket
<https://bitbucket.org/paugier/fluiddyn>`__ or from `the Python
Package Index <https://pypi.python.org/pypi/fluiddyn/>`__.

The development mode is often useful. From the root directory::

  sudo python setup.py develop

Tests
-----

From the root directory::

  python run_tests.py

Or, from the root directory or from any of the "test" directories::

  python -m unittest discover