#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 application to help a user learn to send and receive Morse code.

You need a morse key and Code Practice Oscillator (CPO).
"""

import sys
import platform
import queue

from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QPushButton, QMessageBox
import receive_morse as RM
import display


# set platform-dependent sizes
if platform.system() == 'Windows':
    pass
elif platform.system() == 'Linux':
    pass
elif platform.system() == 'Darwin':
    pass
else:
    raise Exception('Unrecognized platform: %s' % platform.system())


class MorseTrainer(QWidget):
    """Application to demonstrate the Morse Trainer 'display' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()
        self.receive_q = queue.Queue()
        print('End of __init__()')
        sys.stdout.flush()

        self.receiver = RM.Receive(self.receive_q)
        self.receiver.start()

    def initUI(self):
        self.display = display.Display()
        left_button = QPushButton('Left ⬅', self)
        right_button = QPushButton('Right ➡', self)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.display)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(left_button)
        hbox2.addWidget(right_button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        left_button.clicked.connect(self.leftButtonClicked)
        right_button.clicked.connect(self.rightButtonClicked)

        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('Example of Display widget')
        self.show()

        # populate the display widget a bit
        for index in range(40):
            if index in (7, 21):
                self.display.insert_upper('U', fg=display.Display.AnsTextBadColour)
            else:
                self.display.insert_upper('U', fg=display.Display.AskTextColour)

        for index in range(39):
            if index in (5, 19):
                self.display.insert_lower('L', fg=display.Display.AnsTextBadColour)
            else:
                self.display.insert_lower('L', fg=display.Display.AnsTextGoodColour)
        self.display.set_highlight(40)
        self.display.set_tooltip(0, "Expected 'A', got 'N'\nweqweqwe")
        self.display.set_tooltip(5, 'Tooltip at index 5')
        self.display.set_tooltip(19, "Expected 'A', got 'N'\nweqweqwe\nasdasdadasd\na\na\na\na\na")

    def leftButtonClicked(self):
        """Move highlight to the left, if possible."""

        index = self.display.get_highlight()
        if index is not None:
            index -= 1
            if index >= 0:
                self.display.set_highlight(index)

    def rightButtonClicked(self):
        """Clear display, reenter new test text.."""

        self.display.clear()

        for index in range(25):
            if index in (7, 21):
                self.display.insert_upper('1', fg=display.Display.AnsTextBadColour)
            else:
                self.display.insert_upper('1', fg=display.Display.AskTextColour)

        self.display.insert_upper(' ', fg=display.Display.AskTextColour)

        for index in range(25):
            if index in (5, 19):
                self.display.insert_lower('8', fg=display.Display.AnsTextBadColour)
            else:
                self.display.insert_lower('8', fg=display.Display.AnsTextGoodColour)
        self.display.set_highlight(10)
        self.display.set_tooltip(0, 'Tooltip at index 0')
        self.display.set_tooltip(5, 'Tooltip at index 5')
        self.display.set_tooltip(19, 'Tooltip at index 19')




app = QApplication(sys.argv)
ex = MorseTrainer()
sys.exit(app.exec_())
