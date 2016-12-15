#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 custom widget used by Morse Trainer.

Used to select character and word speeds.

speed = Speeds()

speeds = speed.getSpeeds()

The widget generates a signal '.changed' when some value changes.
The owning code must interrogate the widget for the values.
"""

import platform
from random import randint

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QSpinBox, QGroupBox
from PyQt5.QtCore import pyqtSignal


class Speeds(QWidget):

    # signal raised when any value changes
    changed = pyqtSignal()

    # maximum and minimum speeds
    MinSpeed = 5
    MaxSpeed = 40

    def __init__(self, word_speed=MinSpeed, char_speed=MinSpeed):
        QWidget.__init__(self)
        self.initUI(word_speed, char_speed)
        self.setWindowTitle('Test Speeds widget')
        self.setFixedHeight(80)
        self.show()

    def initUI(self, word_speed, char_speed):
        # define the widgets we are going to use
        lbl_words = QLabel('  Overall')
        self.spb_words = QSpinBox(self)
        self.spb_words.setMinimum(Speeds.MinSpeed)
        self.spb_words.setMaximum(Speeds.MaxSpeed)
        self.spb_words.setValue(word_speed)
        self.spb_words.setSuffix(' wpm')

        lbl_chars = QLabel('Characters')
        self.spb_chars = QSpinBox(self)
        self.spb_chars.setMinimum(Speeds.MinSpeed)
        self.spb_chars.setMaximum(Speeds.MaxSpeed)
        self.spb_chars.setValue(char_speed)
        self.spb_chars.setSuffix(' wpm')

        # connect spinbox events to handlers
        self.spb_words.valueChanged.connect(self.handle_wordspeed_change)
        self.spb_chars.valueChanged.connect(self.handle_charspeed_change)

        # start the layout
        layout = QVBoxLayout()

        groupbox = QGroupBox("Speeds")
        layout.addWidget(groupbox)

        hbox = QHBoxLayout()
        hbox.addWidget(lbl_chars)
        hbox.addWidget(self.spb_chars)
        hbox.addWidget(lbl_words)
        hbox.addWidget(self.spb_words)
        hbox.addStretch()

        groupbox.setLayout(hbox)

        self.setLayout(layout)

    def handle_wordspeed_change(self, value):
        """Word speed changed.

        Ensure the character speed is not less and send a signal.
        """

        char_speed = self.spb_chars.value()

        if char_speed < value:
            self.spb_chars.setValue(value)

        self.changed.emit()

    def handle_charspeed_change(self, value):
        """Character speed changed.

        Ensure the character speed is not less and send a signal.
        """

        word_speed = self.spb_words.value()

        if value < word_speed:
            self.spb_words.setValue(value)

        self.changed.emit()

    def getSpeeds(self):
        """Return the speeds as a tuple: (word_speed, char_speed)."""

        return (self.spb_words.value(), self.spb_chars.value())
