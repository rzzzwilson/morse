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

import utils


class Groups(QWidget):

    # signal raised when any value changes
    changed = pyqtSignal(int)


    # order of options and associated value
    Selects = [(0, 'No grouping'),
               (3, '3 characters'),
               (4, '4 characters'),
               (5, '5 characters'),
               (6, '6 characters'),
               (7, '7 characters'),
               (8, '8 characters')]

    # dict to convert index in control to group number
    Index2Group = {i:g for (i, (g, _)) in enumerate(Selects)}

    # dict to convert group number to control index
    Group2Index = {g:i for (i, (g, _)) in enumerate(Selects)}

    # dictionary to decode the select string into a group number
    DecodeSelects = {s:v for (v, s) in Selects}


    def __init__(self):
        QWidget.__init__(self)
        self.initUI()
        self.setFixedHeight(80)
        self.show()

        # internal state variables
        self.group = None

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
        groupbox.setStyleSheet(utils.StyleCSS)
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
        self.group = Groups.Index2Group[index]
        self.changed.emit(self.group)

    def setState(self, group):
        """Set the selected grouping.
        
        group  a group number in (0, 3, 4, 5, 6, 7, 8)
        """

        self.group = group
        index = Groups.Group2Index[group]
        self.combo.setCurrentIndex(index)
        self.combo.update()

    def getState(self):
        """Return the grouping selected.
        
        Returns either:
            0  no grouping
            3  groups of three
            4  ...etc
        """

        return self.group
