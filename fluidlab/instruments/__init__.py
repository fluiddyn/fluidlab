"""Represent and communicate with instruments
=============================================

.. currentmodule:: fluidlab.instruments

We call "instruments" all devices that can be more or less directly
plug to a computer. This packages provides instrument drivers and
utilities to write them.

In FluidLab, the drivers have an attribute `interface` that contains
relatively low-level functions to communicate with the device. Some
base interface class are defined in the module
:mod:`fluidlab.instruments.interfaces`.

The drivers have also attributes representing values that are saved or
can be set in or get from the instruments. Some of these "features"
are defined in :mod:`fluidlab.instruments.features`.

For many instruments, the communication with the computer is made
directly through simple messages understandable by humans.  For these
instruments, the communication can be done using VISA (Virtual
Instrument Software Architecture), independently of how the
communication is done in practice (e.g. with GPIB, RS232, USB,
Ethernet).

A mechanism to easily write such drivers is implemented in:

.. autosummary::
   :toctree:

   drivers
   interfaces
   features
   iec60488

.. todo:: Write drivers for some "VISA instruments"...

Some drivers of particular "VISA instruments" are organized in the
packages:

.. autosummary::
   :toctree:

   scope
   funcgen
   powersupply
   multimeter
   multiplexer
   sourcemeter

Other very common communication standards are Modbus and Firewire:

.. autosummary::
   :toctree:

   modbus
   firewire

For other instruments, the communication is done with libraries:

.. autosummary::
   :toctree:

   sound

The drivers for the data acquisition boards are also gather in this package:

.. autosummary::
   :toctree:

   daq

"""

# Only real instruments in *, not features or iec60488, etc.
__all__ = ["amplifier", "multiplexer", "multimeter", "sourcemeter", "powersupply", "funcgen", "chiller", "scope", "pressure_transducer"]
