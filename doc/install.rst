Installation
============

FluidLab is part of the FluidDyn project.  Some issues regarding the
installation of Python packages are discussed in `the main
documentation of the project
<http://fluiddyn.readthedocs.org/en/latest/install.html>`_.

Dependencies
------------

Fluidlab uses some very common scientific Python packages. They will
be installed automatically during fluidlab install but it can actually
be better to install them before.

- Numpy, Matplotlib, h5py

Other dependencies will be installed automatically and you do not have
to worry about:

- pyusb, minimalmodbus

Optional dependencies
---------------------

Some packages are used for some quite particular tasks. Just install
them if needed:

- Cython, Scipy

We give some advises for packages that are not very easy to install:

.. toctree::
   :maxdepth: 2

   linuxgpib
   
  
Install commands
----------------

The simplest way to install fluidlab is by using pip::

  pip install fluidlab

However, since the package is still in alpha phase (testing for
developers), it is often useful to install it from source in "develop"
mode. To download the source, the easier is to use Mercurial::

  hg clone https://bitbucket.org/fluiddyn/fluidlab
  cd fluidlab
  python setup.py develop


After the installation, try to run the unit tests by running ``make
tests`` from the root directory or ``python -m unittest discover``
from the root directory or from any of the "test" directories.


