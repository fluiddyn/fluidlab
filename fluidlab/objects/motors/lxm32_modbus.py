
from __future__ import print_function

from threading import Thread
from time import sleep
import atexit
import sys
import signal

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.pdu import ExceptionResponse


def get_bit(number, idx):
    return (number & (1 << idx)) != 0

int32max = 2**31
int32min = -int32max
uint16max = 2**16


def sig_handler(signo, frame):
    sys.exit(0)


def split_int32(i):

    if i > int32max or i < int32min:
        raise ValueError

    if i < 0:
        i = abs(i)
        i |= 1 << 31
        i = i ^ 0xFFFFFFFF
        i |= 1 << 31
        i += 1

    i16_l = i >> 16
    i16_r = i & 0xFFFF

    return i16_l, i16_r


def parse_mf_stat(mf_stat):
    mode = mf_stat & 0x1F
    de = get_bit(mf_stat, 4)
    me = get_bit(mf_stat, 5)
    mt = get_bit(mf_stat, 6)
    return mode, de, me, mt


states = {
    1: 'Start (1)',
    2: 'Not Ready To Switch On (2)',
    3: 'Switch On Disabled (3)',
    4: 'Ready To Switch (4)',
    5: 'Switched On (5)',
    6: 'Operation Enabled (6)',
    7: 'Quick Stop Active (7)',
    8: 'Fault Reaction Active (8)',
    9: 'Fault (9)'}

modes = {1: 'Profile Position',
         3: 'Profile Velocity',
         4: 'Profile Torque',
         6: 'Homing',
         0x1f: 'Jog',
         0x1e: 'Electronic Gear',
         0x1d: 'Motion Sequence'}


