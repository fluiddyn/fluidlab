
import unittest

from fluidlab.instruments.example_instru_with_trigger import Instru


class SimpleTestCase(unittest.TestCase):

    def test_instr(self):
        instr = Instru()

        # coming from IEC60488
        instr.clear_status()
        instr.reset_device()

        instr.operation_complete_flag.get()
        instr.operation_complete_flag.set()

        instr.get('operation_complete_flag')
        instr.set('operation_complete_flag')

        # coming from Trigger
        instr.trigger()

        # test errors:
        with self.assertRaises(ValueError):
            instr.operation_complete_flag = True

        with self.assertRaises(AttributeError):
            instr.get('operation_complte_flag')

        with self.assertRaises(ValueError):
            instr.get('interface')


if __name__ == '__main__':
    unittest.main()
