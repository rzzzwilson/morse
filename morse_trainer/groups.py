#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
The 'grouping' widget for Morse Trainer.

grouping = Groups()

group = grouping.get_grouping()
Return None or a value in [2..8] inclusive.

Raises the '.changed' signal when changed.
"""

from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox, QLabel,
                             QHBoxLayout, QVBoxLayout, QGroupBox)

class Groups(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.initUI()
        self.setFixedHeight(80)
        self.show()

    def initUI(self):
        # define the widgets in this group
        combo = QComboBox(self)
        combo.addItem('No grouping')
        combo.addItem('3 characters')
        combo.addItem('4 characters')
        combo.addItem('5 characters')
        combo.addItem('6 characters')
        combo.addItem('7 characters')
        combo.addItem('8 characters')
        label = QLabel('Groups:')

        layout = QVBoxLayout()

        groupbox = QGroupBox("Groups")
        layout.addWidget(groupbox)

        hbox = QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(combo)
        hbox.addStretch()

        groupbox.setLayout(hbox)

        self.setLayout(layout)
