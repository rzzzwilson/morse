#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test of grouping - make the receive boxgroup.
"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QRadioButton
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox


class GroupBox(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle('Test of Receive group control')

        layout = QGridLayout()
        self.setLayout(layout)

        groupbox = QGroupBox("Receive")
#        groupbox.setCheckable(True)
        layout.addWidget(groupbox)

        vbox = QVBoxLayout()
        groupbox.setLayout(vbox)

        radiobutton = QRadioButton("Characters")
        radiobutton.setChecked(True)
        vbox.addWidget(radiobutton)
        radiobutton = QRadioButton("Groups")
        vbox.addWidget(radiobutton)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    screen = GroupBox()
    screen.show()
sys.exit(app.exec())
