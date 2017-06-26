
from __future__ import print_function, division

import time
import sys

import numpy as np
import pylab

from labjack import ljm

from fluiddyn.util.query import query_yes_no
from fluidlab.exp import Timer
from fluidlab.objects.galvanometer import Galva

from .util import wait_for_file, save_exp


class PIVScan(object):

    def __init__(self):
        self.galva = Galva()
        self.t7 = self.galva.t7

    def single_frame_3d(
            self, vmin, vmax, time_expo, time_between_frames, nb_levels,
            total_time=None,
            wait_file=False, nb_period_to_wait=1.):
        '''Single frame PIV.

        Send a saw tooth signal to the galvanometer (DAC0) and a square signal
        to trig cameras (DAC1).

        Parameters
        ----------

        - vmin, vmax: min and max of voltage (in V)
        - time_expo: exposure time (in s)
        - time_between_frames: time between 2 saw tooth (in s)

        Remark: the real time_between_frames can be different from
        input time_between_frames!!  time_between_frames = n/freq with
        n an integer and freq = nb_levels/tup

        - nb_levels: number of steps in the rising part
        - total_time=None: total_time of acquisition (in s)

        '''
        if vmin < 0 or vmax > 5:
            print("##########\nvmin and vmax must be in the range [0, 5]V")
            return None

        IN_NAMES = []
        OUT_NAMES = ['DAC0', 'DAC1']

        volt, frequency, t = saw_tooth_period2(
            vmin=vmin, vmax=vmax,
            time_expo=time_expo,
            nb_levels=nb_levels, time_between_frames=time_between_frames)
        time_between_frames = t[-1] + t[1]
        tup = t[volt[0].argmax()]
        t7 = self.t7
        handle = t7.handle
        aScanList = t7.prepare_stream_loop(
            IN_NAMES=IN_NAMES, OUT_NAMES=OUT_NAMES, volt=volt)

        scansPerRead = frequency
        scanRate = frequency
        TOTAL_NUM_CHANNELS = len(IN_NAMES) + len(OUT_NAMES)

        print(
            '\n' + '#' * 79 + '\n' +
            'Connect DAC0 to the galvanometer\n'
            'Connect DAC1 to connector 1 of PCO Edge camera\n'
            '\n' + '#' * 79 + '\n\n' +
            'Settings in Camware software\n\n'
            '- trigger Mode to "Ext Exp Start"\n'
            '- frame rate >= {} Hz\n'.format(1.0/(tup/nb_levels)) +
            '- exposure <= {} s \n'.format(tup/nb_levels) +
            '- acquire Mode to "Auto"\n'
            '- I/O Signal: tick only "Exposure Trigger"\n')

        if not query_yes_no('Are you ready to start acquisition?'):
            return

        if wait_file:
            wait_for_file('oscillate_*', nb_period_to_wait)

        save_exp(t, volt, time_expo=time_expo, tup=tup,
                 time_between_frames=time_between_frames,
                 rootname='piv_scan_single_frame')

        scanRate = ljm.eStreamStart(
            handle, int(scansPerRead), TOTAL_NUM_CHANNELS, aScanList,
            scanRate)
        print('Stream started')

        t7.wait_before_stop(total_time, time_between_frames)

    def double_frame_3d(
            self, vmin, vmax, time_expo, time_between_frames, nb_levels,
            time_between_pairs, nb_couples,
            wait_file=False, nb_period_to_wait=1.0):
        '''Double frame PIV.

        Send a saw tooth signal to the galvanometer (DAC0) and a square signal
        to trig cameras (DAC1).

        Parameters
        ----------

        vmin, vmax:
          min and max of voltage (in V)

        time_expo:
          exposure time (in s)

        time_between_frames:
          time between 2 saw tooth (in s)

          Remark: the real time_between_frames can be different from
          input time_between_frames!!  time_between_frames = n/freq
          with n an integer and freq = nb_levels/tup

        nb_levels:
          number of steps in the rising part

        time_between_pairs:
          time between 2 pairs of saw tooth

        nb_couples:
          number of pairs of saw_tooth

        Returns
        -------

        time_between_frames: real time_between_frames time

        '''

        if time_between_pairs < (2 * time_between_frames):
            raise ValueError('time_between_pairs < (2 * time_between_frames)')

        if vmin < 0 or vmax > 5:
            raise ValueError('vmin < 0 or vmax > 5')

        IN_NAMES = []
        OUT_NAMES = ['DAC0', 'DAC1']

        volt, frequency, time_between_frames, t = double_saw_tooth2(
            vmin=vmin, vmax=vmax, time_expo=time_expo, nb_levels=nb_levels,
            time_between_frames=time_between_frames)
        print('volt = {}'.format(volt))
        print('frequency = {}'.format(frequency))
        tup = t[volt[0].argmax()] + time_expo
        scansPerRead = frequency
        scanRate = frequency
        TOTAL_NUM_CHANNELS = len(IN_NAMES) + len(OUT_NAMES)

        print(
            '\n' + '-' * 79 + '\n'
            'Connect DAC0 to connector 1 of PCO Edge camera\n' +
            '-' * 79 + '\n\n'
            'Settings in Camware software\n\n'
            '- trigger Mode to "Ext Exp Start"\n'
            '- frame rate >= {} Hz\n'.format(1.0/(tup/nb_levels)) +
            '- exposure <= {} s\n'.format(float(tup)/float(nb_levels)) +
            '- acquire Mode to "Auto"\n'
            '- I/O Signal: tick only "Exposure Trigger"\n'
            '- number of images: {}\n'.format(2*nb_couples*nb_levels) +
            'Start acquisition')

        t7 = self.t7
        handle = t7.handle

        aScanList = t7.prepare_stream(
            IN_NAMES=IN_NAMES, OUT_NAMES=OUT_NAMES, volt=volt)

        # to avoid a strange bug
        for indout, out in enumerate(OUT_NAMES):
            t7.write_out_buffer(
                'STREAM_OUT{}_BUFFER_F32'.format(indout), 0*volt[indout])

        scanRate = ljm.eStreamStart(
            handle, int(scansPerRead), TOTAL_NUM_CHANNELS, aScanList,
            scanRate)

        time.sleep(time_between_pairs)
        for indout, out in enumerate(OUT_NAMES):
            t7.write_out_buffer(
                'STREAM_OUT{}_BUFFER_F32'.format(indout), 0*volt[indout])

        time.sleep(time_between_pairs)
        # end of the code to avoid the strange bug

        if not query_yes_no('Are you ready to start acquisition?'):
            self.stop_stream()
            return

        save_exp(t, volt, time_expo=time_expo, tup=tup,
                 time_between_frames=time_between_frames,
                 time_between_pairs=time_between_pairs,
                 rootname='piv_scan_double_frame')

        if wait_file:
            wait_for_file('oscillate_*', nb_period_to_wait)

        timer = Timer(time_between_pairs)
        try:
            for i in range(nb_couples):
                scanRate = ljm.eStreamStart(
                    handle, int(scansPerRead), TOTAL_NUM_CHANNELS, aScanList,
                    scanRate)
                print('\r{}/{}'.format(i+1, nb_couples), end='')
                sys.stdout.flush()
                time.sleep(2*time_between_frames)
                for indout, out in enumerate(OUT_NAMES):
                    t7.write_out_buffer(
                        'STREAM_OUT{}_BUFFER_F32'.format(indout), volt[indout])
                t = timer.wait_tick()
        except KeyboardInterrupt:
            pass
        finally:
            print('')
            t7.stop_stream()

    def stop_stream(self):
        self.t7.stop_stream()


