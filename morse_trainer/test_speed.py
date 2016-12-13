#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test the 'speed' widget.
"""

import sys
from speed import SpeedGroup
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout

class SpeedGroupExample(QWidget):
    """Application to demonstrate the Morse Trainer 'display' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.speed_group = SpeedGroup()

        hbox = QHBoxLayout()
        hbox.addWidget(self.speed_group)
        self.setLayout(hbox)

        self.setWindowTitle('Example of SpeedGroup widget')
        self.show()

        # connect the widget to '.changed' event handler
        self.speed_group.changed.connect(self.speed_changed)

    def speed_changed(self):
        print('changed speeds, wwpm=%d, cwpm=%d' % self.speed_group.getSpeeds())


app = QApplication(sys.argv)
ex = SpeedGroupExample()
sys.exit(app.exec())
