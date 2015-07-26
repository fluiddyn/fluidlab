"""
Pinching valve (:mod:`fluidlab.objects.pinchvalve`)

.. currentmodule:: fluidlab.objects.pinchvalve

Provides:

.. autoclass:: PinchValve
   :members:

.. autoclass:: ContextManagerOpenedValve
   :members:

.. autoclass:: FalseContextManager
   :members:

.. autofunction:: tube_as_opened_as_possible


"""

from __future__ import division, print_function

from fluidlab.objects.boards import ObjectUsingBoard


class PinchValve(ObjectUsingBoard):
    """A class handling the pinch valve."""
    def __init__(self, board=None, channel=0):

        super(PinchValve, self).__init__(board=board)
        self.channel = channel
        self.close()

    def open(self):
        self.board.dout.write(2**self.channel)

    def close(self):
        self.board.dout.write(0)

    def opened(self):
        return ContextManagerOpenedValve(self)


class ContextManagerOpenedValve(object):
    def __init__(self, valve):
        self.valve = valve

    def __enter__(self):
        self.valve.open()
        return self.valve

    def __exit__(self, type, value, traceback):
        self.valve.close()


class FalseContextManager(object):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


def tube_as_opened_as_possible(valve):
    if valve is not None:
        return ContextManagerOpenedValve(valve)
    else:
        return FalseContextManager()


if __name__ == '__main__':
    import time
    from fluidlab.objects.boards import PowerDAQBoard

    from fluiddyn.util.timer import Timer

    period = 4 # (s)

    board = PowerDAQBoard()
    valve = PinchValve(board)
    # valve = None

    timer = Timer(period)
    for i in xrange(10):
        time.sleep(1)
        # with valve.opened():
        with tube_as_opened_as_possible(valve):
            print('valve opened.')
            timer.wait_tick()
        print('valve closed.')
