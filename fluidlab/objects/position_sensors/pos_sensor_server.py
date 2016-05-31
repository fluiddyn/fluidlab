#! /usr/bin/env python
import rpyc
from pos_sensor import PositionSensor


class PositionSensorService(rpyc.Service):
    cls_sensor = PositionSensor

    def exposed_get_absolute_position(self):
        return self.sensor.get_absolute_position()

    def exposed_get_relative_position(self):
        return self.sensor.get_relative_position()

    def exposed_reset_counter_to_zero(self):
        return self.sensor.reset_counter_to_zero()

    def exposed_set_relative_origin(self, value=0.):
        return self.sensor.set_relative_origin(value=value)

    def exposed_set_absolute_origin(self, value=0.):
        return self.sensor.set_absolute_origin(value=value)

if __name__ == "__main__":

    PositionSensorService.sensor = PositionSensorService.cls_sensor()

    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(PositionSensorService, port=18861)

    t.start()
