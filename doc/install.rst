Installation
============

FluidLab is part of the FluidDyn project.  Some issues regarding the
installation of Python packages are discussed in `the main
documentation of the project
<http://fluiddyn.readthedocs.org/en/latest/install.html>`_.

Dependencies
------------

- Numpy, Scipy, ...

Install commands
----------------
  
FluidSim can be installed by running the following commands::

  hg clone https://bitbucket.org/fluiddyn/fluidlab
  cd fluidlab
  python setup.py develop
 
Installation with Pip should also work::

  pip install fluidlab


Optional dependencies
---------------------


.. toctree::
   :maxdepth: 2

   linuxgpib

  
Run the tests
-------------

You can run some unit tests by running ``make tests`` from the root
directory or ``python -m unittest discover`` from the root directory
or from any of the "test" directories.


