========
FluidLab
========

|release| |pyversions| |docs| |coverage| |heptapod_ci| |travis|

.. |release| image:: https://img.shields.io/pypi/v/fluidlab.svg
   :target: https://pypi.python.org/pypi/fluidlab/
   :alt: Latest version

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/fluidlab.svg
   :alt: Supported Python versions

.. |docs| image:: https://readthedocs.org/projects/fluidlab/badge/?version=latest
   :target: http://fluidlab.readthedocs.org
   :alt: Documentation status

.. |coverage| image:: https://codecov.io/gh/fluiddyn/fluidlab/branch/branch%2Fdefault/graph/badge.svg
   :target: https://codecov.io/gh/fluiddyn/fluidlab
   :alt: Code coverage

.. |heptapod_ci| image:: https://foss.heptapod.net/fluiddyn/fluidlab/badges/branch/default/pipeline.svg
   :target: https://foss.heptapod.net/fluiddyn/fluidlab/-/pipelines
   :alt: Heptapod CI

.. |travis| image:: https://travis-ci.org/fluiddyn/fluidlab.svg
   :target: https://travis-ci.org/fluiddyn/fluidlab
   :alt: Travis CI status

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

With a recent version of `pip`, one can use::

  pip install fluidlab

Alternatively, one can install from source, which are available from `Heptapod
<https://foss.heptapod.net/fluiddyn/fluidlab>`__. From the root directory of
the repository::

  pip install -e .

Tests
-----

From the root directory or from any of the "test" directories, run::

  pytest
