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
import logger
log = logger.Log('debug.log', logger.Log.DEBUG)


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

    morse_char = pyqtSignal('QString')       # received morse char


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
        self.params_file = params_file
        self.running = False

        self.morse = morse.ReadMorse()
        if self.params_file:
            log('Loading params from %s' % self.params_file)
            self.morse.load_params(self.params_file)

#    def __del__(self):
#        log('__del__')
#        # save updated params
#        if self.params_file:
#            log('Saving params to %s' % self.params_file)
#            self.morse.save_params(self.params_file)
#        # close morse reader
#        self.running = False
#        self.wait()

    def close(self):
        if self.params_file:
            log('Saving params to %s' % self.params_file)
            self.morse.save_params(self.params_file)
        log('Stopping thread')
        self.running = False
        self.wait(500)
        log('After .wait(500)')

    def run(self):
        self.running = True
        while self.running:
            char = self.morse.read_morse()
            log('found: %s' % char)
            if len(char) == 1:
                self.sig_obj.morse_char.emit(char)


class MorseTrainer(QWidget):
    """Application to demonstrate the Morse Trainer 'display' widget."""

    def __init__(self, params_file):
        super().__init__()
        self.params_file = params_file
        self.initUI()

        # create signal/slot for recognized morse characters
        self.got_morse_char = Communicate()
        self.got_morse_char.morse_char.connect(self.gotMorseChar)

        self.read_thread = MorseReader(self.got_morse_char, params_file)
        self.read_thread.start()

        # populate the display widget a bit
        self.display.insert_upper('U', fg=display.Display.AskTextColour)

    def initUI(self):
        self.display = display.Display()

        hbox = QHBoxLayout()
        hbox.addWidget(self.display)

        self.setLayout(hbox)

        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('Example of Display widget')
        self.show()

    def gotMorseChar(self, char):
        """The morse reader thread found a character."""

        self.display.insert_upper('U')
        self.display.insert_lower(char, fg=display.Display.AnsTextBadColour)
        self.display.set_highlight()
        self.display.update()

    def closeEvent(self, event):
        log('Closing read_thread')
        self.read_thread.close()


# get program name from sys.argv
prog_name = sys.argv[0]
if prog_name.endswith('.py'):
    prog_name = prog_name[:-3]

# path to file holding morse recognition parameters
params_file = '%s.param' % prog_name

app = QApplication(sys.argv)
ex = MorseTrainer(params_file)
sys.exit(app.exec())