class Motor(object):
    def __init__(self, ip_modbus='192.168.28.21',
                 disable_scan_timeout=False, disable_limit_switches=False):
        self._is_scanning = False
        self.client = ModbusClient(ip_modbus)
        if self.client.connect():
            print('connection ok')
        else:
            raise ValueError('bad modbus connection.')

        if disable_scan_timeout:
            ret = self.read_holding_registers(17498, 2)
            if ret.registers == [0, 20]:
                self.write_registers(17498, [0, 0])

        if disable_limit_switches:
            # disable limit switches (power stage must be disabled)
            self.write_registers(1566, [0]*4)

        self.ramp_v = self.read_ramp_v()

        self.dm_control = 0
        self.ref_a = [0, 0]
        self.ref_b = [0, 0]

        sleep(0.1)

        self.outscan = [0] * 13

        self._has_to_scan = True
        self._is_pingponging = False
        self.ioscanning_thread = Thread(target=self._ioscanning)
        self.ioscanning_thread.daemon = True
        self.ioscanning_thread.start()

        atexit.register(self.close)
        signal.signal(signal.SIGTERM, sig_handler)

    def close(self):
        print('close motor driver')
        self._has_to_scan = False
        while self._is_scanning:
            sleep(0.05)
        self.client.close()

    def __del__(self):
        self.close()

    def _disable_limit_switches(self):
        """disable limit switches (power stage must be disabled)"""
        self.disable()
        self.write_registers(1566, [0]*4)

    def _enable_limit_switches(self):
        """disable limit switches (power stage must be disabled)"""
        self.disable()
        self.write_registers(1566, [0, 1, 0, 1])

    def _build_output_scan(self):
        outscan = [0] * 4
        outscan[0] = 0x2 << 8

        old_out = self.outscan[4:]

        out = [self.dm_control]
        out.extend(self.ref_a)
        out.extend(self.ref_b)
        out.extend(self.ramp_v)

        if out != old_out:
            # flip toggle bit
            self.dm_control ^= 1 << 7
            out[0] = self.dm_control
            print('hex(dm_control):', hex(self.dm_control))

        outscan.extend(out)
        self.outscan = outscan
        assert len(outscan) == 13
        return outscan

    def read_holding_registers(self, address, count=1, **kwargs):
        ret = self.client.read_holding_registers(address, count, **kwargs)
        if isinstance(ret, ExceptionResponse):
            print('ExceptionResponse',
                  ret.exception_code, ret.function_code-128)
        return ret

    def write_registers(self, address, values, **kwargs):
        ret = self.client.write_registers(address, values, **kwargs)
        if isinstance(ret, ExceptionResponse):
            print('ExceptionResponse',
                  ret.exception_code, ret.function_code-128)
        return ret

    def compute_dm_control(
            self, mode=None, enable=None,
            quick_stop=None, fault_reset=None, halt=None,
            clear_halt=None, resume_after_halt=None):

        dm_control = self.dm_control

        if mode is not None:
            if not isinstance(mode, str):
                mode = str(mode)
            if mode.startswith('pos'):
                dm_control = 0x1
            elif mode.startswith('homing'):
                dm_control = 0x6
            else:
                dm_control = 0x23

        if enable:  # enable the power stage
            dm_control |= 1 << 9
        else:  # disable the power stage
            dm_control |= 1 << 8

        if quick_stop:
            dm_control |= 1 << 10

        if fault_reset:
            dm_control |= 1 << 11

        if halt:
            dm_control |= 1 << 13
        elif clear_halt:
            dm_control |= 1 << 14
        elif resume_after_halt:
            dm_control |= 1 << 15

        self.dm_control = dm_control

    def set_dm_control(
            self, mode=None, enable=None,
            quick_stop=None, fault_reset=None, halt=None,
            clear_halt=None, resume_after_halt=None):
        self.compute_dm_control(
            mode=mode, enable=enable, quick_stop=quick_stop,
            fault_reset=fault_reset,
            halt=halt,
            clear_halt=clear_halt, resume_after_halt=resume_after_halt)
        self._pingpong()

    def _ioscanning(self):
        self._is_scanning = True
        while self._has_to_scan:
            self._pingpong()
            sleep(0.5)
        self._is_scanning = False

    def _pingpong(self):
        while self._is_pingponging:
            sleep(0.05)

        self._is_pingponging = True
        self._build_output_scan()
        ret_write = self.write_registers(0, self.outscan, unit=255)

        if isinstance(ret_write, ExceptionResponse):
            print('ExceptionResponse',
                  ret_write.exception_code, ret_write.function_code-128)

        ret_read = self.read_holding_registers(0, 13, unit=255)
        registers = ret_read.registers

        self.par_ch = registers[:4]
        self.drive_stat = drive_stat = registers[4]
        self.mf_stat = mf_stat = registers[5]
        self.motion_stat = motion_stat = registers[6]
        self.drive_input = registers[7]
        self._p_act = registers[8:10]
        self._v_act = registers[10:12]
        self._I_act = registers[12]

        # decode drive_stat
        self.state = states[drive_stat & 0xF]

        self.error = get_bit(drive_stat, 6)
        self.warn = get_bit(drive_stat, 7)
        self.halt = get_bit(drive_stat, 8)
        self.homing = get_bit(drive_stat, 9)
        self.quick_stop = get_bit(drive_stat, 10)
        self.x_add1 = get_bit(drive_stat, 13)
        self.x_end = get_bit(drive_stat, 14)
        self.x_err = get_bit(drive_stat, 15)

        # mf_stat
        self.mode, self.de, self.me, self.mt = parse_mf_stat(mf_stat)

        # motion_stat
        self.motor_standstill = get_bit(motion_stat, 6)
        self.motor_pos = get_bit(motion_stat, 7)
        self.motor_neg = get_bit(motion_stat, 8)

        self._is_pingponging = False

    def get_state(self):
        return (
            'error: {}\nquick_stop: {}'.format(self.error, self.quick_stop) +
            'mode:' + hex(self.mode) +
            '\nde: {}; me: {}; mt: {}\n'.format(self.de, self.me, self.mt) +
            'x_add1: {}; x_end: {}; x_err: {}\n'.format(
                self.x_add1, self.x_end, self.x_err) +
            'drive_input: ' + bin(self.drive_input) +
            '\ndrive_stat: ' + bin(self.drive_stat) +
            '\nstate: ' + self.state +
            '\nmotor_neg: {}, motor_pos: {}, motor_standstill: {}'.format(
                self.motor_neg, self.motor_pos, self.motor_standstill))

    def print_state(self):
        print(self.get_state())

    def read_param(self, address, count=2):
        ret = self.read_holding_registers(address, count)
        return ret.registers

    def read_ramp_v(self):
        return self.read_param(1556, 4)

    def read_v_target(self):
        return self.read_param(6938)

    def read_position_target(self):
        return self.read_param(6940)

    def set_target_rotation_rate(self, i32):
        if self.state == 'Fault (9)':
            print('self.state == "Fault (9)"')
        if not isinstance(i32, int):
            i32 = int(round(i32))
        self.ref_a = list(split_int32(i32))
        self._pingpong()

    def set_target_position(self, i32):
        if self.state == 'Fault (9)':
            print('self.state == "Fault (9)"')
        if not isinstance(i32, int):
            i32 = int(round(i32))
        self.ref_b = list(split_int32(i32))
        self._pingpong()

    def stop_rotation(self):
        self.set_target_rotation_rate(0)

    def disable(self):
        self.set_target_rotation_rate(0)
        self.set_dm_control()

    def enable(self, mode=1):
        self.set_dm_control(mode=mode, enable=1)
        self.set_target_rotation_rate(0)

    def run_quick_stop(self):
        self.set_dm_control(quick_stop=True)

    def fault_reset(self):
        self.set_dm_control(fault_reset=1)

    def set_acceleration(self, a):
        a = abs(a)
        if not isinstance(a, int):
            a = int(round(a))
        if a > uint16max:
            a = uint16max
        self.ramp_v = [0, a] * 2
        self._pingpong()

    def get_position_actual(self):
        self._pingpong()
        return (self._p_act[0] << 16) + self._p_act[1]
