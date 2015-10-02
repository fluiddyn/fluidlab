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
        command_str='STATUS?'
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

HP34401a._build_class_with_features(features)
