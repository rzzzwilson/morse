#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test code for 'grouping' widget used by Morse Trainer.
"""

import sys
from groups import Groups
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
                             QVBoxLayout, QPushButton)


class TestGroups(QWidget):
    """Application to demonstrate the Morse Trainer 'grouping' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.grouping = Groups()

        vbox = QVBoxLayout()
        vbox.addWidget(self.grouping)

        self.setLayout(vbox)

        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('Example of Groups widget')
        self.show()

        self.grouping.changed.connect(self.change_grouping)

    def change_grouping(self, index):
        """Handler for event when 'Groups' object changes."""

        print('change_grouping: index=%s' % str(index))


app = QApplication(sys.argv)
ex = TestGroups()
sys.exit(app.exec())
