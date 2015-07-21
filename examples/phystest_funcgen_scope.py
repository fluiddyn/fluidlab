from __future__ import print_function, division

import unittest
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from fluidlab.instruments.scope.agilent_dsox2014a import AgilentDSOX2014a
from fluidlab.instruments.funcgen.tektronix_afg3022b import TektronixAFG3022b


class TestContainer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Tektronix AFG3022B
        cls.funcgen = TektronixAFG3022b('USB0::1689::839::C034062::0::INSTR')
        # Agilent DSO-X 2014A
        cls.scope = AgilentDSOX2014a('USB0::2391::6040::MY51450715::0::INSTR')

    @classmethod
    def tearDownClass(cls):
        del cls.scope, cls.funcgen

    def init_output_funct_generator(self, voltage=1, frequency=1e4,
                                    offset=0, shape='square', warn=True):
        funcgen = self.funcgen

        funcgen.output1_state.set(1, warn)
        # funcgen.set('output1_state', 1)
        # funcgen.interface.write('OUTPut1:STATe ON')

        funcgen.function_shape.set(shape, warn)
        # funcgen.interface.write('FUNCTION ' + shape)

        funcgen.frequency.set(frequency, warn)
        # funcgen.interface.write('FREQUENCY ' + str(frequency))

        funcgen.voltage.set(voltage, warn)
        # funcgen.interface.write('VOLTAGE:AMPLITUDE ' + str(voltage))

        funcgen.offset.set(offset, warn)
        # funcgen.interface.write('VOLTAGE:OFFSET ' + str(offset))

    def get_scope_time_voltage(self, nb_points=1000,
                               format_output='ascii', warn=True):
        scope = self.scope
        scope.autoscale()
        time, data = scope.get_curve(nb_points, format_output, warn)
        # we have to divide by 2 because of impedance issues
        # the following command, if it works, can solve this problem:
        # scope.interface.write(':CHANnel1:IMPedance FIFTy')
        # more info page 67 (http://www.excaliburengineering.com/
        # media/datasheets/Agilent_33120A_um.pdf)
        data /= 2
        # testing the number of points
        # self.assertEqual(nb_points, len(time))
        # self.assertEqual(nb_points, len(data))
        return time, data

    def test_sin(self):
        shape = 'SIN'
        func = func_sin
        self.for_test_shape(shape, func)

    def test_square(self):
        shape = 'SQUARE'
        func = func_square
        self.for_test_shape(shape, func)

    def test_ramp(self):
        shape = 'RAMP'
        func = func_ramp
        self.for_test_shape(shape, func)

    def for_test_shape(self, shape, func):
        nb_points = 1001
        voltage = 3
        offset = 1
        frequency = 10000  # Hz
        format_output = 'byte'
        warn = True
        params0 = voltage, offset, frequency, 0
        self.init_output_funct_generator(
            voltage, frequency, offset, shape, warn)
        times, voltage_scope = self.get_scope_time_voltage(
            nb_points, format_output, warn)

        # print(func(times, *params0))
        # print(voltage_scope)

        params_fit, pcov = curve_fit(func, times, voltage_scope, p0=params0)
        voltage_fit = func(times, *params_fit)

        # testing the shape
        diff = (np.mean((voltage_scope - voltage_fit)**2) /
                np.mean(voltage_scope**2))
        self.assertTrue(diff < 0.1)
        # testing the voltage
        self.assertTrue(abs(params0[0]-params_fit[0]) < 0.1)
        # testing the offset
        self.assertTrue(abs(params0[1]-params_fit[1]) < 0.1)
        # testing the frequency
        self.assertTrue(abs(params0[2]-params_fit[2])/params0[2] < 0.1)

#        plt.figure()
#        ax = plt.gca()
#        voltage0 = func(times, *params0)

#        ax.plot(times, voltage0, 'y-')
#        ax.plot(times, voltage_scope, 'bx')
#        ax.plot(times, voltage_fit, 'r-')
#        plt.show()


def func_sin(times, amplitude, offset, frequency, phase):
    return amplitude / 2 * np.sin(2 * np.pi * frequency *
                                  times + phase) + offset


def func_square(times, amplitude, offset, frequency, phase):
    result = np.empty_like(times)
    for it, t in enumerate(times):
        hp = 2 * frequency * (t + phase)
        if np.floor(hp) % 2 == 0:
            result[it] = amplitude / 2. + offset
        else:
            result[it] = -amplitude / 2. + offset
    return result


def func_ramp(times, amplitude, offset, frequency, phase):
    result = np.empty_like(times)
    for it, t in enumerate(times):
        # hp = number that counts the Half Periods
        hp = 2 * frequency * (t + phase)
        if np.floor(hp) % 2 == 0:
            result[it] = offset + (hp - np.floor(hp) - 1/2) * amplitude
        else:
            result[it] = offset - (hp - np.floor(hp) - 1/2) * amplitude
    return result


if __name__ == '__main__':
    unittest.main()
