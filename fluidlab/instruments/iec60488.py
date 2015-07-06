"""IEC60488 (:mod:`fluidlab.instruments.iec60488`)
==================================================

[This module is inspired by the module `slave.iec60488`. Part of the
documentation is taken from it. Thank you to the Slave authors.]

This module implements a IEC 60488-2:2004(E) compliant interface.

The `IEC 60488-2`_ describes a standard digital interface for programmable
instrumentation. It is used by devices connected via the IEEE 488.1 bus,
commonly known as GPIB. It is an adoption of the *IEEE std. 488.2-1992*
standard.

The `IEC 60488-2`_ requires the existence of several commands which are
logically grouped.

Provides:

.. autoclass:: IEC60488
   :members:
   :private-members:

Despite the required commands, there are several optional command
groups defined. The standard requires that if one command is used,
it's complete group must be implemented. These are implemented in the
following mixin classes.

.. autoclass:: PowerOn
   :members:

.. autoclass:: ParallelPoll
   :members:

.. autoclass:: ResourceDescription
   :members:

.. autoclass:: ProtectedUserData
   :members:

.. autoclass:: Calibration
   :members:

.. autoclass:: Trigger
   :members:

.. autoclass:: TriggerMacro
   :members:

.. autoclass:: Macro
   :members:

.. autoclass:: ObjectIdentification
   :members:

.. autoclass:: StoredSetting
   :members:

.. autoclass:: Learn
   :members:

.. autoclass:: SystemConfiguration
   :members:

.. autoclass:: PassingControl
   :members:

.. _IEC 60488-2: http://dx.doi.org/10.1109/IEEESTD.2004.95390

"""

from fluidlab.instruments.features import (
    FunctionCommand, BoolValue, StringValue, RegisterValue)

from fluidlab.instruments.driver import Driver


class IEC60488(Driver):
    """

    The `IEC 60488-2`_ requires the existence of several commands which are
    logically grouped.

    Reporting Commands

    - `*CLS` - Clears the data status structure.
    - `*ESE` - Write the event status enable register.
    - `*ESE?` - Query the event status enable register.
    - `*ESR?` - Query the standard event status register.
    - `*SRE` - Write the status enable register.
    - `*SRE?` - Query the status enable register.
    - `*STB` - Query the status register.

    Internal operation commands

    - `*IDN?` - Identification query.
    - `*RST` - Perform a device reset.
    - `*TST?` - Perform internal self-test.

    Synchronization commands

    - `*OPC` - Set operation complete flag high.
    - `*OPC?` - Query operation complete flag.
    - `*WAI` - Wait to continue.
    """

features = [
    FunctionCommand(
        'clear_status', 'Clears the data status structure', '*CLS'),
    FunctionCommand(
        'query_esr', 'Query the standard event status register.', '*ESR?'),
    FunctionCommand('wait', 'Wait to continue', '*WAI'),
    FunctionCommand(
        'perform_internal_test',
        'Perform internal self-test.', '*TST?'),
    FunctionCommand('reset_device', 'Perform a device reset', '*RST'),
    BoolValue('operation_complete_flag',
              doc='Operation complete flag.',
              command_set='*OPC')]

IEC60488._build_class(features)


class PowerOn(Driver):
    """A mixin class, implementing the optional power on commands.

    Power on common commands

    * `*PSC` - Set the power-on status clear bit.
    * `*PSC?` - Query the power-on status clear bit.
    """

PowerOn._build_class([
    BoolValue('power_on_status',
              doc='Power-on status.',
              command_set='*PSC')])


class ParallelPoll(Driver):
    """A mixin class, implementing the optional parallel poll commands.

    Parallel poll common commands

    * `*IST?` - Query the individual status message bit.
    * `*PRE` - Set the parallel poll enable register.
    * `*PRE?` - Query the parallel poll enable register.
    """

ParallelPoll._build_class([
    FunctionCommand(
        'query_status_message_bit',
        'Query the individual status message bit', '*IST?'),
    RegisterValue('parallel_poll',
                  doc='Parallel poll enable register.',
                  command_set='*PRE')])


