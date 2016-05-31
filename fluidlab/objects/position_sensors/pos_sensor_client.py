
import rpyc
import socket


class PositionSensorServerError(Exception):
    pass


class PositionSensorClient(object):

    def __init__(self):
        try:
            self._conn = rpyc.connect('localhost', 18861)
        except socket.error:
            raise PositionSensorServerError(
                'No position sensor server seems to be running.')
        self._root = self._conn.root

    def get_absolute_position(self):
        return float(self._root.exposed_get_absolute_position())

    def get_relative_position(self):
        return float(self._root.exposed_get_relative_position())

    def reset_counter_to_zero(self):
        return self._root.exposed_reset_counter_to_zero()

    def set_absolute_origin(self, value=0.):
        return self._root.exposed_set_absolute_origin(value=value)

    def set_relative_origin(self, value=0.):
        return self._root.exposed_set_relative_origin(value=value)

if __name__ == "__main__":
    sensor = PositionSensorClient()
