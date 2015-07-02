"""A false interface... (:mod:`fluidlab.instruments.interface`)
===============================================================

Provides:

.. autoclass:: Interface
   :members:
   :private-members:

"""


class Interface(object):
    def write(self, s):
        print(s)

    def read(self):
        return 'read nothing since it is a false Interface class.'

    def query(self, s):
        self.write(s)
        return self.read()
