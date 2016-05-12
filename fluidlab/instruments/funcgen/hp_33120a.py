"""Hewlett Packard 33120A
=========================

.. autoclass:: HP33120a
   :members:
   :private-members:


"""

__all__ = ['HP33120a']

from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import SuperValue, FloatValue

class HP33120a(IEC60488):
	"""
	Driver for the function generator Hewlett-Packard 33120A
	
	"""

class HP33120a_ShapeValue(SuperValue):
	shapes = {'sine': 'SIN', 'square': 'SQU', 'triangle': 'TRI',
			  'ramp': 'RAMP', 'noise': 'NOIS', 'dc': 'DC'}
			  
	def __init__(self):
		super(HP33120a_ShapeValue, self).__init__(
			'shape', doc='Shape of the output signal')
	
	def set(self, value):
		if value not in self.shapes.keys():
			raise ValueError('Bad shape name. Possible values are sine, square, triangle, ramp, noise or dc')
		self._interface.write('SOUR:FUNC:SHAP ' + self.shapes[value])
		
	def get(self):
		rvalue = self._interface.query('SOUR:FUNC:SHAP?')
		if rvalue.endswith('\n'):
			rvalue=rvalue[:-1]
		rkey = None
		for key,value in self.shapes.iteritems():
			if value == rvalue:
				rkey = key
		return rkey
		
features = [
	FloatValue('freq',
			   doc='Frequency of output signal',
			   command_get='SOUR:FREQ?',
			   command_set='SOUR:FREQ',
			   check_instrument_value=False),
	FloatValue('vrms',
			   doc='Set/get output amplitude (default to INF load)',
			   command_get='SOUR:VOLT:UNIT VRMS\nSOUR:VOLT?',
			   command_set='SOUR:VOLT:UNIT VRMS\nOUTP:LOAD INF\nSOUR:VOLT',
			   check_instrument_value=False),
	FloatValue('load',
			   doc='Get/Select the output termination',
			   command_get='OUTP:LOAD?',
			   command_set='OUTP:LOAD',
			   check_instrument_value=False),
	HP33120a_ShapeValue()]

HP33120a._build_class_with_features(features)
