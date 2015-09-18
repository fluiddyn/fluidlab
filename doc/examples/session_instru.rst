Experimental session and instruments
====================================

The first script does totally useless things but it shows how FluidLab
can be used for very simple scripts to control experiments. An
"experimental session" with one "data table" is created or loaded if
it already exists. A figure to plot the two quantities `U0` and `U1`
is defined. Data is saved at each time step of a short time loop.

Since there is no physical instruments, you should be able to try this
script. You can modify the argument `email_to` to a real email address
and uncomment the lines starting with "email" in the instantiation of
the session. You can also modify the flag `raise_error` to see what it
gives with the logger and the emails.

.. literalinclude:: exp_without_instr.py

The next script also corresponds to a false experiment but two real
instruments, a function generator
(:mod:`fluidlab.instruments.funcgen.tektronix_afg3022b`) and an
oscilloscope (:mod:`fluidlab.instruments.scope.agilent_dsox2014a`), are
used:

.. literalinclude:: exp_funcgen_scope.py  




