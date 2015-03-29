"""
Experiments with a vertical duct (:mod:`fluidlab.exp.vertduct`)
===================================================================

.. currentmodule:: fluidlab.exp.vertduct

Provides:

.. autoclass:: VerticalDuctExp
   :members:
   :private-members:

"""

from __future__ import division, print_function

import numpy as np

from fluiddyn.util import load_exp

from fluidlab.exp.withconductivityprobe import ExpWithConductivityProbe




class VerticalDuctExp(ExpWithConductivityProbe):
    """Represent a test experiment with a vertical duct.

    See the documentation of the inherited class.

    """
    _base_dir = 'Vertical_duct'

    def __init__(self,
                 zs=None, rhos=None,
                 params=None,
                 description=None,
                 str_path=None,
                 position_start=352., position_max=None, Deltaz=340.,
                 need_board=True
                 ):

        # start the init. and find out if it is the first creation
        self._init_from_str(str_path)

        if self.first_creation:
            # add a bit of description
            description_base = """
Experiment in a small vertical duct.

This tank is 460 mm high and the 2 horizontal sides measure 80 mm.

The main objectif of this experience is to test the filling with the
pumps and the measurements with the conductivity probe.

"""
            self._complete_description(
                description_base, description=description)

        # call the __init__ function of the inherited class
        super(VerticalDuctExp, self).__init__(
            rhos=rhos, zs=zs,
            params=params,
            description=description,
            str_path=str_path,
            position_start=position_start,
            position_max=position_start, Deltaz=Deltaz,
            need_board=need_board)










def create_exp(rho_max=1.098, z_max=400):

    rho_min = 1.
    Delta_rho = rho_max - rho_min

#     zs_norm = np.array([0, 1./6, 5./6, 1])
#     rhos_norm = np.array([1., 0.5, 0.5, 0.])
#     description = """
# Profil: strong linear stratification at the bottom and
# top. Unstratified in the middle.

# """

    # zs_norm = np.array(  [0., 1/4, 1/2, 1/2, 3/4, 1.])
    # rhos_norm = np.array([1., 1.,  2/3, 1/3, 0.,  0.])
    zs_norm = np.array(  [0., 1/3, 2/3, 1.])
    rhos_norm = np.array([1., 1/2, 1/2, 0.])

    description = """
Profile: stratified at the top and bottom and homogenous in the middle.

"""
    zs = z_max*zs_norm
    rhos = rho_min + Delta_rho*rhos_norm
    exp = VerticalDuctExp(zs=zs, rhos=rhos, description=description)

    return exp








def load_exp_and_measure_profils(str_path_save):

    exp = load_exp(str_path=str_path_save,
                   position_start=379., Deltaz=370.)
    exp.sprobe.set_sample_rate(1000.)
    period = 60
    exp.profiles.measure(duration=2*period, period=period,
                         deltaz=370, speed_measurements=100,
                         speed_up=60)

    exp.profiles.plot()
    return exp










if __name__ == '__main__':

    # exp = create_exp()

    str_path_save = 'Exp_2014-09-29_15-33-23'

    # exp = load_exp_and_measure_profils(str_path_save)

    exp = load_exp(str_path_save)

    # exp.tank.fill(pumps=True)


    exp.profiles.plot(ind_file_profiles=[-1])

    # exp.sprobe.set_sample_rate(200.)
    # exp.sprobe.measure(duration=0.1, VERBOSE=True)
    # exp.sprobe.measure(duration=0.1, VERBOSE=True)
    # exp.sprobe.measure(duration=2., VERBOSE=True)

    # exp.sprobe.plot_calibrations()


    # exp.sprobe.move(deltaz=40, speed=60, bloquing=True)
    # exp.sprobe.move(deltaz=500, speed=100, bloquing=True)
