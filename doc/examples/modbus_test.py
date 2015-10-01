import time
from fluidlab.instruments.modbus.unidrive_sp import Unidrive_sp
leroy = Unidrive_sp('/dev/tty.usbserial', 'rtu', 1, 'minimalmodbus')

leroy.enable_rotation()
leroy.start_rotation(1)
time.sleep(4)
leroy.stop_rotation()
leroy.disable_rotation()
