#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 application to help a user learn to send and receive Morse code.

You need a morse key and Code Practice Oscillator (CPO).
"""

import sys
import platform
import queue

from PyQt5.QtCore import pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QPushButton, QMessageBox
import morse
import display


# set platform-dependent stuff, if any
# we had to do this with wxpython, maybe pyqt is better?
if platform.system() == 'Windows':
    pass
elif platform.system() == 'Linux':
    pass
elif platform.system() == 'Darwin':
    pass
else:
    raise Exception('Unrecognized platform: %s' % platform.system())


class Communicate(QObject):
    """Signal/slot communication class."""

    morseChar = pyqtSignal('QString')       # received morse chars


class MorseReader(QThread):
    """A class for a morse reader that runs in another thread.

    Recognized characters are sent to the main thread by a signal.
    """

    def __init__(self, sig_obj, params_file=None):
        """Initialize the reader.

        sig_obj      the signal object to emit() characters back to master
        params_file  parameters file
        """

        super().__init__()

        self.sig_obj = sig_obj
        print('self.sig_obj=%s' % type(self.sig_obj))
        self.params_file = params_file
        self.running = False

        self.morse = morse.ReadMorse()
        if self.params_file:
            self.morse.load_params(self.params_file)

    def __del__(self):
        # close morse reader
        self.running = False
        self.wait()
        if self.params_file:
            self.morse.save_params(self.params_file)

    def run(self):
        self.running = True
        print('run() looping')
        while self.running:
            char = self.morse.read_morse()
            print('Sending: %s' % char)
            self.sig_obj.morseChar.emit(char)


class MorseTrainer(QWidget):
    """Application to demonstrate the Morse Trainer 'display' widget."""

    def __init__(self, params_file):
        super().__init__()
        self.params_file = params_file
        self.initUI()

        # create signal/slot for recognized morse characters
        self.got_morse_char = Communicate()
        self.got_morse_char.morseChar.connect(self.morseChar)

        self.read_thread = MorseReader(self.got_morse_char, params_file)
        self.read_thread.start()

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
        for index in range(30):
            if index in (7, 21):
                self.display.insert_upper('U', fg=display.Display.AnsTextBadColour)
            else:
                self.display.insert_upper('U', fg=display.Display.AskTextColour)

        for index in range(29):
            if index in (5, 19):
                self.display.insert_lower('L', fg=display.Display.AnsTextBadColour)
            else:
                self.display.insert_lower('L', fg=display.Display.AnsTextGoodColour)
        self.display.set_highlight()
        self.display.set_tooltip(0, "Expected 'A', got 'N'\nweqweqwe")
        self.display.set_tooltip(5, 'Tooltip at index 5, rwtrwtrewtrwtrewtrewtrewtrewtrewtrewtrewtrewtrewtrewtrewtrewtrew')
        self.display.set_tooltip(19, "Expected 'A', got 'N'\nweqweqwe\nasdasdadasd\na\na\na\na\na")

    def morseChar(self, char):
        """The morse reader thread found a character."""

        self.display.insert_lower(char)
        self.display.insert_upper('.')
        self.display.set_highlight()
        self.display.update()

    def leftButtonClicked(self):
        """Move highlight to the left, if possible."""

        index = self.display.get_highlight()
        if index is not None:
            index -= 1
            if index >= 0:
                self.display.set_highlight(index)

    def rightButtonClicked(self):
        """Simulate getting a morse char."""

        self.got_morse_char.morseChar.emit('A')



# get program name from sys.argv
prog_name = sys.argv[0]
if prog_name.endswith('.py'):
    prog_name = prog_name[:-3]

# path to file holding morse recognition parameters
params_file = '%s.param' % prog_name

app = QApplication(sys.argv)
ex = MorseTrainer(params_file)
sys.exit(app.exec_())
