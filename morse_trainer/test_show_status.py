#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test the 'show status' widget.
"""

import sys
from random import randint
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout)
from show_status import ShowStatus


class ShowStatusExample(QWidget):
    """Application to demonstrate the Morse Trainer 'display' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.alphabet_status = ShowStatus('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.numbers_status = ShowStatus('0123456789')
        self.punctuation_status = ShowStatus("""?/,.():;!'"=""")
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
        self.setWindowTitle('Example of ShowStatus widget')
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
            gd.refresh(new)


app = QApplication(sys.argv)
ex = ShowStatusExample()
sys.exit(app.exec())
