"""Iso-tech IPS 2303S
=====================

.. autoclass:: IsoTechIPS2303S
   :members:
   :private-members:

"""

from serial.tools.list_ports import comports

from fluidlab.instruments.drivers import Driver

from fluidlab.instruments.interfaces.serial_inter import SerialInterface

from fluidlab.instruments.features import (
    QueryCommand, FloatValue)


class FloatValue2(FloatValue):
    _fmt = '{:5.3f}'

    def __init__(self, name, doc='', command_set=None):

        if command_set is None:
            raise ValueError('command_set should be a string.')

        command_get = command_set + '?\r\n'

        super(FloatValue2, self).__init__(
            name=name, doc=doc,
            command_set=command_set, command_get=command_get)

    def _convert_from_str(self, value):
        return value.strip()

    def get(self):
        """Get the value from the instrument."""
        result = self._convert_from_str(
            self._interface.query(self.command_get))
        self._check_value(result)
        return result

    def set(self, value, warn=True):
        """Set the value in the instrument."""
        self._check_value(value)
        self._interface.write(
            self.command_set + ':' +
            self._convert_as_str(value) + '\n')
        if warn:
            self._check_instrument_value(value)


class IsoTechIPS2303S(Driver):
    """Driver for the power supply IPS 2303S.

    """
    def __init__(self):

        port = None
        for info_port in comports():
            if '0403:6001' in info_port[2]:
                port = info_port[0]

        if port is None:
            raise ValueError('The device does not seem to be plugged.')

        interface = SerialInterface(port, baudrate=9600, bytesize=8,
                                    parity='N', stopbits=1, timeout=1)

        super(IsoTechIPS2303S, self).__init__(interface)


def _parse_status_code(code):

    return code


features = [
    QueryCommand(
        'query_identification', 'Identification query',
        command_str='*IDN?\r\n'),
    QueryCommand(
        'query_status',
        'Query status\n\n'
        'Return a dictionary containing information of the device.',
        command_str='STATUS?\r\n',
        parse_result=_parse_status_code)]

for channel in [1, 2]:
    features.extend([
        FloatValue2(
            'iset{}'.format(channel),
            doc='Set the output current for channel {}.'.format(channel),
            command_set='ISET{}'.format(channel)),
        FloatValue2(
            'vset{}'.format(channel),
            doc='Set the output voltage for channel {}.'.format(channel),
            command_set='VSET{}'.format(channel)),
        QueryCommand(
            'get_iout{}'.format(channel),
            'Get the actual output current for channel {}.'.format(channel),
            'IOUT{}?\r\n'.format(channel)),
        QueryCommand(
            'get_vout{}'.format(channel),
            'Get the actual output voltage for channel {}.'.format(channel),
            'VOUT{}?\r\n'.format(channel))])


IsoTechIPS2303S._build_class_with_features(features)


def idn_with_serial():
    import serial

    port = None
    for info_port in comports():
        if '0403:6001' in info_port[2]:
            port = info_port[0]

    if port is None:
        raise ValueError('The device does not seem to be plugged.')

    sp = serial.Serial(
        port=port,
        baudrate=9600,  # warning: does work for higher baudrate!
        timeout=1, bytesize=8, parity='N', stopbits=1)

    sp.readline()

    sp.write('*IDN?\r\n')

    print(sp.readline())

    return sp


def idn_with_visa():
    import visa

    rm = visa.ResourceManager('@py')

    # for r in rm.list_resources():
    #     if 'ttyUSB' in r:
    #         resource_name = r

    # print(resource_name)

    resource_name = 'ASRL/dev/ttyUSB0::INSTR'

    instr = rm.open_resource(resource_name)

    instr.write('*IDN?\r\n')

    print(instr.read())


if __name__ == '__main__':
    sp = idn_with_serial()
    # idn_with_visa()
