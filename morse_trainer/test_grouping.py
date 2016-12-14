#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test code for 'grouping' widget used by Morse Trainer.
"""

import sys
from grouping import Grouping
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
                             QVBoxLayout, QPushButton)


class TestGrouping(QWidget):
    """Application to demonstrate the Morse Trainer 'grouping' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.grouping = Grouping()

        vbox = QVBoxLayout()
        vbox.addWidget(self.grouping)

        self.setLayout(vbox)

        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('Example of Grouping widget')
        self.show()


app = QApplication(sys.argv)
ex = TestGrouping()
sys.exit(app.exec())
