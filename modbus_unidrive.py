import time
from fluidlab.instruments.modbus.unidrive_sp import Unidrive_sp

motor = Unidrive_sp("/dev/tty.usbserial", timeout=1)

motor.enable_rotation()
motor.start_rotation(1)

time.sleep(4)

motor.stop_rotation()
motor.disable_rotation()
