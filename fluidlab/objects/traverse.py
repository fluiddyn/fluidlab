"""
Traverses (:mod:`fluidlab.objects.traverse`)
============================================

.. currentmodule:: fluidlab.objects.traverse

Provides:

.. autoclass:: Traverse
   :members:

"""

from __future__ import division, print_function

import numpy as np
import time

from fluidlab.objects.boards import ObjectUsingBoard




class Traverse(ObjectUsingBoard):
    """Represent a traverse."""

    def __init__(self, board=None, 
                 position_start=300.,
                 position_max=None,
                 Deltaz=400.,
             ):

        super(Traverse, self).__init__(board=board)

        self.mm_per_step = 454./3000 # (mm)

        position_start = float(position_start)
        Deltaz = float(Deltaz)

        self.position = position_start
        if position_max is None:
            self.pos_max = position_start
        else:
            self.pos_max = float(position_max)
        self.pos_min = self.pos_max-Deltaz

        self.board = board





    def  move_nb_steps(self, 
                       direction="up", nb_steps=200, 
                       steps_per_second=500,
                       bloquing=False):
        """Moves `nb_steps` in the direction `direction`.

        Parameters
        ----------
        direction : str
           The direction.

        nb_steps : int
           The number of steps.

        steps_per_second : number
           The number of steps per second (fixing the speed).

        bloquing : bool
           Whether or not the function should be bloquing.
        """
        driving_signal = 2*np.ones([nb_steps*2])
        driving_signal[::2] = 5
        if direction == "up": driving_signal *= -1
        
        self.board.aout(out0=driving_signal, frequency=steps_per_second*2)
        if bloquing:
            time_to_sleep = nb_steps/steps_per_second
            # print(time_to_sleep)
            time.sleep(time_to_sleep)



    def move(self, deltaz=100, speed=100, bloquing=False):
        """
        Move by a particular distance with a particular speed.

        Parameters
        ----------
        deltaz: number
           Distance to move (in mm).

        speed: number
           (in mm/s)
        """
        nb_steps = abs(np.round(deltaz/self.mm_per_step))
        steps_per_second = np.round(speed/self.mm_per_step)

        if deltaz > 0: direction = "up"
        else: direction = "down"

        self.move_nb_steps(
            direction=direction, nb_steps=nb_steps,
            steps_per_second=steps_per_second, 
            bloquing=bloquing)

        deltaz = nb_steps*self.mm_per_step
        if direction == "down": deltaz *= -1

        self.position += deltaz

        self._verify_position()


    def _verify_position(self):
        if self.position > self.pos_max:
            self.position = self.pos_max
        elif self.position < self.pos_min:
            self.position = self.pos_min

        # print('new position: {0:5.1f} mm'.format(self.position))



    def gotopos(self, position, speed=100, bloquing=True):
        """Go as close as possible of a position"""
        if position < self.pos_min:
            position = self.pos_min
        elif position > self.pos_max:
            position = self.pos_max
        deltaz = position - self.position
        self.move(deltaz=deltaz, speed=speed, bloquing=bloquing)



if __name__ == '__main__':

    from fluiddyn.util.timer import Timer

    from fluidlab.objects.boards import PowerDAQBoard

    board = PowerDAQBoard()

    traverse = Traverse(board=board)

    distance = 150

    timer = Timer(4)
    for i in xrange(2):
        print('down')
        traverse.move(deltaz=-distance, speed=100, bloquing=True)
        print('up')
        traverse.move(deltaz=distance, speed=50, bloquing=True)
        print('wait')
        timer.wait_till_tick()

