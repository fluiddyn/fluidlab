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
    def __repr__(self):
        return (super(Feature, self).__repr__() + '\n' + self.__doc__)


class FunctionCommand(Feature):
    def __init__(self, name, command_str, doc):
        self._name = name
        self.command_str = command_str
        self.__doc__ = doc

    def _complete_driver_class(self, Driver):
        command_str = self.command_str

        def func(self):
            self.interface.write(command_str)
        func.__doc__ = self.__doc__
        setattr(Driver, self._name, func)


class Value(Feature):
    def __init__(self, name, command_get=None, command_set=None,
                 doc=None):
        self._name = name
        self.command_get = command_get
        self.command_set = command_set
        self.__doc__ = doc


class ValueBool(Value):
    def __init__(self, name, command_get=None, command_set=None,
                 doc=None):
        self._name = name
        self.command_get = command_get
        self.command_set = command_set
        self.__doc__ = doc

    def _complete_driver_class(self, Driver):
        name = self._name
        command_get = self.command_get
        command_set = self.command_set

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

        setattr(Driver, self._name, self)
