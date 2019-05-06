0.1.0
-----

- Change class hierarchy, so that interfaces are no longer under instruments.
  The new hierarchy highlights the separation between interface classes which
  implement communication with boards (e.g. VISA library or Linux-GPIB library to
  communicate with GPIB boards, socket to communicate with network devices,
  etc.), and instrument classes (both abstract and concrete) which represent
  specific devices. Some device may be connected in different manners, and some
  physical boards can be addressed with various libraries.

- Allow to use simple string description, e.g. VISA style string
  ("GPIB0::1::INSTR"), or IP address "192.168.0.4", in the __init__ method of
  devices, instead of an Interface object. The most appropriate Interface class
  will be infered from Instrument.default_interface class variable. Default
  association can be changed with the fluidlab.interface.set_default_interface
  function. In the future, permanent custom association could be provided with a
  dedicated user configuration file.

- Change all interface and instrument `__init__` method to restrain from
  opening communication. Indeed, one must not rely on the `__del__` method to
  close the connection. Instead, the underlying interface must be opened and
  closed using the `open()` and `close()` method, or a context manager must be
  used. The context manager will open and close the underlying interface
  appropriately. The Interface abstract base class maintains a boolean to retain
  the opened/closed state. Concreate Interface class must only implement _open
  and _close methods without checking openness. If some device requires
  initialisation communication, this should not be done in `__init__`. Either use
  a dedicated instance method, and call it explicitely, or overload the driver
  `__enter__`/`__exit__` methods.

0.0.1a
------

- Split the package fluiddyn between one base package and specialized
  packages.