def multilevel_piv(time_between_frames, volt, tacq=None, nloop=None):
    '''
    multilevel_piv

    Parameters
    ----------

    volt : np.array
      signal to send to galvanometer

    time_between_frames : float
      the time between 2 levels of the laser sheet

    tacq :{None, float}
      time of acquition in each level

    nloop : integer
      loop nloop times the array volt
    '''
    if tacq >= time_between_frames:
        print("you need to verify tacq < time_between_frames")
        return None

    galva = Galva()
    handle = galva.t7.handle

    print(
        '\n' + '#' * 79 + '\n Connect DAC0 to the galvanometer'
        'Connect DAC1 to connector 2 of PCO Edge camera'
        '\n' + '#' * 79 + '\nSettings in Camware software:\n\n'
        '- Trigger Mode to "Auto Sequence"\n'
        '- Frame rate: what you desire'
        '- Exposure: what you desire'
        '- Acquire Mode to "External"\n'
        'I/O Signal: tick only "Acquire Enable"\n')

    test = True
    while test:
        resp = input("Are you ready to start the acquisition? (y/n)\n")
        if resp == "y":
            test = False
        else:
            return None

    if tacq is None:
        tacq = 0.9*time_between_frames

    if nloop is not None:
        voltperiod = volt
        for i in range(nloop):
            volt = np.hstack([volt, voltperiod])

    save_exp(np.linspace(0, volt.size*time_between_frames, volt.size), volt,
             rootname="multilevel_piv")
    timer = Timer(time_between_frames)
    for volti in volt:

        ljm.eWriteName(handle, 'DAC0', volti)
        ljm.eWriteName(handle, 'DAC1', 5)

        time.sleep(tacq)
        ljm.eWriteName(handle, 'DAC1', 0)
        timer.wait_tick()

    ljm.eWriteName(handle, 'DAC0', 0)
    ljm.eWriteName(handle, 'DAC1', 0)


