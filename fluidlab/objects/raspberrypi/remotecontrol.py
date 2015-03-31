"""
Remote control of RPi (:mod:`fluidlab.objects.raspberrypi.remotecontrol`)
=========================================================================


"""


from __future__ import division, print_function

try:
    import rpyc
except ImportError:
    pass

import shutil





class RaspBerryPi(object):
    """Remote control of the Raspberry pi.

    A `rpyc` server has to be run on the Raspberry Pi before creating
    a RaspBerryPi object.

    """
    def __init__(self):
        host = 'localhost'
        host = 'emperor.dampt.cam.ac.uk'
        host = '131.192.168.167'

        self.conn = rpyc.classic.connect(host, 18861)

        self.init_with_exp = self.conn.root.exposed_init_with_client
        self.measure = self.conn.root.exposed_measure




    def copy_file_from_pi(self, path_rasp, path_local):
        with open(path_local, 'w') as flocal:
            with self.conn.root.open(path_rasp) as f:
                shutil.copyfileobj(f, flocal)



if __name__ == '__main__':
    rbpi = RaspBerryPi()

    # rbpi.copy_file_from_pi('/home/pa371/temp_test', 'temp3')
