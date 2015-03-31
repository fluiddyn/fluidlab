"""create_exp_TC_lin.py: create an ILSTaylorCouetteExp
------------------------------------------------------

Use the parameters defined in params_creation_TC_lin.py to create an
object of the class
:class:`fluidlab.exp.taylorcouette.linearprofile.ILSTaylorCouetteExp`,
i.e. an object representing a Taylor-Couette experiment with a
stratified fluid (Initially Linear Stratification).

"""
from __future__ import division, print_function

import params_creation_TC_lin as p
reload(p)

from fluidlab.exp.taylorcouette.linearprofile import ILSTaylorCouetteExp

from fluiddyn.util.query import query_yes_no

if __name__ == '__main__':

    exp = ILSTaylorCouetteExp(
        rho_min=p.rho_min, rho_max=p.rho_max,
        N0=p.N0,
        Omega1=p.Omega1, Omega2=p.Omega2,
        R1=p.R1, R2=p.R2,
        prop_homog=p.prop_homog,
        description=p.description
    )

    print(
        'Create experiment with\n'
        'exp.name_dir:\n    '+exp.name_dir+
        '\nexp.path_save:\n    '+exp.path_save)

    ok = query_yes_no("""
    Do you want to add a "str_path=..." in str_path_working_exp.py
    in order to set this experiment as the working experiment?
    """
    )
    if ok:
        with open('str_path_working_exp.py', 'a') as f:
            f.write("""
str_path = '"""+exp.name_dir+"""'
""")

        with open('path_working_exp.txt', 'w') as f:
            f.write(exp.path_save)
