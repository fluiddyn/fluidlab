""".py: 
---------------------------------------------------------------


"""

from __future__ import division, print_function

import str_path_working_exp
reload(str_path_working_exp)
str_path = str_path_working_exp.str_path


import fluiddyn as fld

if __name__ == '__main__':

    exp = fld.load_exp(str_path)

