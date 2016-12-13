#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

In this example, we position two push
buttons in the bottom-right corner
of the window.

author: Jan Bodnar
website: zetcode.com
last edited: January 2015
"""

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout)


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        topButton = QPushButton('Top')
        okButton = QPushButton('OK')
        cancelButton = QPushButton('Cancel')

        hbox = QHBoxLayout()
        hbox.addStretch(2)
        hbox.addWidget(okButton)
        hbox.addStretch(1)
        hbox.addWidget(cancelButton)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(topButton)
        hbox2.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox2)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Buttons')
        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec())