# def saw_tooth_period(vmin, vmax, tup, nb_levels, time_between_frames):
#     ''' Determine the saw tooth profile for single frame acquisition
#        INPUT:
#            - vmin, vmax: min and max of voltage (in V)
#            - tup: rising time (in s)
#            - nb_levels: number of steps in the rising part
#            - time_between_frames: total time (in s)
#        OUTPUT:
#            - volt[0]: saw_tooth profile
#            - volt[1]: square wave to trig the camera
#            - freq: time frequency
#     '''
#     nb_levels -= 1
#     freq = 2.0 / (tup / nb_levels)
#     # multiplie )ar 2 l'échantillonage pour faire créneaux
#     N = time_between_frames * freq / 2.0

#     # first channel
#     volttemp = np.hstack([np.linspace(vmin, vmax, nb_levels+1)[:-1],
#                           np.linspace(vmax, vmin, N-nb_levels+1)[:-1]])
#     volt0 = np.zeros(volttemp.size * 2)
#     for ind in range(volttemp.size):
#         volt0[2*ind:2*ind+2] = np.asarray([volttemp[ind], volttemp[ind]])

#     # second channel
#     Vmin = 0.0
#     Vmax = 5.0
#     volttemp = np.hstack([np.zeros(nb_levels+1)+Vmax,
#                           np.zeros(N-nb_levels+1)[2:]+Vmin])

#     volt1 = np.zeros(volttemp.size * 2)
#     for ind in range(volttemp.size):
#         volt1[2*ind:2*ind+2] = np.asarray([volttemp[ind], 0])
#     print(volt0.shape, volt1.shape)
#     volt = np.vstack([volt0, volt1])

#     pylab.ion()
#     t = np.arange(0, time_between_frames, 1/freq)[0:volt0.size]
#     pylab.plot(t, volt[0], '+')
#     pylab.plot(t, volt[1], 'r+')
#     for i in range(int(t.size/2-1)):
#         pylab.plot(t[i*2:i*2+3],
#                    np.hstack([volt[0][i*2:i*2+2],
#                               volt[0][i*2+1]]), 'b-')
#         pylab.plot(t[i*2:i*2+2],
#                    np.hstack([volt[1][i*2:i*2+1],
#                               volt[1][i*2]]), 'r-')
#     pylab.plot(t[-2:], volt[0][-2:], 'b-')
#     pylab.plot(t[-2:], volt[1][-2:], 'r-')
#     pylab.plot((t[1]+t[-1])*np.ones(2), [0, 5], 'k')
#     pylab.ylim([-1, 6])
#     pylab.show()
#     pylab.draw()
#     return volt, freq, t


