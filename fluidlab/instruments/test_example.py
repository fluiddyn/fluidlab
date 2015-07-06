
import unittest

from fluidlab.instruments.example_instru_with_trigger import Instru


class SimpleTestCase(unittest.TestCase):

    def test_instr(self):
        instr = Instru()

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
