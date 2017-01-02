#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test the 'speeds' widget.
"""

import sys
from speeds import Speeds
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout

class SpeedsExample(QWidget):
    """Application to demonstrate the Morse Trainer 'display' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.speed_group = Speeds()

        hbox = QHBoxLayout()
        hbox.addWidget(self.speed_group)
        self.setLayout(hbox)

        self.setWindowTitle('Example of Speeds widget')
        self.setFixedSize(400, 125)
        self.show()

        # connect the widget to '.changed' event handler
        self.speed_group.changed.connect(self.speed_changed)

    def speed_changed(self, char_speed):
        print('Changed speeds, cwpm=%d' % char_speed)
        print('Change overall speed to %d' % char_speed)
        self.speed_group.setState(char_speed)


app = QApplication(sys.argv)
ex = SpeedsExample()
sys.exit(app.exec())