def saw_tooth_period2(vmin, vmax, time_expo, nb_levels, time_between_frames):
    ''' Determine the saw tooth profile for single frame acquisition

    Parameters
    ----------

    - vmin, vmax: min and max of voltage (in V)
    - time_expo: exposure time (in s)
    - nb_levels: number of steps in the rising part
    - time_between_frames: total time (in s)

    Returns
    -------

    - volt[0]: saw_tooth profile
    - volt[1]: square wave to trig the camera
    - freq: time frequency
    '''

    nb_levels -= 1
    freq = (2. / time_expo)

    N = time_between_frames / time_expo
    if (N != int(N)) or (N <= nb_levels):
        print("time_between_frames / time_expo has to be an integer larger than nb_levels ! ")
        return

    # Ndown = N - nb_levels

    # first channel
    volttemp = np.hstack([np.linspace(vmin, vmax, nb_levels+1)[:-1],
                          np.linspace(vmax, vmin, N-nb_levels+1)[:-1]])
    volt0 = np.zeros(volttemp.size * 2)
    for ind in range(volttemp.size):
        volt0[2*ind:2*ind+2] = np.asarray([volttemp[ind], volttemp[ind]])

    # second channel
    Vmin = 0.0
    Vmax = 5.0
    volttemp = np.hstack([np.zeros(nb_levels+1)+Vmax,
                          np.zeros(N-nb_levels+1)[2:]+Vmin])

    volt1 = np.zeros(volttemp.size * 2)
    for ind in range(volttemp.size):
        volt1[2*ind:2*ind+2] = np.asarray([volttemp[ind], 0])
    print(volt0.shape, volt1.shape)
    volt = np.vstack([volt0, volt1])

    pylab.figure()
    t = np.arange(0, time_between_frames, 1/freq)[0:volt0.size]
    pylab.plot(t, volt[0], '+')
    pylab.plot(t, volt[1], 'r+')
    for i in range(int(t.size/2-1)):
        pylab.plot(t[i*2:i*2+3],
                   np.hstack([volt[0][i*2:i*2+2],
                              volt[0][i*2+1]]), 'b-')
        pylab.plot(t[i*2:i*2+2],
                   np.hstack([volt[1][i*2:i*2+1],
                              volt[1][i*2]]), 'r-')
    pylab.plot((t[1]+t[-1])*np.ones(2), [0, 5], 'k')
    pylab.ylim([-1, 6])
    pylab.xlabel('t (s)')
    pylab.ylabel('voltage (V)')
    pylab.show()
    return volt, freq, t


# def double_saw_tooth(vmin, vmax, tup, nb_levels, time_between_frames):
#     '''Determine the saw tooth profile for double frame acquisition

#     Parameters
#     ----------

#     - vmin, vmax: min and max of voltage (in V)
#     - tup: rising time (in s)
#     - nb_levels: number of steps in the rising part
#     - time_between_frames: total time (in s)

#     Returns
#     -------

#     - volt[0]: saw_tooth profile
#     - volt[1]: square wave to trig the camera
#     - freq: time frequency
#     - time_between_frames: the calculated time_between_frames.

#     As freq is calculated such that freq = nb_levels/tup, time_between_frames is defined
#     as time_between_frames = n/freq with n an integer and can be different from input
#     time_between_frames.

#     '''
#     nb_levels -= 1

#     tdown = time_between_frames - tup
#     ttot = time_between_frames + tup + tdown
#     freq = 2.0 / (tup / nb_levels)
#     # multiplie )ar 2 l'échantillonage pour faire créneaux
#     Ndown = tdown / tup * nb_levels / 2.0
#     # N = ttot * freq / 2.0

#     # first channel
#     volttemp = np.hstack([np.linspace(vmin, vmax, nb_levels+1)[0:-1],
#                           np.linspace(vmax, vmin, Ndown+1)[0:-1],
#                           np.linspace(vmin, vmax, nb_levels+1)[0:-1],
#                           np.linspace(vmax, vmin, Ndown+1)[0:-1]])
#     volt0 = np.zeros(volttemp.size * 2 + 1)
#     for ind in range(volttemp.size):
#         volt0[2*ind:2*ind+2] = np.asarray([volttemp[ind], volttemp[ind]])
#     volt0[-1] = volt0[0]
#     # second channel
#     Vmin = 0
#     Vmax = 5
#     volttemp = np.hstack([np.zeros(nb_levels+1)+Vmax,
#                           np.zeros(Ndown+1)[2:]+Vmin,
#                           np.zeros(nb_levels+1)+Vmax,
#                           np.zeros(Ndown+1)[2:]+Vmin])
#     volt1 = np.zeros(volttemp.size * 2+1)
#     for ind in range(volttemp.size):
#         volt1[2*ind:2*ind+2] = np.asarray([volttemp[ind], 0])
#     volt1[-1] = 0
#     volt = np.vstack([volt0, volt1])

#     pylab.ion()
#     t = np.arange(0, ttot, 1/freq)[0:volt0.size]
#     # t = np.linspace(0, (N+1)/freq, 2 * N+1)[0:volt0.size]
#     pylab.plot(t, volt0, '+')
#     pylab.plot(t, volt[1], 'r+')
#     for i in range(int(t.size/2-1)):
#         pylab.plot(t[i*2:i*2+3],
#                    np.hstack([volt[0][i*2:i*2+2],
#                               volt[0][i*2+1]]), 'b-')
#         pylab.plot(t[i*2:i*2+2],
#                    np.hstack([volt[1][i*2:i*2+1],
#                               volt[1][i*2]]), 'r-')
#     pylab.plot(t[-2:], volt[0][-2:], 'b-')
#     pylab.plot(t[-2:], volt[1][-2:], 'r-')
#     pylab.ylim([-1, 6])
#     pylab.show()
#     pylab.draw()
#     time_between_frames = t[np.argwhere(volt0 == vmin)][2]
#     pylab.plot(time_between_frames*np.ones(2), [0, 5], 'k')
#     print("time_between_frames is set to {}s".format(time_between_frames))
#     return volt, freq, time_between_frames, t


