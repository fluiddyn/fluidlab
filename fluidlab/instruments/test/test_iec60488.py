
import unittest

from fluiddyn.io import stdout_redirected

from fluidlab.instruments.iec60488 import IEC60488, Trigger


class InstruWithTrigger(IEC60488, Trigger):
    """An IEC60488 instrument with trigger."""


class SimpleTestCase(unittest.TestCase):

    def test_instr(self):

        with stdout_redirected():
            instr = InstruWithTrigger()

            # coming from IEC60488
            instr.clear_status()
            instr.reset_device()

            instr.status_enable_register.get()
            instr.status_enable_register.set(50)

            instr.get('status_enable_register')
            instr.set('status_enable_register', 1)

            # coming from Trigger
            instr.trigger()

        # test errors:
        with self.assertRaises(ValueError):
            instr.status_enable_register.set(550)

        with self.assertRaises(ValueError):
            instr.status_enable_register = True

        with self.assertRaises(AttributeError):
            instr.get('status_enble_register')

        with self.assertRaises(ValueError):
            instr.get('interface')


if __name__ == '__main__':
    unittest.main()
