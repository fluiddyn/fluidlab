"""Example of a instrument with trigger
=======================================

"""

from fluidlab.instruments.iec60488 import IEC60488, Trigger


class Instru(IEC60488, Trigger):
    """An IEC60488 instrument with trigger."""


if __name__ == '__main__':
    instr = Instru()