def double_saw_tooth2(vmin, vmax, time_expo, nb_levels, time_between_frames):
    '''Determine the saw tooth profile for double frame acquisition

    Parameters
    ----------

    - vmin, vmax: min and max of voltage (in V)
    - time_expo: exposure time (in s)
    - nb_levels: number of steps in the rising part
    - time_between_frames: total time (in s)

    Returns
    -------

    - volt[0]: saw_tooth profile
    - volt[1]: square wave to trig the camera
    - freq: time frequency
    - time_between_frames: the calculated time_between_frames.

    As freq is calculated such that freq = nb_levels/tup,
    time_between_frames is defined as time_between_frames = n/freq
    with n an integer and can be different from input
    time_between_frames.

    '''
    nb_levels -= 1
    freq = (2.0 / time_expo)

    N = time_between_frames / time_expo
    # if (N != int(N)) or (N <= nb_levels):
    #     raise ValueError(
    #         "time_between_frames / time_expo has to be an integer larger than nb_levels !")

    Ndown = N - nb_levels
    # print('Ndown = {}'.format(Ndown))

    Ndown = int(Ndown)

    print(Ndown)

    # first channel
    volttemp = np.hstack([np.linspace(vmin, vmax, nb_levels+1)[0:-1],
                          np.linspace(vmax, vmin, Ndown+1)[0:-1],
                          np.linspace(vmin, vmax, nb_levels+1)[0:-1],
                          np.linspace(vmax, vmin, Ndown+1)[0:-1]])
    volt0 = np.zeros(volttemp.size * 2 + 1)
    for ind in range(volttemp.size):
        volt0[2*ind:2*ind+2] = np.asarray([volttemp[ind], volttemp[ind]])
    volt0[-1] = volt0[0]
    # second channel
    Vmin = 0
    Vmax = 5
    volttemp = np.hstack([np.zeros(nb_levels+1)+Vmax,
                          np.zeros(Ndown+1)[2:]+Vmin,
                          np.zeros(nb_levels+1)+Vmax,
                          np.zeros(Ndown+1)[2:]+Vmin])
    volt1 = np.zeros(volttemp.size * 2+1)
    for ind in range(volttemp.size):
        volt1[2*ind:2*ind+2] = np.asarray([volttemp[ind], 0])
    volt1[-1] = 0
    volt = np.vstack([volt0, volt1])

    pylab.figure()
    t = np.arange(0, time_between_frames * 2 + time_expo, 1/freq)[0:volt0.size]
    # t = np.linspace(0, (N+1)/freq, 2 * N+1)[0:volt0.size]
    pylab.plot(t, volt0, '+')
    pylab.plot(t, volt[1], 'r+')
    for i in range(int(t.size/2-1)):
        pylab.plot(t[i*2:i*2+3],
                   np.hstack([volt[0][i*2:i*2+2],
                              volt[0][i*2+1]]), 'b-')
        pylab.plot(t[i*2:i*2+2],
                   np.hstack([volt[1][i*2:i*2+1],
                              volt[1][i*2]]), 'r-')
    pylab.ylim([-1, 6])
    pylab.xlabel('t (s)')
    pylab.ylabel('voltage (V)')
    time_between_frames = t[np.argwhere(volt0 == vmin)][2]
    pylab.plot(time_between_frames*np.ones(2), [0, 5], 'k')
    pylab.show()
    print("time_between_frames is set to {}s".format(time_between_frames))
    return volt, freq, time_between_frames, t


def test_multilevel(T):
    t = np.linspace(0, 10, 1000)
    print(t[1] - t[0])
    volt = 3 + 2 * np.cos(t*2*np.pi/T)
    multilevel_piv(t[1] - t[0], volt)


def test_multilevel2():
    volt = np.arange(5)
    t = volt * 1
    multilevel_piv(t[1] - t[0], volt, outputname="DAC0")
