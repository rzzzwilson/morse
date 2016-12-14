#!/usr/bin/env python3

from PyQt5.QtWidgets import *
import sys

class GroupBox(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("GroupBox")

        # create all widgets
        radiobutton1 = QRadioButton("RadioButton 1")
        radiobutton1.setChecked(True)
        radiobutton2 = QRadioButton("RadioButton 2")

        # start layout
        layout = QGridLayout()

        groupbox = QGroupBox("GroupBox Example")
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)

        vbox = QVBoxLayout()
        groupbox.setLayout(vbox)

        vbox.addWidget(radiobutton1)
        vbox.addWidget(radiobutton2)

        self.setLayout(layout)

app = QApplication(sys.argv)
screen = GroupBox()
screen.show()
sys.exit(app.exec())
