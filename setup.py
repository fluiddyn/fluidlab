
from setuptools import setup, find_packages

try:
    from Cython.Distutils.extension import Extension
    from Cython.Distutils import build_ext
except ImportError:
    from setuptools import Extension, build_ext
    from distutils.command import build_ext

import os
here = os.path.abspath(os.path.dirname(__file__))

import sys
if sys.version_info[:2] < (2, 7) or (3, 0) <= sys.version_info[0:2] < (3, 2):
    raise RuntimeError("Python version 2.7 or >= 3.2 required.")

# Get the long description from the relevant file
with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()
lines = long_description.splitlines(True)
long_description = ''.join(lines[8:])

# Get the version from the relevant file
execfile('fluidlab/_version.py')
# Get the development status from the version string
if 'a' in __version__:
    devstatus = 'Development Status :: 3 - Alpha'
elif 'b' in __version__:
    devstatus = 'Development Status :: 4 - Beta'
else:
    devstatus = 'Development Status :: 5 - Production/Stable'

ext_modules = []

import numpy as np

path_PowerDAQ = r'C:\Program Files (x86)\UEI\PowerDAQ\SDK'
if os.path.exists(path_PowerDAQ):
    path_sources = 'fluiddyn/lab/boards/PowerDAQ'
    ext_PowerDAQ = Extension(
        'fluiddyn.lab.boards.powerdaq',
        include_dirs=[
            os.path.join(path_PowerDAQ, 'Include'),
            path_sources,
            np.get_include()],
        libraries=["pwrdaq32"],
        library_dirs=[os.path.join(path_PowerDAQ, r'x64\lib')],
        sources=[path_sources+'/powerdaq.pyx'])
    ext_modules.append(ext_PowerDAQ)


setup(name='fluidlab',
      version=__version__,
      description=('Framework for studying fluid dynamics by experiments.'),
      long_description=long_description,
      keywords='Fluid dynamics, research',
      author='Pierre Augier',
      author_email='pierre.augier@legi.cnrs.fr',
      url='https://bitbucket.org/paugier/fluiddyn',
      license='CeCILL',
      classifiers=[
          # How mature is this project? Common values are
          # 3 - Alpha
          # 4 - Beta
          # 5 - Production/Stable
          devstatus,
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'Topic :: Scientific/Engineering',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          # actually CeCILL License (GPL compatible license for French laws)
          #
          # Specify the Python versions you support here. In particular,
          # ensure that you indicate whether you support Python 2,
          # Python 3 or both.
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          # 'Programming Language :: Python :: 3',
          # 'Programming Language :: Python :: 3.3',
          # 'Programming Language :: Python :: 3.4',
          'Programming Language :: Cython',
          'Programming Language :: C',
      ],
      packages=find_packages(exclude=['doc', 'digiflow', 'examples']),
      install_requires=['fluiddyn', 'h5py'],
      extras_require=dict(
          doc=['Sphinx>=1.1', 'numpydoc']),
      scripts=['bin/fluiddyn-stop-pumps'],
      cmdclass={"build_ext": build_ext},
      ext_modules=ext_modules)
