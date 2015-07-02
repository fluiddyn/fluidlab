"""IEC60488 (:mod:`fluidlab.instruments.iec60488`)
==================================================

Provides:

.. autoclass:: IEC60488
   :members:
   :private-members:

.. autoclass:: Trigger
   :members:
   :private-members:

.. autoclass:: Instr
   :members:
   :private-members:

"""

from fluidlab.instruments.features import FunctionCommand, ValueBool

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
        'clear_status', '*CLS', 'Clears the data status structure'),
    FunctionCommand(
        'query_esr', '*ESR?', 'Query the standard event status register.'),
    FunctionCommand('wait', '*WAI', 'Wait to continue'),
    FunctionCommand(
        'perform_internal_test', '*TST?',
        'Perform internal self-test.'),
    FunctionCommand('reset_device', '*RST', 'Perform a device reset'),
    ValueBool('operation_complete_flag',
              command_get='*OPC?', command_set='*OPC',
              doc='Operation complete flag')
]


IEC60488._complete_cls(features)


class Trigger(Driver):
    """A mixin class, implementing the optional trigger command.
    """

Trigger._complete_cls([
    FunctionCommand('trigger', '*TRG', 'Execute trigger command')])


if __name__ == '__main__':
    iec = IEC60488()
