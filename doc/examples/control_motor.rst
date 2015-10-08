Control a motor
===============

The video demonstrates how a motor (Modbus RTU with RS485 in RJ45) can
be controlled with Python and the package fluidlab.


.. raw:: html

   <iframe frameborder="0" width="480" height="270"
           src="http://www.dailymotion.com/embed/video/x387j3r"
           allowfullscreen>
   </iframe>


The driver of the motor is coded in the module
:mod:`fluidlab.instruments.modbus.unidrive_sp`.


The first script with a simple loop:

.. literalinclude:: drive_motor.py


And the code for the mini GUI (sorry, quick and dirty...):

.. literalinclude:: demo_graphical_driver_motor.py



