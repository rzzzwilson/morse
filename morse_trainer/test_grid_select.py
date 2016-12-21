#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test the 'grid_display' custom widget used by Morse Trainer.
"""

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
                             QVBoxLayout, QPushButton)
from grid_select import GridSelect
import utils


class GridSelectExample(QWidget):
    """Application to demonstrate the Morse Trainer 'display' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.display_alphabet = GridSelect(utils.Alphabetics)
        self.display_numbers = GridSelect(utils.Numbers)
        self.display_punctuation = GridSelect(utils.Punctuation)
        invert_button = QPushButton('Invert Selections', self)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.display_alphabet)
        hbox1.addWidget(self.display_numbers)
        hbox1.addWidget(self.display_punctuation)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(invert_button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        invert_button.clicked.connect(self.invertButtonClicked)

        self.display_alphabet.changed.connect(self.changeAlphabetHandler)
        self.display_numbers.changed.connect(self.changeNumbersHandler)
        self.display_punctuation.changed.connect(self.changePunctuationHandler)

        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('Example of GridSelect widget')
        self.show()

    def invertButtonClicked(self):
        """Get alphabet (and others) selection, invert, put back."""

        for gd in (self.display_alphabet,
                   self.display_numbers, self.display_punctuation):
            selection = gd.getState()
            inverted = {key:(not value) for (key, value) in selection.items()}
            gd.setState(inverted)

    def changeAlphabetHandler(self, status):
        print('Alphabet has changed: %s' % str(status))

    def changeNumbersHandler(self, status):
        print('Numbers has changed: %s' % str(status))

    def changePunctuationHandler(self, status):
        print('Punctuation has changed: %s' % str(status))


app = QApplication(sys.argv)
ex = GridSelectExample()
sys.exit(app.exec())
