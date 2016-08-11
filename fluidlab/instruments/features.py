"""Features for defining drivers (:mod:`fluidlab.instruments.features`)
=======================================================================

.. todo:: Work on the documentation of :mod:`fluidlab.instruments.features`.

Provides:

.. autoclass:: Feature
   :members:
   :private-members:

.. autoclass:: WriteCommand
   :members:
   :private-members:

.. autoclass:: QueryCommand
   :members:
   :private-members:

.. autoclass:: Value
   :members:
   :private-members:

.. autoclass:: BoolValue
   :members:
   :private-members:

.. autoclass:: StringValue
   :members:
   :private-members:

.. autoclass:: NumberValue
   :members:
   :private-members:

.. autoclass:: IntValue
   :members:
   :private-members:

.. autoclass:: FloatValue
   :members:
   :private-members:

.. autoclass:: RegisterValue
   :members:
   :private-members:

"""
import warnings, time
import six

def custom_formatwarning(message, category, filename, lineno, line=None):
    return '{}:{}: {}: {}\n'.format(
        filename, lineno, category.__name__, message)


warnings.formatwarning = custom_formatwarning
warnings.simplefilter('always', UserWarning)
# warnings.simplefilter('always', Warning)
# warnings.simplefilter('always')


class Feature(object):
    def __init__(self, name, doc=''):
        self._name = name
        self.__doc__ = doc


class WriteCommand(Feature):
    def __init__(self, name, doc='', command_str=''):
        super(WriteCommand, self).__init__(name, doc)
        self.command_str = command_str

    def _build_driver_class(self, Driver):
        """Add a "write function" to the driver class

        """
        command_str = self.command_str

        def func(self):
            self._interface.write(command_str)

        func.__doc__ = self.__doc__
        setattr(Driver, self._name, func)


class QueryCommand(Feature):
    def __init__(self, name, doc='', command_str='', parse_result=None):
        super(QueryCommand, self).__init__(name, doc)
        self.command_str = command_str
        self.parse_result = parse_result

    def _build_driver_class(self, Driver):
        """Add a "query function" to the driver class

        """
        command_str = self.command_str

        parse_result = self.parse_result

        if parse_result is None:
            def func(self):
                return self._interface.query(command_str)
        else:
            def func(self):
                return parse_result(self._interface.query(command_str))

        func.__doc__ = self.__doc__
        setattr(Driver, self._name, func)


class SuperValue(Feature):
    def _build_driver_class(self, Driver):
        name = self._name
        setattr(Driver, name, self)


class Value(SuperValue):
    _fmt = '{}'

    def __init__(self, name, doc='', command_set=None, command_get=None, check_instrument_value=True, pause_instrument=0.0, channel_argument=False):
        super(Value, self).__init__(name, doc)
        self.command_set = command_set
        self.check_instrument_value_after_set = check_instrument_value

        self.pause_instrument = pause_instrument
        # certains appareils plantent si on leur parle sans faire de pauses
        
        self.channel_argument = channel_argument
        # if true, then get() and set() needs a channel argument
        # in that case, command_get and command_set strings are provided
        # with python string format arguments {channel} and {value}

        if command_get is None and command_set is not None:
            command_get = command_set + '?'

        self.command_get = command_get

    def _check_value(self, value):
        pass

    def _check_instrument_value(self, value):
        pass

    def _convert_from_str(self, value):
        return value.strip()

    def _convert_as_str(self, value):
        return self._fmt.format(value)

    def get(self, channel=0):
        """Get the value from the instrument.
           Optional argument 'channel' is used for multichannel instrument.
           Then command_get should include '%d'
        """
        if self.pause_instrument > 0:
            time.sleep(self.pause_instrument)
        command = self.command_get
        if(self.channel_argument):
            command = command.format(channel=channel)
        result = self._convert_from_str(
            self._interface.query(command))
        self._check_value(result)
        return result

    def set(self, value, channel=0):
        """Set the value in the instrument.
           Optional argument 'channel' is used for multichannel instrument.
           Then command_set argument should include '%d'
        """
        if self.pause_instrument > 0:
            time.sleep(self.pause_instrument)
        self._check_value(value)
        if self.channel_argument:
            command = self.command_set.format(channel=channel, value=self._convert_as_str(value))
        else:
            command = self.command_set + ' ' + self._convert_as_str(value)
        self._interface.write(command)
        if self.check_instrument_value_after_set:
            self._check_instrument_value(value)


class BoolValue(Value):
    def __init__(self, name, doc='', command_set=None, command_get=None, check_instrument_value=True, pause_instrument=0.0, channel_argument=False, true_string='1', false_string='0'):
        super(BoolValue, self).__init__(name, doc, command_set, command_get, check_instrument_value, pause_instrument, channel_argument)
        self.true_string = true_string
        self.false_string = false_string

    def _convert_from_str(self, value):
        value = value.strip()
        if value == self.false_string:
            return False
        else:
            return True

    def _convert_as_str(self, value):
        if value:
            return self.true_string
        else:
            return self.false_string

    def _check_instrument_value(self, value):
        instr_value = self.get()
        if instr_value != value:
            msg = (self._name + ' could not be set to ' +
                   str(value) + ' and was set to ' +
                   str(instr_value) + ' instead')
            warnings.warn(msg, UserWarning)


