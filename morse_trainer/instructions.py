#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
The 'instructions' widget for Morse Trainer.

Used to show a QLabel containing instructions.

instructions = Instructions()
"""

from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox, QLabel,
                             QHBoxLayout, QVBoxLayout, QGroupBox)

class Instructions(QWidget):
    def __init__(self, text):
        """Create instructions containing 'text'."""

        QWidget.__init__(self)
        self.initUI(text)
        self.show()

    def initUI(self, text):
        # define the widgets in this group
        doc = QLabel(text)
        doc.setWordWrap(True);

        layout = QVBoxLayout()

        groupbox = QGroupBox("Instructions")
        layout.addWidget(groupbox)

        hbox = QHBoxLayout()
        hbox.addWidget(doc)
        hbox.addStretch()

        groupbox.setLayout(hbox)

        self.setLayout(layout)
