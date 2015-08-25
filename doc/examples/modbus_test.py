import unittest
from fluidlab.instruments.modbus.unidrive_sp import Unidrive_sp
leroy = Unidrive_sp('/dev/tty.usbserial', 'rtu', 1, 'minimalmodbus')

acc = 5
leroy.acceleration_time.set(acc)
resulting_acc = leroy.acceleration_time.get()
print(acc)
print(resulting_acc)