class StringValue(Value):
    def __init__(self, name, doc='', command_set=None, command_get=None,
                 valid_values=None, check_instrument_value=True, pause_instrument=0.0, channel_argument=False):
        super(StringValue, self).__init__(
            name, doc, command_set=command_set, command_get=command_get, check_instrument_value=check_instrument_value, pause_instrument=pause_instrument, channel_argument=channel_argument)
        self.valid_values = valid_values

    def _check_value(self, value):
        value = value.lower()
        if (self.valid_values is not None and
                value not in self.valid_values):
            raise ValueError(
                'Value "{}" not in valid_values, which is equal to {}'.format(
                    value, repr(self.valid_values)))

    def _check_instrument_value(self, value):
        value = value.lower()
        instr_value = self.get().lower()
        if not(value.startswith(instr_value)):
            msg = (self._name + ' could not be set to ' +
                   str(value) + ' and was set to ' +
                   str(instr_value) + ' instead')
            warnings.warn(msg, UserWarning)


class NumberValue(Value):
    def __init__(self, name, doc='', command_set=None, command_get=None,
                 limits=None, check_instrument_value=True, pause_instrument=0.0, channel_argument=False):
        super(NumberValue, self).__init__(
            name, doc, command_set=command_set, command_get=command_get, check_instrument_value=check_instrument_value, pause_instrument=pause_instrument, channel_argument=channel_argument)

        if limits is not None and len(limits) != 2:
            raise ValueError(
                'limits have to be a sequence of length 2 or None')

        self.limits = limits

    def _check_value(self, value):
        if self.limits is None:
            return

        lim_min = self.limits[0]
        lim_max = self.limits[1]

        if (lim_min is not None and value < lim_min):
            raise ValueError(
                'Value ({}) is smaller than lim_min ({})'.format(
                    value, lim_min))

        if (lim_max is not None and value > lim_max):
            raise ValueError(
                'Value ({}) is larger than lim_max ({})'.format(
                    value, lim_max))

    def _check_instrument_value(self, value):
        instr_value = self.get()
        if abs(instr_value-value) > 0.001*abs(value):
            msg = (self._name + ' could not be set to ' +
                   str(value) + ' and was set to ' +
                   str(instr_value) + ' instead')
            warnings.warn(msg, UserWarning)


class FloatValue(NumberValue):
    _fmt = '{:f}'

    def _convert_from_str(self, value):
        return float(value)


class IntValue(NumberValue):
    _fmt = '{:d}'

    def _convert_from_str(self, value):
        return int(value)


class RegisterValue(NumberValue):
    def __init__(self, name, doc='', command_set=None, command_get=None,
                 keys=None, default_value=0, check_instrument_value=True, pause_instrument=0.0, channel_argument=False):

        if keys is None:
            raise ValueError('Keys has to contain the keys of the register.')

        self.keys = keys
        self.nb_bits = len(keys)

        limits = (0, 2**self.nb_bits)

        super(RegisterValue, self).__init__(
            name, doc, command_set=command_set, command_get=command_get,
            limits=limits, check_instrument_value=check_instrument_value, pause_instrument=pause_instrument, channel_argument=channel_argument)

        if isinstance(default_value, six.integer_types):
            self.default_value = self.compute_dict_from_number(default_value)
        elif isinstance(default_value, dict):
            for k in default_value.keys():
                if k not in keys:
                    raise ValueError('key {} not in keys'.format(k))
            for k in keys:
                default_value.setdefault(k, False)
            self.default_value = default_value
        else:
            raise ValueError('default_value has to be an int or a dict.')

    def _build_driver_class(self, Driver):
        name = self._name
        setattr(Driver, name, self)

    def get_as_number(self):
        """Get the register as number."""
        value = self._interface.query(self.command_get)
        self._check_value(value)
        return value

    def get(self):
        """Get the register as dictionary."""
        number = self.get_as_number()
        return self.compute_dict_from_number(number)

    def set(self, value):
        """Set the register.

        Parameters
        ----------

        value : {dict, int}
           The value as a dictionnary or an integer.

        """

        if isinstance(value, dict):
            value = self.compute_number_from_dict(value)

        self._check_value(value)
        self._interface.write(self.command_set + ' {}'.format(value))

    def compute_number_from_dict(self, d):
        for k in d.keys():
            if k not in self.keys:
                raise ValueError('key {} not in keys'.format(k))

        self._complete_dict_with_default(d)

        number = 0
        for i, k in enumerate(self.keys):
            if d[k]:
                number += 2**i
        return number

    def compute_dict_from_number(self, number):
        s = bin(number)[2:].zfill(self.nb_bits)

        d = {}
        for i, k in enumerate(self.keys):
            d[k] = s[-1-i] == '1'

        return d

    def _complete_dict_with_default(self, d):
        for k, v in self.default_value.items():
            d.setdefault(k, v)
