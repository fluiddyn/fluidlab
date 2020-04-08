.. warning ::

   Our repositories in Bitbucket.org will soon be deleted! Our new home:
   https://foss.heptapod.net/fluiddyn (`more details
   <https://fluiddyn.readthedocs.io/en/latest/advice_developers.html>`_).

========
FluidLab
========

|release| |docs| |coverage| |travis|

.. |release| image:: https://img.shields.io/pypi/v/fluidlab.svg
   :target: https://pypi.python.org/pypi/fluidlab/
   :alt: Latest version

.. |docs| image:: https://readthedocs.org/projects/fluidlab/badge/?version=latest
   :target: http://fluidlab.readthedocs.org
   :alt: Documentation status

.. |coverage| image:: https://codecov.io/gh/fluiddyn/fluidlab/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/fluiddyn/fluidlab

.. |travis| image:: https://travis-ci.org/fluiddyn/fluidlab.svg?branch=master
   :target: https://travis-ci.org/fluiddyn/fluidlab

FluidLab is the package of the `FluidDyn project
<http://fluiddyn.readthedocs.org>`__ for doing laboratory experiments.

An earlier version has first been developed by `Pierre Augier
<http://www.legi.grenoble-inp.fr/people/Pierre.Augier/>`_ (CNRS researcher at
`LEGI <http://www.legi.grenoble-inp.fr>`_, Grenoble) in the G. K. Batchelor
Fluid Dynamics Laboratory at DAMTP, University of Cambridge.

*Key words and ambitions*: fluid dynamics research with Python (>= 3.6);
modular, object-oriented, collaborative, tested and documented, free and
open-source software.

License
-------

FluidDyn is distributed under the CeCILL-B_ License, a BSD compatible french
license.

.. _CeCILL-B: http://www.cecill.info/index.en.html

Installation
------------

You can get the source code from `Heptapod
<https://foss.heptapod.net/fluiddyn/fluidlab>`__ or from `the Python Package Index
<https://pypi.python.org/pypi/fluidlab/>`__.

The development mode is often useful. From the root directory::

  pip install -e .

Tests
-----

From the root directory::

  make tests

Or, from the root directory or from any of the "test" directories::

  pytest
