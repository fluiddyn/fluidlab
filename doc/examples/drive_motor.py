
from time import sleep

from fluidlab.exp import Timer
from fluidlab.instruments.modbus.unidrive_sp import UnidriveSP

motor = UnidriveSP()

# set a timer which ticks every 5 s
timer = Timer(time_between_ticks=5)

print('Enter in a loop for 3 ticks.')
for i in range(3):
    print('  Enter in the block of the loop. i = {}.'.format(i))
    print('  Start rotation with a frequency of 2 Hz.')
    motor.start_rotation(2)

    print('  Sleep 2 s.')
    sleep(2)

    print('  Change target rotation rate to 1 Hz.')
    motor.set_target_rotation_rate(1)

    print('  Sleep 2 s.')
    sleep(2)

    print('  Stop the motor.')
    motor.stop_rotation()

    print('  Wait for the tick.')
    timer.wait_tick()
