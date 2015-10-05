"""Iso-tech IPS 2303S
============

.. autoclass:: IsoTechIPS2303S
   :members:
   :private-members:

"""

from fluidlab.instruments.drivers import VISADriver

from fluidlab.instruments.features import (
    QueryCommand, FloatValue)


class IsoTechIPS2303S(VISADriver):
    """Driver for the power supply IPS 2303S.

    """


def _parse_status_code(code):

    return code


features = [
    QueryCommand(
        'query_identification', 'Identification query',
        command_str='*IDN?'),
    QueryCommand(
        'query_status',
        'Query status\n\n'
        'Return a dictionary containing information of the device.',
        command_str='STATUS?',
        parse_result=_parse_status_code)]

for channel in [1, 2]:
    features.extend([
        FloatValue(
            'iset{}'.format(channel),
            doc='Set the output current for channel {}.'.format(channel),
            command_get='ISET{}?'.format(channel)),
        FloatValue(
            'vset{}'.format(channel),
            doc='Set the output voltage for channel {}.'.format(channel),
            command_get='VSET{}?'.format(channel)),
        QueryCommand(
            'get_iout{}'.format(channel),
            'Get the actual output current for channel {}.'.format(channel),
            'IOUT{}'.format(channel)),
        QueryCommand(
            'get_vout{}'.format(channel),
            'Get the actual output voltage for channel {}.'.format(channel),
            'VOUT{}'.format(channel)),
    ])


IsoTechIPS2303S._build_class_with_features(features)


if __name__ == '__main__':

    import serial
    from serial.tools.list_ports import comports

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

    sp.write('*IDN?\r\n'.encode())

    print(sp.readline())
