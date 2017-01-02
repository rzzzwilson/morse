#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 custom widget used by Morse Trainer.

Used to select character speed and show overall word speed.

speed = Speeds()

speed.setSpeed(wpm)     # sets the overall speed display
cwpm = speed.getState() # get the char wpm value set by the user

The widget generates a signal '.changed' when some value changes.
"""

import platform
from random import randint

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QSpinBox, QGroupBox, QLineEdit
from PyQt5.QtCore import pyqtSignal

import utils


class Speeds(QWidget):

    # signal raised when user changes cwpm
    changed = pyqtSignal(int)

    # maximum and minimum speeds
    MinSpeed = 5
    MaxSpeed = 40

    def __init__(self, char_speed=MinSpeed):
        QWidget.__init__(self)
        self.initUI(char_speed)
        self.setWindowTitle('Test Speeds widget')
        self.setFixedHeight(80)
        self.show()

        # define state variables
        self.char_speed = char_speed

    def initUI(self, char_speed):
        # define the widgets we are going to use
        lbl_words = QLabel('  Overall')
        self.led_words = QLineEdit(self)
        self.led_words.text = ''
        self.led_words.setReadOnly(True)

        lbl_chars = QLabel('Characters')
        self.spb_chars = QSpinBox(self)
        self.spb_chars.setMinimum(Speeds.MinSpeed)
        self.spb_chars.setMaximum(Speeds.MaxSpeed)
        self.spb_chars.setValue(char_speed)
        self.spb_chars.setSuffix(' wpm')

        # start the layout
        layout = QVBoxLayout()

        groupbox = QGroupBox("Speeds")
        groupbox.setStyleSheet(utils.StyleCSS)
        layout.addWidget(groupbox)

        hbox = QHBoxLayout()
        hbox.addWidget(lbl_chars)
        hbox.addWidget(self.spb_chars)
        hbox.addWidget(lbl_words)
        hbox.addWidget(self.led_words)
        hbox.addStretch()

        groupbox.setLayout(hbox)

        self.setLayout(layout)

        # connect spinbox events to handlers
        self.spb_chars.valueChanged.connect(self.handle_charspeed_change)

    def handle_charspeed_change(self, char_speed):
        """Character speed changed."""

        self.char_speed = char_speed
        self.changed.emit(self.char_speed)

    def setSpeed(self, wpm):
        """Set the overall wpm speed.

        wpm   the overall words per minute (integer)
        """

        self.word_speed = wpm
        new_display = '%d wpm' % wpm
        self.led_words.setText(new_display)
        self.update()

    def getState(self):
        """Return the character speed."""

        return self.char_speed
