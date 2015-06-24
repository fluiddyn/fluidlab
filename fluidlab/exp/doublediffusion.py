"""
Experiments on double diffusion (:mod:`fluidlab.exp.doublediffusion`)
=========================================================================

.. currentmodule:: fluidlab.exp.doublediffusion

Provides:

.. autoclass:: DoubleDiffusion
   :members:
   :private-members:

"""

from __future__ import division, print_function


from fluidlab.exp.withtank import ExperimentWithTank


class DoubleDiffusion(ExperimentWithTank):
    """Represent an experience on the double diffusion instability.

    See the documentation of the inherited class.

    """
    _base_dir = 'Double_diffusion'

    def __init__(self,
                 zs=None, rhos=None, params=None,
                 description=None,
                 str_path=None
                 ):
        # start the init. and guess if it is the first creation
        self._init_from_str(str_path)

        if self.first_creation:
            # add a bit of description
            description_base = """
Experiment in a small beaker on the double diffusion instability.

"""
            description = self._complete_description(
                description_base, description=description)

        # call the __init__ function of the inherited class
        super(DoubleDiffusion, self).__init__(
            rhos=rhos, zs=zs,
            params=params,
            description=description,
            str_path=str_path)
