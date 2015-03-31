"""Server (:mod:`fluidlab.objects.raspberrypi.server`)
======================================================

Defines a rpyc server.

"""

import os
try:
    from rpyc import SlaveService
    from rpyc.utils.server import ThreadedServer
except ImportError:
    SlaveService = object


from fluiddyn.io import FLUIDDYN_PATH_EXP
from fluidlab.objects.raspberrypi.torque import TorqueRaspberryPi


class RaspberryPiService(SlaveService):

    # def on_connect(self):
    #     pass

    # def on_disconnect(self):
    #     # code that runs when the connection has already closed
    #     # (to finalize the service, if needed)
    #     pass



    def exposed_init_with_client(
            self,
            FLUIDDYN_PATH_EXP_client,
            name_exp=None,
            path_exp_client=None,
            open_client=None
    ):
        FLUIDDYN_PATH_EXP_client = os.path.normpath(FLUIDDYN_PATH_EXP_client)

        if path_exp_client is not None:
            path_exp_client = os.path.normpath(path_exp_client)

            if path_exp_client.startswith(FLUIDDYN_PATH_EXP_client):
                path_relative = path_exp_client[
                    len(FLUIDDYN_PATH_EXP_client)+1:]
                path_relative = path_relative.replace('\\', '/')
                path_exp = os.path.join(FLUIDDYN_PATH_EXP, path_relative)
            else:  # a little bit strange, but why not...
                path_exp = os.path.join(FLUIDDYN_PATH_EXP, path_exp_client)
        else:
            path_exp = None

        self.torque = TorqueRaspberryPi(
            path_exp=path_exp, name_exp=name_exp,
            path_exp_client=path_exp_client,
            open_client=open_client
        )

        self.exposed_torque = self.torque

        self.open_client = open_client



    def exposed_measure(self, duration, sample_rate, SAVE=True):
        if not hasattr(self, 'torque'):
            raise ValueError(
"""ServiceRaspberryPi should be firt initialized with its function
init_with_client.""")
        return self.torque.measure(duration, sample_rate, SAVE)


    # def exposed_transfer_from_raspberrypi(self, files=None):
    #     pass
    # def exposed_rsync_files_from_raspberrypi(self):
    #     pass





    def exposed_open(self, filename, mode="r"):
        return open(filename, mode)






    # def save_in_client(self, path_file):
    #     print('path_file', path_file)

    #     name_file = ''
    #     path_local = self.torque

    #     with open(path_local):
    #         with self.remote_open(path_file, 'w') as f:
    #             pass




if __name__ == "__main__":
    server = ThreadedServer(RaspberryPiService, port=18861)
    server.start()
