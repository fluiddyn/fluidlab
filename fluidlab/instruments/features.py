"""Features (:mod:`fluidlab.instruments.features`)
==================================================

Provides:

.. autoclass:: Feature
   :members:
   :private-members:

.. autoclass:: FunctionCommand
   :members:
   :private-members:

.. autoclass:: Value
   :members:
   :private-members:

.. autoclass:: ValueBool
   :members:
   :private-members:

"""


class Feature(object):
    def __init__(self, name, doc=''):
        self._name = name
        self.__doc__ = doc

    def __repr__(self):
        if len(self.__doc__) > 0:
            return (super(Feature, self).__repr__() + '\n\n' + self.__doc__)
        else:
            return super(Feature, self).__repr__()


class FunctionCommand(Feature):
    def __init__(self, name, doc='', command_str=''):
        super(FunctionCommand, self).__init__(name, doc)
        self.command_str = command_str

    def _build_driver_class(self, Driver):
        command_str = self.command_str

        def func(self):
            self.interface.write(command_str)
        func.__doc__ = self.__doc__
        setattr(Driver, self._name, func)


class Value(Feature):
    def __init__(self, name, doc='', command_get=None, command_set=None):
        super(Value, self).__init__(name, doc)
        self.command_get = command_get
        self.command_set = command_set

    def _build_driver_class(self, Driver):
        name = self._name
        command_get = self.command_get
        command_set = self.command_set

        setattr(Driver, name, self)

        def get(self):
            """Get """ + name
            return self._interface.query(command_get)

        setattr(Driver, 'get_' + self._name, get)
        self.get = get.__get__(self, self.__class__)

        def set(self):
            """Set """ + name
            self._interface.write(command_set)

        setattr(Driver, 'set_' + self._name, set)
        self.set = set.__get__(self, self.__class__)


class BoolValue(Value):
    pass


class StringValue(Value):
    def __init__(self, name, doc='', command_get=None, command_set=None,
                 possible_values=None):
        super(StringValue, self).__init__(name, doc)
        self.command_get = command_get
        self.command_set = command_set
        self.possible_values = possible_values

    def _check_value(self, value):
        if (self.possible_values is not None and
                value not in self.possible_values):
            raise ValueError(
                'Value {} not in possible_values, which is equal to {}'.format(
                    value, repr(self.possible_values)))

    def _build_driver_class(self, Driver):
        name = self._name
        command_get = self.command_get
        command_set = self.command_set

        setattr(Driver, name, self)

        def get(self):
            """Get """ + name
            value = self._interface.query(command_get)
            self._check_value(value)
            return value

        self.get = get.__get__(self, self.__class__)

        def set(self, value):
            """Set """ + name
            self._check_value(value)
            self._interface.write(command_set)

        self.set = set.__get__(self, self.__class__)


class NumberValue(Value):
    def __init__(self, name, doc='', command_get=None, command_set=None,
                 limits=None):
        super(NumberValue, self).__init__(name, doc)
        self.command_get = command_get
        self.command_set = command_set

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

    def _build_driver_class(self, Driver):
        name = self._name
        command_get = self.command_get
        command_set = self.command_set

        setattr(Driver, name, self)

        def get(self):
            """Get """ + name
            value = self._interface.query(command_get)
            self._check_value(value)
            return value

        self.get = get.__get__(self, self.__class__)

        def set(self, value):
            """Set """ + name
            self._check_value(value)
            self._interface.write(command_set)

        self.set = set.__get__(self, self.__class__)
