
import unittest

from fluiddyn.io import stdout_redirected

from fluidlab.instruments.test.devices_pyvisasim import Device2


class SimpleTestCase(unittest.TestCase):

    def test_device2(self):

        with stdout_redirected():

            dev = Device2('ASRL2::INSTR', backend='@sim')

        idn = dev.get_idn()
        self.assertEqual(idn, u'SCPI,MOCK,VERSION_1.0\n')

        dev.voltage.set(2)
        voltage = dev.voltage.get()
        self.assertEqual(voltage, 2)

        dev.output_enabled.set(True)
        oe = dev.output_enabled.get()
        self.assertEqual(oe, True)

        # test errors:
        with self.assertRaises(ValueError):
            dev.voltage.set(7)

        with self.assertRaises(ValueError):
            dev.output_enabled = True

        with self.assertRaises(AttributeError):
            dev.get('aaaaa')

        with self.assertRaises(ValueError):
            dev.get('interface')


if __name__ == '__main__':
    unittest.main()