class ResourceDescription(Driver):
    """A mixin class, implementing the optional resource description common
    commands.

    Resource description common commands

    * `*RDT` - Store the resource description in the device.
    * `*RDT?` - Query the stored resource description.
    """

ResourceDescription._build_class([
    StringValue('resource_description',
                doc='Resource description.',
                command_set='*RDT')])


class ProtectedUserData(Driver):
    """A mixin class, implementing the protected user data commands.

    Protected user data commands

    * `*PUD` - Store protected user data in the device.
    * `*PUD?` - Query the protected user data.
    """

ProtectedUserData._build_class([
    StringValue('user_data',
                doc='Protected user data.',
                command_set='*PUD')])


class Calibration(Driver):
    """A mixin class, implementing the optional calibration command.

    Calibration command

    * `*CAL?` - Perform internal self calibration.
    """

Calibration._build_class([
    FunctionCommand(
        'perform_calibration',
        'Perform internal self calibration', '*CAL?')])


class Trigger(Driver):
    """A mixin class, implementing the optional trigger command.

    Trigger command

    * `*TRG` - Execute trigger command.
    """

Trigger._build_class([
    FunctionCommand('trigger', 'Execute trigger command.', '*TRG')])


class TriggerMacro(Driver):
    """A mixin class, implementing the optional trigger macro commands.

    Trigger macro commands

    * `*DDT` - Define device trigger.
    * `*DDT?` - Define device trigger query.
    """

TriggerMacro._build_class([
    StringValue('define_device_trigger',
                doc='Define device trigger.',
                command_set='*DDT')])


class Macro(Driver):
    """A mixin class, implementing the optional macro commands.

    Macro Commands

    * `*DMC` - Define device trigger.
    * `*EMC` - Define device trigger query.
    * `*EMC?` - Define device trigger.
    * `*GMC?` - Define device trigger query.
    * `*LMC?` - Define device trigger.
    * `*PMC` - Define device trigger query.
    """

Macro._build_class([
    FunctionCommand(
        'dmc', 'Define device trigger (???).', '*DMC'),
    StringValue('emc',
                doc='Define device trigger (???).',
                command_set='*EMC'),
    FunctionCommand(
        'gmc', 'Define device trigger (???).', '*GMC?'),
    FunctionCommand(
        'lmc', 'Define device trigger (???).', '*LMC?'),
    FunctionCommand(
        'pmc', 'Define device trigger (???).', '*PMC')])


class ObjectIdentification(Driver):
    """A mixin class, implementing the optional object identification command.

    Option Identification command

    * `*OPT?` - Option identification query.
    """
ObjectIdentification._build_class([
    FunctionCommand(
        'opt_identification', 'Option identification query.', '*OPT?')])


class StoredSetting(Driver):
    """A mixin class, implementing the optional stored setting commands.

    Stored settings commands

    * `*RCL` - Restore device settings from local memory.
    * `*SAV` - Store current settings of the device in local memory.
    """

StoredSetting._build_class([
    FunctionCommand(
        'restore_device_settings',
        'Restore device settings from local memory.', '*RCL'),
    FunctionCommand(
        'store_current_settings',
        'Store current settings of the device in local memory.', '*SAV')])


class Learn(Driver):
    """A mixin class, implementing the optional learn command.

    Learn command

    * `*LRN?` - Learn device setup query.
    """

Learn._build_class([
    FunctionCommand(
        'learn_device_setup',
        'Learn device setup query.', '*LRN?')])


class SystemConfiguration(Driver):
    """A mixin class, implementing the optional system configuration commands.

    System configuration commands

    * `*AAD` - Accept address command.
    * `*DLF` - Disable listener function command.
    """

SystemConfiguration._build_class([
    FunctionCommand(
        'accept_address_command',
        'Accept address command.', '*AAD'),
    FunctionCommand(
        'disable_listener',
        'Disable listener function command.', '*DLF')])


class PassingControl(Driver):
    """A mixin class, implementing the optional passing control command.

    Passing control command

    * `*PCB` - Pass control back.
    """

PassingControl._build_class([
    FunctionCommand(
        'pass_control_back',
        'Pass control back.', '*PCB')])


if __name__ == '__main__':
    iec = IEC60488()
