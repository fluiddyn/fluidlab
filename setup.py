
import os
import sys
import subprocess

from setuptools import setup, find_packages

from runpy import run_path

try:
    from Cython.Distutils.extension import Extension
    from Cython.Distutils import build_ext
    has_cython = True
except ImportError:
    from setuptools import Extension
    from distutils.command.build_ext import build_ext
    has_cython = False

if sys.version_info[:2] < (2, 7) or (3, 0) <= sys.version_info[0:2] < (3, 2):
    raise RuntimeError("Python version 2.7 or >= 3.2 required.")

try:
    hg_rev = subprocess.check_output(['hg', 'id', '--id']).strip()
except (OSError, subprocess.CalledProcessError):
    pass
else:
    with open('fluidlab/_hg_rev.py', 'w') as f:
        f.write('hg_rev = "{}"\n'.format(hg_rev))

# Get the long description from the relevant file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()
lines = long_description.splitlines(True)
long_description = ''.join(lines[14:])

# Get the version from the relevant file
d = run_path('fluidlab/_version.py')
__version__ = d['__version__']

# Get the development status from the version string
if 'a' in __version__:
    devstatus = 'Development Status :: 3 - Alpha'
elif 'b' in __version__:
    devstatus = 'Development Status :: 4 - Beta'
else:
    devstatus = 'Development Status :: 5 - Production/Stable'

ext_modules = []

path_PowerDAQ = r'C:\Program Files (x86)\UEI\PowerDAQ\SDK'
if os.path.exists(path_PowerDAQ):
    import numpy as np
    path_sources = 'fluiddyn/lab/boards/PowerDAQ'
    ext_PowerDAQ = Extension(
        'fluiddyn.lab.boards.powerdaq',
        include_dirs=[
            os.path.join(path_PowerDAQ, 'Include'),
            path_sources,
            np.get_include()],
        libraries=["pwrdaq32"],
        library_dirs=[os.path.join(path_PowerDAQ, r'x64\lib')],
        sources=[path_sources + '/powerdaq.pyx'])
    ext_modules.append(ext_PowerDAQ)


install_requires = ['fluiddyn >= 0.0.12a0', 'pyusb', 'minimalmodbus']
# Even though we also use scipy, we don't require its installation
# because it can be heavy to install.
if has_cython:
    # Older versions of Cython cause setup.py to fail.
    # Rmq: Which version? The requirement >= 0.23 seems too strong.
    install_requires += ['Cython >= 0.20']


on_rtd = os.environ.get('READTHEDOCS')
if not on_rtd:
    install_requires.append('h5py')


setup(name='fluidlab',
      version=__version__,
      description='Framework for studying fluid dynamics by experiments.',
      long_description=long_description,
      keywords='Fluid dynamics, research',
      author='Pierre Augier',
      author_email='pierre.augier@legi.cnrs.fr',
      url='https://bitbucket.org/paugier/fluiddyn',
      license='CeCILL-B',
      classifiers=[
          # How mature is this project? Common values are
          # 3 - Alpha
          # 4 - Beta
          # 5 - Production/Stable
          devstatus,
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'Topic :: Scientific/Engineering',
          'License :: OSI Approved :: BSD License',
          # Actually CeCILL-B License (BSD compatible license for French laws,
          # see http://www.cecill.info/index.en.html
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
          'Programming Language :: Cython'],
      packages=find_packages(exclude=['doc', 'digiflow', 'examples']),
      install_requires=install_requires,
      extras_require={'doc': ['Sphinx>=1.1', 'numpydoc']},
      scripts=['bin/fluid_stop_pumps.py'],
      cmdclass={"build_ext": build_ext},
      ext_modules=ext_modules)
