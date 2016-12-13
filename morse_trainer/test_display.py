#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test code for 'display' widget used by Morse Trainer.
"""

import sys
from display import Display
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
                             QVBoxLayout, QPushButton)


class DisplayExample(QWidget):
    """Application to demonstrate the Morse Trainer 'display' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.display = Display()
        left_button = QPushButton('Left ⬅', self)
        right_button = QPushButton('Right ➡', self)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.display)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(left_button)
        hbox2.addWidget(right_button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        left_button.clicked.connect(self.leftButtonClicked)
        right_button.clicked.connect(self.rightButtonClicked)

        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('Example of Display widget')
        self.show()

        # populate the display widget a bit
        for index in range(40):
            if index in (7, 21):
                self.display.insert_upper('U', fg=Display.AnsTextBadColour)
            else:
                self.display.insert_upper('U', fg=Display.AskTextColour)

        for index in range(39):
            if index in (5, 19):
                self.display.insert_lower('L', fg=Display.AnsTextBadColour)
            else:
                self.display.insert_lower('L', fg=Display.AnsTextGoodColour)

        self.display.set_highlight(39)

        # rely on index being tooltip ID
        self.display.set_tooltip(0, "Expected 'A', got 'N'\nweqweqwe")
        self.display.set_tooltip(5, 'Tooltip at index 5, '
                                     'rewyerewrewtrewtrewtrewtrewrtewi'
                                     'trewrewtrewtrewtrewtrewtrew')
        self.display.set_tooltip(19, "Expected 'A', got 'N'\n"
                                     "weqweqwe\nasdasdadasd\na\na\na\na\na")

    def leftButtonClicked(self):
        """Move highlight to the left, if possible."""

        index = self.display.get_highlight()
        if index is not None:
            index -= 1
            if index >= 0:
                self.display.set_highlight(index)

    def rightButtonClicked(self):
        """Clear display, reenter new test text.."""

        self.display.clear()

        for index in range(25):
            if index in (7, 21):
                self.display.insert_upper('1', fg=Display.AnsTextBadColour)
            else:
                self.display.insert_upper('1', fg=Display.AskTextColour)

        self.display.insert_upper(' ', fg=Display.AskTextColour)

        for index in range(24):
            if index in (5, 19):
                self.display.insert_lower('8', fg=Display.AnsTextBadColour)
            else:
                self.display.insert_lower('8', fg=Display.AnsTextGoodColour)

        self.display.set_highlight(10)

        # rely on index being tooltip ID
        self.display.set_tooltip(0, 'Tooltip at index 0')
        self.display.set_tooltip(5, 'Tooltip at index 5')
        self.display.set_tooltip(19, 'Tooltip at index 19')


app = QApplication(sys.argv)
ex = DisplayExample()
sys.exit(app.exec())
