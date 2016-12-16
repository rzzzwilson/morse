#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test code for 'instructions' widget used by Morse Trainer.
"""

import sys
from instructions import Instructions
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
                             QVBoxLayout, QPushButton)


class TestInstructions(QWidget):
    """Application to demonstrate the Morse Trainer 'grouping' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        instructions = ('Lorem ipsum dolor sit amet, consectetur adipiscing '
                        'elit, sed do eiusmod tempor incididunt ut labore et '
                        'dolore magna aliqua. Ut enim ad minim veniam, quis '
                        'nostrud exercitation ullamco laboris nisi ut aliquip '
                        'ex ea commodo consequat. Duis aute irure dolor in '
                        'reprehenderit in voluptate velit esse cillum dolore '
                        'eu fugiat nulla pariatur. Excepteur sint occaecat '
                        'cupidatat non proident, sunt in culpa qui officia '
                        'deserunt mollit anim id est laborum.')
        self.instructions = Instructions(instructions)

        vbox = QVBoxLayout()
        vbox.addWidget(self.instructions)

        self.setLayout(vbox)

        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('Example of Instructions widget')
        self.show()


app = QApplication(sys.argv)
ex = TestInstructions()
sys.exit(app.exec())
