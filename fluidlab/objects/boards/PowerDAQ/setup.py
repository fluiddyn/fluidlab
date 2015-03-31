from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy as np

import os



name = "powerdaq"
path_cy_code = os.getcwd()

libraries = ["pwrdaq32"]

ext_modules = [
    Extension(name,
              [path_cy_code+'/'+name+'.pyx'],
              libraries=libraries,
              include_dirs=[
                  'C:\Program Files (x86)\UEI\PowerDAQ\SDK\Include',
                  np.get_include()],
              library_dirs=[
                  r'C:\Program Files (x86)\UEI\PowerDAQ\SDK\x64\lib'])]

setup(name=name,
      cmdclass={"build_ext": build_ext},
      ext_modules=ext_modules)


path_cy_lib = path_cy_code+'/build/lib.win-amd64-2.7'

name_file_lib = name+'.pyd'


if os.path.isfile(path_cy_lib+'/'+name_file_lib):
    print('Copy new version of the library...')
    if os.path.isfile(path_cy_code+'/../'+name_file_lib+'_old'):
        os.remove(path_cy_code+'/../'+name_file_lib+'_old')

    if os.path.isfile(path_cy_code+'/../'+name_file_lib):
        os.rename(path_cy_code+'/../'+name_file_lib,
                  path_cy_code+'/../'+name_file_lib+'_old')

    os.rename(path_cy_lib+'/'+name_file_lib, path_cy_code+'/../'+name_file_lib)
