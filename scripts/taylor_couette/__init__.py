"""Scripts for preparing and carrying out Taylor-Couette experiments
====================================================================

Some of these scripts should be modified to do useful things. Thus, I
would strongly advise to open and understand them before running them!

These scripts can be used for the different steps that have to be done
to run particular types of experiments. Typically, the steps can be:

1. Chose consistent parameters in one of the files
   params_creation_*.py, which defines some parameters that can be
   modified. You should run it in order to verify the consistency of
   the parameters.

2. Create an experiment object with the parameters contains in the
   corresponding params_creation_*.py file (create_exp_*.py).

3. Chose a "working" experiment by modifying str_path in
   str_path_working_exp.py, which is used for loading the
   corresponding experiment by the other scripts.

4. Fill the tank with the wanted profile (fill_tank.py).

5. Move the traverse and test the probe (traverse_and_probe.py).

6. Run the experiment (run_exp.py).

7. Plot some results (plot_profiles.py)


The scripts are now described in more details:

.. automodule:: scripts.taylor_couette.params_creation_TC_lin

.. automodule:: scripts.taylor_couette.create_exp_TC_lin

.. automodule:: scripts.taylor_couette.str_path_working_exp

.. automodule:: scripts.taylor_couette.fill_tank

.. automodule:: scripts.taylor_couette.traverse_and_probe

.. automodule:: scripts.taylor_couette.run_exp_impulsive_start

.. automodule:: scripts.taylor_couette.run_exp_control_1cylinder

.. automodule:: scripts.taylor_couette.run_exp_control_2cylinders

.. automodule:: scripts.taylor_couette.plot_profiles

"""
