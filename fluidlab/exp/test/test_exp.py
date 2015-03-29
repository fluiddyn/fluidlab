
import fluiddyn
from fluidlab.exp.base import Experiment

from fluidlab.exp.withtank import ExperimentWithTank
from fluidlab.exp.doublediffusion import DoubleDiffusion

from fluidlab.exp.withconductivityprobe import ExpWithConductivityProbe
from fluidlab.exp.vertduct import VerticalDuctExp

from fluidlab.exp.taylorcouette.base import TaylorCouetteExp
from fluidlab.exp.taylorcouette.linearprofile import ILSTaylorCouetteExp
from fluidlab.exp.taylorcouette.quadprofile import IQSTaylorCouetteExp
from fluidlab.exp.taylorcouette.twolayers import I2LTaylorCouetteExp


from fluiddyn.io import stdout_redirected

import unittest
import os
import shutil



def del_and_load_exp(exp, **kargs):
    path_save = exp.path_save
    # str_path = os.path.split(path_save)[-1]
    str_path = path_save
    del(exp)
    # load the experiment
    exp = fluiddyn.load_exp(str_path, **kargs)
    # clean by removing the directory
    shutil.rmtree(path_save)
    return exp


class TestExperiment(unittest.TestCase):
    def test_create_load(self):
        """Should be able to create and load an experiment."""
        exp = Experiment(params={'a': 2}, description='Test.')
        del_and_load_exp(exp)


class TestExperimentWithTank(unittest.TestCase):
    def test_create_fill_load(self):
        """Should be able to create, fill and load an ExperimentWithTank."""
        exp = ExperimentWithTank(
            rhos=[1.1, 1], zs=[0, 200], params={'a': 2},
            description='Test.',
        )
        with stdout_redirected():
            exp.tank.fill(pumps=False, hastoplot=False)
        del_and_load_exp(exp)


class TestDoubleDiffusion(unittest.TestCase):
    def test_create_load(self):
        """Should be able to create and load an DoubleDiffusion."""
        exp = DoubleDiffusion(
            rhos=[1.1, 1], zs=[0, 200], params={'a': 2},
            description='Test.'
        )
        del_and_load_exp(exp)


class TestExpWithConductivityProbe(unittest.TestCase):
    def test_create_load(self):
        """Should be able to create and load an ExpWithConductivityProbe."""

        with stdout_redirected():
            exp = ExpWithConductivityProbe(
                rhos=[1.1, 1], zs=[0, 200], params={'a': 2},
                description='Test.')

        del_and_load_exp(exp, need_board=False)


class TestVerticalDuctExp(unittest.TestCase):
    def test_create_load(self):
        """Should be able to create and load a VerticalDuctExp."""
        exp = VerticalDuctExp(
            rhos=[1.1, 1], zs=[0, 200], params={'a': 2},
            description='Test.',
            need_board=False
        )
        self.assertEqual(exp._base_dir, 'Vertical_duct')
        del_and_load_exp(exp, need_board=False)








class TestTaylorCouetteExp(unittest.TestCase):
    def test_create_load(self):
        """Should be able to create and load an experiment."""
        exp = TaylorCouetteExp(
            rhos=[1.1, 1], zs=[0, 200],
            Omega1=1, Omega2=0,
            R1=150., R2=261.,
            params={'a': 2}, description='Test.',
            need_board=False
        )

        self.assertEqual(exp._base_dir, os.path.join('TaylorCouette', 'Base'))
        del_and_load_exp(exp, need_board=False)



class TestILSTaylorCouetteExp(unittest.TestCase):
    def test_create_load(self):
        """Should be able to create and load an experiment."""
        description = 'Test.'
        exp = ILSTaylorCouetteExp(
            rho_max=1.1, N0=1.,
            prop_homog=0.1,
            Omega1=1, Omega2=0,
            R1=150., R2=261.,
            params={'a': 2}, description=description,
            need_board=False
        )
        self.assertEqual(exp._base_dir, os.path.join('TaylorCouette', 'ILS'))
        self.assertTrue('ILS' in exp.description)
        self.assertTrue(exp.description.endswith(description))

        self.assertTrue('Ri' in exp.params)

        exp = del_and_load_exp(exp, need_board=False)




class TestIQSTaylorCouetteExp(unittest.TestCase):
    def test_create_load(self):
        """Should be able to create and load an IQSTaylorCouetteExp."""
        exp = IQSTaylorCouetteExp(
            rho_max=1.1,
            z_max=200,
            alpha=0.6,
            Omega1=1, Omega2=0,
            R1=150., R2=261.,
            params={'a': 2}, description='Test.',
            need_board=False
        )
        self.assertEqual(exp._base_dir, os.path.join('TaylorCouette', 'IQS'))
        del_and_load_exp(exp, need_board=False)


class TestI2LTaylorCouetteExp(unittest.TestCase):
    def test_create_load(self):
        """Should be able to create and load an I2LTaylorCouetteExp."""
        exp = I2LTaylorCouetteExp(
            rho_min=1.0, rho_max=1.1,
            z_max=200,
            Omega1=1, Omega2=0,
            R1=150., R2=261.,
            params={'a': 2}, description='Test.',
            need_board=False
        )
        self.assertEqual(exp._base_dir, os.path.join('TaylorCouette', 'I2L'))
        del_and_load_exp(exp, need_board=False)






if __name__ == '__main__':
    unittest.main()
