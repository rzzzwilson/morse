#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
The 'receive group' widget.
"""

from PyQt5.QtWidgets import *

class ReceiveGroup(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle('ReceiveGroup Test')
        self.initUI()

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

        hbox = QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(combo)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)

        self.setLayout(vbox)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    screen = ReceiveGroup()
    screen.show()
    sys.exit(app.exec())
