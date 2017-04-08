#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
The 'instructions' widget for Morse Trainer.

Used to show a QLabel containing instructions.  Read only.

instructions = Instructions()
"""

from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox, QLabel,
                             QTextEdit, QHBoxLayout, QVBoxLayout, QGroupBox)

class Instructions(QWidget):
    def __init__(self, text):
        """Create instructions containing 'text'."""

        QWidget.__init__(self)
        self.initUI(text)
        self.show()

    def initUI(self, text):
        # define the widgets in this group
        doc = QTextEdit(self)
        doc.setReadOnly(True)
        doc.insertPlainText(text)

        # start the layout
        layout = QVBoxLayout()
        layout.addWidget(doc)

        self.setLayout(layout)
