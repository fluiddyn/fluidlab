"""tti_cpx400dp
===============

.. autoclass:: TtiCpx400dp
   :members:
   :private-members:


"""

__all__ = ['TtiCpx400dp']

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue, BoolValue

class TtiCpx400dpUnitValue(FloatValue):
	def _convert_from_str(self, value):
		index_v = value.find('V')
		index_i = value.find('A')
		if index_v > index_i:
			index = index_v
		else:
			index = index_i
		return float(value[0:index])
	
class TtiCpx400dp(IEC60488):
    """Driver for the power supply TTI CPX400DP
	   Dual 420 watt DC Power Supply
	   
    """
	
features = [
	TtiCpx400dpUnitValue(
		'vdc',
		doc='Get actual voltage/Set voltage setpoint on specified channel',
		command_set='V{channel} {value}',
		command_get='V{channel}O?',
		channel_argument=True,
		check_instrument_value=False),
	TtiCpx400dpUnitValue(
		'idc',
		doc='Get actual current/Set current setpoint on specified channel',
		command_set='I{channel} {value}',
		command_get='I{channel}O?',
		channel_argument=True,
		check_instrument_value=False),
	BoolValue(
		'onoff',
		doc='Toogle output ON/OFF for specified channel',
		command_set='OP{channel} {value}',
		command_get='OP{channel}?',
		channel_argument=True,
		check_instrument_value=False),
	BoolValue(
		'onoffall',
		doc='Toogle output ON/OFF for both channels simultaneously',
		command_set='OPALL ',
		channel_argument=False,
		check_instrument_value=False)]

TtiCpx400dp._build_class_with_features(features)
