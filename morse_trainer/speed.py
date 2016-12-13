#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 custom widget used by Morse Trainer.

Used to select character and word speeds.

speed = SpeedGroup()

speeds = speed.getSpeeds()

The widget generates a signal '.changed' when some value changes.
The owning code must interrogate the widget for the values.
"""

import platform
from random import randint

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QSpinBox, QGroupBox
from PyQt5.QtCore import pyqtSignal


class SpeedGroup(QWidget):

    # signal raised when any value changes
    changed = pyqtSignal()

    # maximum and minimum speeds
    MinSpeed = 5
    MaxSpeed = 40

    def __init__(self, word_speed=MinSpeed, char_speed=MinSpeed):
        QWidget.__init__(self)
        self.initUI(word_speed, char_speed)
        self.setWindowTitle('Test Speed Group widget')
        self.show()

    def initUI(self, word_speed, char_speed):
        # define the widgets we are going to use
        lbl_words = QLabel('Words')
        self.spb_words = QSpinBox(self)
        self.spb_words.setMinimum(SpeedGroup.MinSpeed)
        self.spb_words.setMaximum(SpeedGroup.MaxSpeed)
        self.spb_words.setValue(word_speed)
        self.spb_words.setSuffix(' wpm')

        lbl_chars = QLabel('Characters')
        self.spb_chars = QSpinBox(self)
        self.spb_chars.setMinimum(SpeedGroup.MinSpeed)
        self.spb_chars.setMaximum(SpeedGroup.MaxSpeed)
        self.spb_chars.setValue(char_speed)
        self.spb_chars.setSuffix(' wpm')

        # connect spinbox events to handlers
        self.spb_words.valueChanged.connect(self.handle_wordspeed_change)
        self.spb_chars.valueChanged.connect(self.handle_charspeed_change)

        # start the layout
        vbox = QVBoxLayout()

        groupbox = QGroupBox("Speeds")
        vbox.addWidget(groupbox)

        hbox = QHBoxLayout()

        hbox.addWidget(lbl_words)
        hbox.addWidget(self.spb_words)
        hbox.addWidget(lbl_chars)
        hbox.addWidget(self.spb_chars)
        hbox.addStretch()

        groupbox.setLayout(hbox)
        vbox.addWidget(groupbox)
        vbox.addStretch()

        self.setLayout(vbox)

    def handle_wordspeed_change(self, value):
        """Word speed changed.

        Ensure the character speed is not less and send a signal.
        """

        char_speed = self.spb_chars.value()

        if char_speed < value:
            self.spb_chars.setValue(value)

        self.changed.emit()

    def handle_charspeed_change(self, value):
        """Character speed changed.  Send a signal."""

        self.changed.emit()

    def getSpeeds(self):
        """Return the speeds as a tuple: (word_speed, char_speed)."""

        return (self.spb_words.value(), self.spb_chars.value())
