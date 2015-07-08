"""Interfaces with the instruments (:mod:`fluidlab.instruments.interfaces`)
===========================================================================

Provides:

.. autoclass:: Interface
   :members:
   :private-members:

.. autoclass:: FalseInterface
   :members:
   :private-members:

"""


class Interface(object):
    pass


class FalseInterface(Interface):
    def write(self, s):
        print(s)

    def read(self):
        print('read 0 since it is a false Interface class.')
        return 0

    def query(self, s):
        self.write(s)
        return self.read()
