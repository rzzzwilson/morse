#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test the 'show proficiency' widget.
"""

import sys
from random import randint
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout)
from proficiency import Proficiency
import utils


class ProficiencyExample(QWidget):
    """Application to demonstrate the Morse Trainer 'display' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.alphabet_status = Proficiency(utils.Alphabetics)
        self.numbers_status = Proficiency(utils.Numbers)
        self.punctuation_status = Proficiency(utils.Punctuation)
        redisplay_button = QPushButton('Redisplay', self)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.alphabet_status)
        hbox1.addWidget(self.numbers_status)
        hbox1.addWidget(self.punctuation_status)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(redisplay_button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        redisplay_button.clicked.connect(self.redisplayButtonClicked)

        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('Example of Proficiency widget')
        self.show()

    def redisplayButtonClicked(self):
        """Regenerate some data (random) and display it."""

        for gd in (self.alphabet_status,
                   self.numbers_status, self.punctuation_status):
            # generate random data
            new = {}
            for char in gd.data:
                new[char] = randint(0,100)/100
            # set first character to 0
            new[gd.data[0]] = 0
            # redisplay
            gd.setState(new)


app = QApplication(sys.argv)
ex = ProficiencyExample()
sys.exit(app.exec())
