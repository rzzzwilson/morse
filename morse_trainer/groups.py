#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
The 'grouping' widget for Morse Trainer.

grouping = Groups()

group = grouping.get_grouping()
Return None or a value in [2..8] inclusive.

Raises the '.change' signal when changed.
"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox, QLabel,
                             QHBoxLayout, QVBoxLayout, QGroupBox)

class Groups(QWidget):

    # signal raised when any value changes
    change = pyqtSignal(int)

    # order of options and associated value
    Selects = [(0, 'No grouping'),
               (3, '3 characters'),
               (4, '4 characters'),
               (5, '5 characters'),
               (6, '6 characters'),
               (7, '7 characters'),
               (8, '8 characters')]

    DecodeIndex = {i:g for (i, (g, _)) in enumerate(Selects)}

    # dictionary to decode the select string into a group number
    DecodeSelects = {s:v for (v, s) in Selects}


    def __init__(self):
        QWidget.__init__(self)
        self.initUI()
        self.setFixedHeight(80)
        self.show()

        # internal state variables
        self.grouping = None

        # link change events to handler
        self.combo.currentIndexChanged.connect(self.group_change)

    def initUI(self):
        # define the widgets in this group
        self.combo = QComboBox(self)
        for (_, select) in Groups.Selects:
            self.combo.addItem(select)
        label = QLabel('Groups:')

        layout = QVBoxLayout()

        groupbox = QGroupBox("Groups")
        layout.addWidget(groupbox)

        hbox = QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.combo)
        hbox.addStretch()

        groupbox.setLayout(hbox)

        self.setLayout(layout)

    def group_change(self):
        """Selection changed in combo box, change internal state."""

        index = self.combo.currentIndex()
        self.grouping = Groups.DecodeIndex[index]
        self.change.emit(self.grouping)

    def getGrouping(self):
        """Return the grouping selected."""

        return self.grouping
