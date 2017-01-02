#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test the 'charset' custom widget used by Morse Trainer.
"""

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
                             QVBoxLayout, QPushButton)
from charset import Charset


class TestCharset(QWidget):
    """Application to demonstrate the Morse Trainer 'charset' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        user_charset = {'A':True, '0':True}
        self.display = Charset(koch_selected=False, koch_num=2,
                               user_charset=user_charset)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.display)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        self.setLayout(vbox)

        self.display.changed.connect(self.changeCharsetHandler)

        self.setGeometry(100, 100, 500, 100)
        self.setWindowTitle('Example of Charset widget')
        self.show()

    def changeCharsetHandler(self, status):
        """The widget has changed.
        
        status  a dict {'A':True, 'B':False, ...} which is the new status
        """

        print('Charset has changed, status=\n%s' % str(status))

app = QApplication(sys.argv)
ex = TestCharset()
sys.exit(app.exec())
