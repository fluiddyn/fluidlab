"""
Pumps (:mod:`fluidlab.objects.pumps`)
=====================================

.. _pumps:
.. currentmodule:: fluidlab.objects.pumps

Provides:

.. autoclass:: MasterFlexPumps
   :members:
   :private-members:


"""

from __future__ import division, print_function

import os
import numpy as np
import time
import atexit

from fluiddyn.io import _write_warning
from fluiddyn.util import query
from fluiddyn.io import txt

try:
    import serial
except ImportError as exc:
    _write_warning('Warning: ImportError\n    ' + str(exc))


here = os.path.abspath(os.path.dirname(__file__))
path_calib = os.path.join(here, 'calibration_pumps.txt')

if not os.path.exists(path_calib):
    with open(path_calib, 'w') as f:
        f.write('Calibration pumps, maximum flowrate '
                'for pumps 1 (line 1) and 2 (line 2):\n'
                '1099.6\n1146.1')


def modif_calib_file(pump, flow_rate):
    with open(path_calib, 'r') as f:
        lines = f.readlines()
    lines[pump] = '{:.0f}'.format(flow_rate)+'\n'
    with open(path_calib, 'w') as f:
        f.write(''.join(lines))
    print('New calibration flowrate in the file...')




class MasterFlexPumps(object):
    """Represent some Masterflex pumps.

    We use Masterflex L/S (model number 7551.00).

    Parameters
    ----------
    nb_pumps : {2, int}, optional
        Number of pumps

    verbose : {False, bool}, optional
        If True, more verbose.

    Attributes
    ----------
    flow_rates_max: `numpy.ndarray`
        Maximum flow rates of the pumps.

    pumps: list
        List of the pump indexes.

    serial: serial.Serial
        Object representing the serial port connected to the pumps.

    Notes
    -----
    The pumps and this class are often used with the class
    :class:`fluidlab.objects.tanks.StratifiedTank`.

    """

    # define some useful ASCII characters
    stx = chr(2)  # start of text
    enq = chr(5)  # enquiry
    ack = chr(6)  # acknoledge
    nak = chr(21)  # negative acknoledge
    cr = chr(13)  # carriage return

    def __init__(self, nb_pumps=2, verbose=False):
        self.rot_per_min_max = 600.

        flow_rates_max = txt.quantities_from_txt_file(path_calib)[0]
        if nb_pumps==1:
            self.flow_rates_max = flow_rates_max[0]  # (ml/min)
        if nb_pumps==2:
            self.flow_rates_max = flow_rates_max[:2]  # (ml/min)
        else:
            self.flow_rates_max = 1000*np.ones(nb_pumps)  # (ml/min)

        self.pumps = range(1, nb_pumps+1)

        port = 'COM3'  # Serial port to which the pump(s) are connected (COM3)

        # configure the serial connections (the parameters differs on
        # the device you are connecting to)
        try:
            self.serial = serial.Serial(port=port,
                                        baudrate=4800,
                                        bytesize=7,
                                        parity=serial.PARITY_ODD,
                                        stopbits=serial.STOPBITS_ONE
                                        # ,
                                        # xonxoff=False, # xon=off,
                                        # rtscts=False # rts=hs
                                    )
        except NameError as exc:
            self.serial = None

        except serial.serialutil.SerialException as exc:
            self.serial = None
            _write_warning('Warning: SerialException\n    ' + str(exc))

        except OSError as exc:
            self.serial = None
            _write_warning('Warning: OSError\n    ' + str(message))

        else:
            self.stop(pumps=99)
            if verbose:
                print('serial.write: <ENQ>')
            self.serial.write(self.enq)
            ret = self.serial.readline()
            if verbose:
                print('answer pump:', ret)

            self._command('')
            self._command('I')
            self.stop(99)
            self.set_rot_per_min(0.1)
            self.stop(99)
            self._command('Z')
            atexit.register(MasterFlexPumps.stop, self)


        self.pumps = list(range(1, nb_pumps+1))




    def _command(self, command, pumps=None, verbose=False):
        """Send a command to some pumps.

        Parameters
        ----------
        command : str
            The command that has to be send to the pumps.

        pumps : int or array_like
            The index of one pump or an array_like containing the
            indexes of pumps.

        verbose : bool
            More verbose If equal to ``True``.

        Returns
        -------
        results : list
            The results of the commands.

        Notes
        -----
        The command can be for example '', 'G0', 'I', 'z'...

        """
        pumps = self._give_list_pumps(pumps)
        results = []
        for pump in pumps:
            key = 'P{0:02d}'.format(pump)
            line_to_write = self.stx+key+command+self.cr
            if verbose:
                print('serial.write:', line_to_write)
            self.serial.write(line_to_write)
            result = self.serial.readline()
            if len(result) == 0:
                if verbose:
                    print('no answer.')
            elif result[0] == self.ack:
                if verbose:
                    print('answer pump: <ACK> (happy)')
            elif result[0] == self.nak:
                print('answer pump: <NAK> (unhappy)')
            elif verbose:
                print('answer pump:', result)
            results.append(result)

        return results

    def go(self, pumps=None):
        """Start some pumps.

        Send the command 'G0' to the pumps.

        Parameters
        ----------
        pumps : {None, int, array_like}, optional
            The index of one pump or an array_like containing the
            indexes of pumps. If None, the function uses self.pumps.

        """
        pumps = self._give_list_pumps(pumps)
        return self._command('G0', pumps=pumps)

    def set_rot_per_min(self, rots_per_min=0, pumps=None):
        """Set the number of rotations per min for some pumps.

        Parameters
        ----------
        rots_per_min : number or array_like
            The rotation rate(s) in rotations per mimute.

        pumps : {None, int, array_like}, optional
            The index of one pump or an array_like containing the
            indexes of pumps. If None, the function uses self.pumps.

        """
        pumps = self._give_list_pumps(pumps)

        rots = rots_per_min

        if hasattr(rots, '__iter__'):
            if len(rots) != len(pumps):
                raise ValueError("if hasattr(rots, '__iter__'), "+
                                 "len(rots) should be equal to len(pumps)")
            for ir, rot in enumerate(rots):
                if rot > self.rot_per_min_max+0.01:
                    rots[ir] = self.rot_per_min_max
                    print(
'rot_per_min for pump {0:d} too large,'.format(pumps[ir]),
'new rots_per_min:', rots
                    )
                elif rot < 0.1:
                    rots[ir] = 0.1

            for ip, pump in enumerate(pumps):
                ret = self._command('S{0:+07.1f}'.format(rots[ip]), pumps=pump)
            return ret
        else:
            if rots > self.rot_per_min_max:
                rots = self.rot_per_min_max
                print('The rotation per min is too large '+
                      'and has been limited to the maximum rotation')
            elif rots < 0.1:
                rots = 0.1
            return self._command('S{0:+07.1f}'.format(rots), pumps=pumps)

    def stop(self, pumps=None):
        """Stop some pumps.

        Parameters
        ----------
        pumps : {None, int, array_like}, optional
            The index of one pump or an array_like containing the
            indexes of pumps. If None, the function uses self.pumps.

        """
        pumps = self._give_list_pumps(pumps)
        return self._command('H', pumps=pumps)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def _give_list_pumps(self, pumps=None):
        """Return a list of pump indexes.

        Parameters
        ----------
        pumps : {None, int, array_like}, optional
            The index of one pump or an array_like containing the
            indexes of pumps. If None, the function uses self.pumps.

        """
        if pumps is None:
            pumps = self.pumps
        else:
            if not hasattr(pumps, '__iter__'):
                pumps = [pumps]
        return pumps


    def calibrate(self, pumps=None, nb_mins=4):
        """Calibrate the pumps.

        Parameters
        ----------
        pumps : {None, int, array_like}, optional
            The index of one pump or an array_like containing the
            indexes of pumps. If None, the function uses self.pumps.

        nb_mins : {4, number}
            Number of minutes for calibrating one pumps.

        """
        pumps = self._give_list_pumps(pumps)

        for pump in pumps:
            self.calibrate_one_pump(pump, nb_mins=nb_mins)


    def calibrate_one_pump(self, pump=1, nb_mins=None, rot_per_min=None):

        ip = pump-1

        if rot_per_min is None:
            rot_per_min = self.rot_per_min_max/2

        flow_rate_approx = (self.flow_rates_max[ip]*rot_per_min
                            /self.rot_per_min_max)

        print(
'Calibrate pump {0:d}:\n'.format(pump)+
'{0} min '.format(nb_mins)+
'with an approximate flow rate of '+
'{0} ml/min;\n'.format(flow_rate_approx)+
'approximate volume equal to {0} ml.'.format(nb_mins*flow_rate_approx)
)

        if query.query_yes_no('Do you have a large enough tank? Ready?'):
            pumps.set_rot_per_min(rot_per_min, pumps=pump)
            pumps.go(pumps=pump)
            time.sleep(nb_mins*60)
            pumps.stop()

            volume = query.query_number('How many ml have been pumped?')

            flow_rate = volume/nb_mins

            print('Then, flow_rates_max for pump {0:d} '.format(pump)+
                  'should be equal to {0:6.1f}.'.format(
                      flow_rate*self.rot_per_min_max/rot_per_min)
            )




    def set_flow_rate(self, flow_rates=0, pumps=None):
        """Set the flow rates.

        Parameters
        ----------
        flow_rates : {number, array_like}
            flow rates in ml/min.
        pumps : {None, int, array_like}, optional
            The index of one pump or an array_like containing the
            indexes of pumps. If None, the function uses self.pumps.

        """
        pumps = self._give_list_pumps(pumps)
        ipumps = np.array(pumps)-1

        flow_rates_max = self.flow_rates_max[ipumps]
        # print('flow_rates_max', flow_rates_max)

        rots_per_min = flow_rates/flow_rates_max*self.rot_per_min_max
        # print('rots_per_min', rots_per_min)

        self.set_rot_per_min(rots_per_min, pumps=pumps)

    def test_one_pump(self, pump=1, vol_to_pump=2000., flow_rate_test=None):
        """Test one pump and print actual maximum flowrate.

        Pump with the pump with the index *pump* an approximate volume
        *vol_to_pump*. Ask for a measure of the volume actually
        pumped. Print the "actual" maximum flowrate for the tested pump
        (which can be written in the function __init__).

        The "actual" maximum flowrate is the one that which has give
        a more accurate result, computed from the volume actually
        pumped.

        Parameters
        ----------
        pump : {1, int}, optional
            A pump index.

        vol_to_pump : {2000., number}
            The volume to pump.

        flow_rate_test : {None, number}, optional
            The flow rate used for testing. If None, use 2/3 of the
            maximum flow rate for the tested pump.

        """

        if flow_rate_test is None:
            flow_rate_test = self.flow_rates_max[pump-1]*2/3

        nb_mins_to_pump = vol_to_pump/flow_rate_test

        print(
            '\nTest pump {:d}:\n'.format(pump)+
            'flow_rates_max = {}\n'.format(self.flow_rates_max[pump-1])+
            'approximate volume equal to {0} ml,\n'.format(vol_to_pump)+
            'with an approximate flow rate of '+
            '{0} ml/min,\n'.format(flow_rate_test)+
            'Duration of the test: {0:6.2f} min '.format(nb_mins_to_pump)
)

        pumps.set_flow_rate(flow_rate_test, pumps=pump)
        pumps.go(pumps=pump)
        time.sleep(nb_mins_to_pump*60)
        pumps.stop(pumps=pump)

        vol_measured = query.query_number('How many ml have been pumped?')
        flow_rate_measured = vol_measured/nb_mins_to_pump


        flow_rate_new = (self.flow_rates_max[pump-1]*flow_rate_measured
                         /flow_rate_test)

        print('Then flow_rates_max for pump {0:d} '.format(pump)+
              'should be equal to {0:5.0f}.'.format(flow_rate_new))


        ok = query.query_yes_no(
            ('Do you want to update the calibration file and \n'
             'the Pumps object with this value?'),
            default="no")
        if ok:
            modif_calib_file(pump, flow_rate_new)








if __name__ == '__main__':


    pumps = MasterFlexPumps(nb_pumps=2)

    # pumps.set_flow_rate(1000, pumps=[1])
    # pumps.go()
    # time.sleep(20)

    # pumps.stop()

    # pumps.calibrate()
    pumps.test_one_pump(2, vol_to_pump=400*4, flow_rate_test=400)
