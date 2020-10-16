import sys
from pathlib import Path
import subprocess

from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext

from runpy import run_path

if sys.version_info[0:2] < (3, 6):
    raise RuntimeError("Python version >= 3.6 required.")

try:
    hg_rev = subprocess.check_output(["hg", "id", "--id"]).strip()
except (OSError, subprocess.CalledProcessError):
    pass
else:
    with open("fluidlab/_hg_rev.py", "w") as f:
        f.write(f'hg_rev = "{hg_rev}"\n')

# Get the long description from the relevant file
with open("README.rst") as file:
    long_description = file.read()
lines = long_description.splitlines(True)
long_description = "".join(lines[14:])

# Get the version from the relevant file
__version__ = run_path("fluidlab/_version.py")["__version__"]

# Get the development status from the version string
if "a" in __version__:
    devstatus = "Development Status :: 3 - Alpha"
elif "b" in __version__:
    devstatus = "Development Status :: 4 - Beta"
else:
    devstatus = "Development Status :: 5 - Production/Stable"

ext_modules = []
setup_requires = []


path_PowerDAQ = Path(r"C:\Program Files (x86)\UEI\PowerDAQ\SDK")
if path_PowerDAQ.exists():
    setup_requires.extend(["Cython >= 0.20", "numpy"])

    if "egg_info" not in sys.argv:

        from Cython.Distutils.extension import Extension
        from Cython.Distutils import build_ext
        import numpy as np

        path_sources = Path("fluiddyn/lab/boards/PowerDAQ")
        ext_PowerDAQ = Extension(
            "fluiddyn.lab.boards.powerdaq",
            include_dirs=[
                path_PowerDAQ / "Include",
                path_sources,
                np.get_include(),
            ],
            libraries=["pwrdaq32"],
            library_dirs=[path_PowerDAQ / r"x64\lib"],
            sources=[path_sources / "powerdaq.pyx"],
        )
        ext_modules.append(ext_PowerDAQ)


install_requires = ["fluiddyn >= 0.3.2", "pyusb", "minimalmodbus"]
# Even though we also use scipy, we don't require its installation
# because it can be heavy to install.

setup(
    name="fluidlab",
    version=__version__,
    description="Framework for studying fluid dynamics by experiments.",
    long_description=long_description,
    keywords="Fluid dynamics, research",
    author="Pierre Augier",
    author_email="pierre.augier@univ-grenoble-alpes.fr",
    url="https://foss.heptapod.net/fluiddyn/fluidlab",
    license="CeCILL-B",
    classifiers=[
        devstatus,
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: BSD License",
        # Actually CeCILL-B License (BSD compatible license for French laws,
        # see http://www.cecill.info/index.en.html
        #
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(exclude=["doc", "digiflow", "examples"]),
    setup_requires=setup_requires,
    install_requires=install_requires,
    scripts=["bin/fluid_stop_pumps.py"],
    cmdclass={"build_ext": build_ext},
    ext_modules=ext_modules,
)
