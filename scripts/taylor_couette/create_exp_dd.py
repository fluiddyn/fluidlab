"""create_exp_dd.py: create a DoubleDiffusion experiment
--------------------------------------------------------

Create an object of the class
:class:`fluidlab.exp.doublediffusion.DoubleDiffusion`, i.e. an
object representing an experiment on the double diffusion instability.

"""
from __future__ import division, print_function

import numpy as np

from fluidlab.exp.doublediffusion import DoubleDiffusion

rho_min=1.
rho_max=1.15
z_max=400

description = """
Profil: two homogeneous layers (sugar above and salt underneath).


"""

if __name__ == '__main__':

    Delta_rho = rho_max - rho_min

    zs_norm = np.array(  [0,  1./2, 1./2, 1])
    rhos_norm = np.array([1.,   1.,   0., 0.])

    zs = z_max*zs_norm
    rhos = rho_min + Delta_rho*rhos_norm

    exp = DoubleDiffusion(zs=zs, rhos=rhos, description=description)

    print("""
    Create experiment with
    exp.name_dir:
    """+exp.name_dir+
    """

    You should change str_path in str_path_working_exp.py accordingly!
    """
    )
