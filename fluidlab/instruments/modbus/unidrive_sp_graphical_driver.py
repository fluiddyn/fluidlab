"""Example of a tiny graphical driver.
======================================

.. autoclass:: GraphicalDriver
   :members:
   :private-members:

"""


import sys
from PySide import QtGui
import time


class GraphicalDriver(QtGui.QWidget):
    def __init__(self):
        super(GraphicalDriver, self).__init__()
        self.init_motor()
        self.initUI()

    def initUI(self):
        grid = QtGui.QGridLayout()
        self.grid = grid
        self.create_btn('Unlock', self.unlock_motor, 0, 0)
        self.create_btn('Lock', self.lock_motor, 0, 1)
        self.create_btn('Start', self.start_motor, 1, 0)
        self.create_btn('Stop', self.stop_motor, 1, 1)
        self.create_btn('Triangle', self.triangle_dialog, 2, 1)

        set_speed_btn = QtGui.QPushButton('Set speed', self)
        set_speed_btn.clicked.connect(self.show_dialog)
        self.set_speed_btn = set_speed_btn

        self.lcd = QtGui.QLCDNumber(self)
        try:
            self.lcd.display(self.leroy.speed.get()/4)
        except AttributeError:
            pass
        self.speed_layout = QtGui.QVBoxLayout()
        self.speed_layout.setSpacing(0)
        self.speed_layout.addWidget(set_speed_btn)
        self.speed_layout.addWidget(self.lcd)
        self.grid.addLayout(self.speed_layout, 2, 0)
        self.setLayout(grid)
        self.move(300, 150)
        self.setWindowTitle('Leroy Somer driver')
        self.show()

    def init_motor(self):
        from fluidlab.instruments.modbus.unidrive_sp import Unidrive_sp
        try:
            self.leroy = Unidrive_sp(
                '/dev/ttyUSB0',
                # '/dev/tty.usbserial',
                'rtu', 1,
                'minimalmodbus')
        except OSError:
            print('Motor not found')

    def create_btn(self, name, function, x, y):
        button = QtGui.QPushButton(name, self)
        self.grid.addWidget(button, x, y)
        button.clicked.connect(function)

    def show_dialog(self):
        speed, ok = QtGui.QInputDialog.getText(
            self, 'Input Dialog',
            'Enter the motor speed in Hz:')
        if ok:
            self.set_motor_speed(speed)
            self.lcd.display(self.leroy.speed.get()/4)

    def triangle_dialog(self):
        max_speed, ok_a = QtGui.QInputDialog.getText(
            self, 'Input Dialog 1',
            'Enter the maximum motor speed in Hz:')
        duration, ok_b = QtGui.QInputDialog.getText(
            self, 'Input Dialog 2',
            'Enter the duration in s:')
        steps, ok_c = QtGui.QInputDialog.getText(
            self, 'Input Dialog 3',
            'Enter the number of steps:')
        if ok_a and ok_b and ok_c:
            self.triangle(max_speed, duration, steps)

    def lock_motor(self):
        self.leroy.disable_rotation()

    def unlock_motor(self):
        self.leroy.enable_rotation()

    def start_motor(self):
        self.leroy.start_rotation()

    def stop_motor(self):
        self.leroy.stop_rotation()

    def set_motor_speed(self, speed, check=True):
        self.leroy.speed.set(4*float(speed), check)

    def triangle(self, max_speed=3., duration=5., steps=30):
        max_speed = float(max_speed)
        duration = float(duration)
        steps = int(steps)
        speed = 0.
        t = 0.
        start_speed = self.leroy.speed.get()
        self.leroy.enable_rotation()
        self.leroy.start_rotation(0)
        while t < duration/2:
            time.sleep(duration/steps)
            speed += 2*max_speed/steps
            t += duration/steps
            self.leroy.speed.set(4*speed, check=False)
        while t < duration:
            time.sleep(duration/steps)
            speed -= 2*max_speed/steps
            t += duration/steps
            if speed<0:
                speed=0.0
            self.leroy.speed.set(4*speed, check=False)
        self.leroy.speed.set(start_speed, check=False)
        self.leroy.stop_rotation()
        self.leroy.disable_rotation()


def main():
    app = QtGui.QApplication(sys.argv)
    ex = GraphicalDriver()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
