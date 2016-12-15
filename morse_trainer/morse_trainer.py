#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 application to help a user learn to send and receive Morse code.

You need a morse key and Code Practice Oscillator (CPO).
"""

import platform
import queue

from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget
from PyQt5.QtWidgets import QFormLayout, QLineEdit, QRadioButton, QLabel, QCheckBox
from PyQt5.QtWidgets import QPushButton, QMessageBox, QSpacerItem

import receive_morse
from display import Display
from speed import Speed
from groups import Groups
from charset import Charset

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


ProgramMajor = 0
ProgramMinor = 1
ProgramVersion = '%d.%d' % (ProgramMajor, ProgramMinor)


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

        self.receive_morse = receive_morse.ReadMorse()
        if self.params_file:
            log('Loading params from %s' % self.params_file)
            self.receive_morse.load_params(self.params_file)

    def __del__(self):
        log('__del__')
        # save updated params
        if self.params_file:
            log('Saving params to %s' % self.params_file)
            self.receive_morse.save_params(self.params_file)
        # close morse reader
        self.running = False
        self.wait()

    def close(self):
        if self.params_file:
            log('Saving params to %s' % self.params_file)
            self.receive_morse.save_params(self.params_file)
        log('Stopping thread')
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            char = self.receive_morse.read_morse()
            log('found: %s' % char)
            if len(char) == 1:
                self.sig_obj.morse_char.emit(char)

class MorseTrainer(QTabWidget):
    def __init__(self, parent = None):
        super(MorseTrainer, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.send_tab = QWidget()
        self.receive_tab = QWidget()
        self.stats_tab = QWidget()

        self.addTab(self.send_tab, 'Send')
        self.addTab(self.receive_tab, 'Receive')
        self.addTab(self.stats_tab, 'Status')
        self.initSendTab()
        self.initReceiveTab()
        self.InitStatsTab()
        self.setWindowTitle('Morse Trainer %s' % ProgramVersion)

    def initSendTab(self):
        # define widgets on this tab
        self.send_display = Display()
        self.btn_send_start_stop = QPushButton('Start')
        self.btn_send_clear = QPushButton('Clear')

        # start layout
        buttons = QVBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.btn_send_start_stop)
        buttons.addItem(QSpacerItem(20, 20))
        buttons.addWidget(self.btn_send_clear)

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addLayout(buttons)

        layout = QVBoxLayout()
        layout.addWidget(self.send_display)
        layout.addLayout(hbox)
        self.send_tab.setLayout(layout)

    def initReceiveTab(self):
        # define widgets on this tab
        self.receive_display = Display()
        self.receive_speed = Speed()
        self.receive_grouping = Groups()
        self.receive_charset = Charset()
        self.btn_receive_start_stop = QPushButton('Start')
        self.btn_receive_clear = QPushButton('Clear')

        # start layout
        buttons = QVBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.btn_receive_start_stop)
        buttons.addItem(QSpacerItem(20, 20))
        buttons.addWidget(self.btn_receive_clear)

        controls = QVBoxLayout()
        controls.addWidget(self.receive_speed)
        controls.addWidget(self.receive_grouping)
        controls.addWidget(self.receive_charset)
        controls.addStretch()

        hbox = QHBoxLayout()
        hbox.addLayout(controls)
        hbox.addLayout(buttons)

        layout = QVBoxLayout()
        layout.addWidget(self.receive_display)
        layout.addLayout(hbox)
        self.receive_tab.setLayout(layout)

    def InitStatsTab(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel('subjects'))
        layout.addWidget(QCheckBox('Physics'))
        layout.addWidget(QCheckBox('Maths'))
        self.setTabText(2, 'Status')
        self.stats_tab.setLayout(layout)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = MorseTrainer()
    ex.show()
    sys.exit(app.exec())
