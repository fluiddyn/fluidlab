"""IEC60488 (:mod:`fluidlab.instruments.iec60488`)
==================================================

Provides:

.. autoclass:: IEC60488
   :members:
   :private-members:

.. autoclass:: Trigger
   :members:
   :private-members:

"""

from fluidlab.instruments.features import FunctionCommand, BoolValue

from fluidlab.instruments.driver import Driver


class IEC60488(Driver):
    """

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
              command_get='*OPC?', command_set='*OPC')]

IEC60488._build_class(features)


class Trigger(Driver):
    """A mixin class, implementing the optional trigger command.
    """

Trigger._build_class([
    FunctionCommand('trigger', 'Execute trigger command.', '*TRG')])


if __name__ == '__main__':
    iec = IEC60488()
