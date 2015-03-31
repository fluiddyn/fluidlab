"""Data Acquisition boards (:mod:`fluidlab.objects.boards`)
===========================================================

.. _lab.boards:
.. currentmodule:: fluidlab.objects.boards

Provides two small classes, :class:`ObjectUsingBoard` and the modules:

.. autosummary::
   :toctree:

   nidaqnx

**Remark**: Can not import the module
:mod:`fluidlab.objects.boards.powerdaq` in Linux... So no doc!


The classes for data acquisition boards should be obtained from this
package. If the boards are not available, no error are raised and the
classes are replaced by the class
:class:`fluidlab.objects.boards.FalseBoard`.

For example, with a computer without PowerDAQ board::

    from fluidlab.objects.boards import PowerDAQBoard
    board = PowerDAQBoard() # no error
    assert(board.works == False) # no error
    assert(not board) # no error
    board.ain.configure(sample_rate=100) 
    # AttributeError: You tried to use a false acquisition board.


.. autoclass:: ObjectUsingBoard
   :members:
   :private-members:

.. autoclass:: FalseBoard
   :members:
   :private-members:

"""

from fluiddyn.io import _write_warning

class FalseBoard(object):
    """Represent a false acquisition board.

    This object tested as a boolean is False. It has an attribute
    `works` equal to False and an AttributeError on it returns an
    understandable message.

    """
    works = False
    def __getattr__(self, key):
        raise AttributeError('You tried to use a false acquisition board.')
    def __bool__(self):
        """For python => 3.0"""
        return False
    def __nonzero__(self):
        """For python < 3"""
        return False



try:
   from .powerdaq import PowerDAQBoard
except ImportError:
    _write_warning(
       'Warning:\n    no fluidlab.objects.boards.powerdaq (use FalseBoard).')
    PowerDAQBoard = FalseBoard


from . import nidaqnx

if nidaqnx.works:
    NIDAQBoard = nidaqnx.NIDAQBoard
else:
    _write_warning(
       'Warning:\n    '
       'no fluidlab.objects.boards.nidaqnx.NIDAQBoard (use FalseBoard).')
    NIDAQBoard = FalseBoard







class ObjectUsingBoard(object):
    """Useful to write classes for objects using a board."""
    def __init__(self, board=None, VERBOSE=False):
        if board is None and VERBOSE:
            print(
"""Warning: none instance of the class PowerDAQBoard (or NIDAQBoard)
has been given. Some functions need the board."""
            )
        self.board = board

