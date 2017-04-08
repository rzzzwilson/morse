#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test the 'charset status' widget.
"""

import sys
from random import randint
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout)
from charset_proficiency import CharsetProficiency
import utils


class TestCharsetProficiency(QWidget):
    """Application to demonstrate the Morse Trainer 'charset status' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.status = CharsetProficiency('Test Status', utils.Alphabetics,
                                                        utils.Numbers,
                                                        utils.Punctuation)
        redisplay_button = QPushButton('Redisplay', self)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.status)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(redisplay_button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        redisplay_button.clicked.connect(self.redisplayButtonClicked)

        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('Example of CharsetProficiency widget')
        self.show()

    def redisplayButtonClicked(self):
        """Regenerate some data (random) and display it."""

        # generate random data
        new = {}
        for char in self.status.data:
            if char in 'A0?':
                # first in each set is 0.0
                new[char] = 0.0
            else:
                new[char] = randint(0,100)/100
        self.status.setState(new)


app = QApplication(sys.argv)
ex = TestCharsetProficiency()
sys.exit(app.exec())
