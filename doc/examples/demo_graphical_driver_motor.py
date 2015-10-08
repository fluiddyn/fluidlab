"""Example of a tiny generic graphical driver.
==============================================

.. autoclass:: GraphicalDriver
   :members:
   :private-members:

"""


import sys
from PySide import QtGui

from serial import SerialException


from fluidlab.instruments.modbus.unidrive_sp import (
    UnidriveSP, example_linear_ramps)


class FalseMotor(object):
    def __init__(self):
        self.rr = 0.

    def unlock(self):
        pass

    def lock(self):
        pass

    def set_target_rotation_rate(self, rr, check=False):
        self.rr = rr

    def get_target_rotation_rate(self):
        return self.rr

    def start_rotation(self, a):
        pass

    def stop_rotation(self):
        pass


class GraphicalDriver(QtGui.QWidget):
    def __init__(self, class_motor=UnidriveSP):
        super(GraphicalDriver, self).__init__()

        # initialization of the motor driver
        try:
            self.motor = class_motor()
        except (OSError, SerialException):
            self.motor = FalseMotor()

        # initialization of the window
        self.initUI()

    def create_btn(self, name, function, x, y):
        button = QtGui.QPushButton(name, self)
        self.grid.addWidget(button, x, y)
        button.clicked.connect(function)
        return button

    def initUI(self):
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(20)

        # create few basic buttons
        self.create_btn('Unlock', self.motor.unlock, 0, 0)
        self.create_btn('Lock', self.motor.lock, 0, 1)
        self.create_btn('Start', self.motor.start_rotation, 1, 0)
        self.create_btn('Stop', self.motor.stop_rotation, 1, 1)
        self.create_btn('Triangle', self.triangle_dialog, 2, 1)

        # create a layout for the speed with one button and one "lcd"
        speed_layout = QtGui.QVBoxLayout()
        speed_layout.setSpacing(5)

        set_speed_btn = QtGui.QPushButton('Set speed', self)
        set_speed_btn.clicked.connect(self.show_set_speed_dialog)
        self.set_speed_btn = set_speed_btn

        self.lcd = QtGui.QLCDNumber(self)
        self.lcd.display(self.motor.get_target_rotation_rate())

        speed_layout.addWidget(set_speed_btn)
        speed_layout.addWidget(self.lcd)

        self.grid.addLayout(speed_layout, 2, 0)

        # global setting
        self.setLayout(self.grid)
        self.move(400, 300)
        self.setWindowTitle('Leroy Somer driver')
        self.show()

    def show_set_speed_dialog(self):
        speed, ok = QtGui.QInputDialog.getText(
            self, 'Input Dialog',
            'Enter the motor speed in Hz:')
        if ok:
            self.motor.set_target_rotation_rate(float(speed))
            self.lcd.display(self.motor.get_target_rotation_rate())

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
            example_linear_ramps(self.motor, max_speed, duration, steps)


def main():
    app = QtGui.QApplication(sys.argv)
    ex = GraphicalDriver()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
