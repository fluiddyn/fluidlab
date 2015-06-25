========
FluidLab
========

*Framework for studying fluid dynamics by laboratory experiments.*

`Package Documentation <http://pythonhosted.org/fluidlab>`__

FluidLab is the package of the `FluidDyn project
<http://pythonhosted.org/fluiddyn>`__ for doing laboratory
experiments.  The project is still in a testing stage so it is still
pretty unstable and many of its planned features have not yet been
implemented.

An earlier version has first been developed by `Pierre Augier
<http://www.legi.grenoble-inp.fr/people/Pierre.Augier/>`_ (CNRS
researcher at `LEGI <http://www.legi.grenoble-inp.fr>`_, Grenoble) in
the G. K. Batchelor Fluid Dynamics Laboratory at DAMTP, University of
Cambridge.

*Key words and ambitions*: fluid dynamics research with Python (2.7 or
>= 3.3); modular, object-oriented, collaborative, tested and
documented, free and open-source software.

License
-------

FluidDyn is distributed under the CeCILL-B_ License, a BSD compatible
french license.

.. _CeCILL-B: http://www.cecill.info/index.en.html

Installation
------------

You can get the source code from `Bitbucket
<https://bitbucket.org/fluiddyn/fluidlab>`__ or from `the Python
Package Index <https://pypi.python.org/pypi/fluidlab/>`__.

The development mode is often useful. From the root directory::

  sudo python setup.py develop

Tests
-----

From the root directory::

  make tests

Or, from the root directory or from any of the "test" directories::

  python -m unittest discover
