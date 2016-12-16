#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 application to help a user learn to send and receive Morse code.

You need a morse key and Code Practice Oscillator (CPO).
"""

import sys
import json
import platform

from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget
from PyQt5.QtWidgets import QFormLayout, QLineEdit, QRadioButton, QLabel, QCheckBox
from PyQt5.QtWidgets import QPushButton, QMessageBox, QSpacerItem

import receive_morse
from display import Display
from speeds import Speeds
from groups import Groups
from charset import Charset
from charset_status import CharsetStatus
from instructions import Instructions
import utils

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


# set defaults
DefaultWordsPerMinute = 10
DefaultCharWordsPerMinute = 10

ProgName = sys.argv[0]
if ProgName.endswith('.py'):
        ProgName = ProgName[:-3]

ProgramMajor = 0
ProgramMinor = 1
ProgramVersion = '%d.%d' % (ProgramMajor, ProgramMinor)

StateSaveFile = '%s.state' % ProgName


class MorseTrainer(QTabWidget):
    def __init__(self, parent = None):
        super(MorseTrainer, self).__init__(parent)

        # define internal state variables
        self.clear_data()

        # get state from the save file, if any
        self.load_state(StateSaveFile)

        # define the UI
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
        self.setFixedSize(815, 675)
        self.setWindowTitle('Morse Trainer %s' % ProgramVersion)

    def initSendTab(self):
        # define widgets on this tab
        self.send_display = Display()
        doc_text = ('Here we test your sending accuracy.  The program '
                    'will print the character you should send in the '
                    'top row of the display above.  Your job is to send '
                    'that character using your key and code practice '
                    'oscillator.  The program will print what it thinks '
                    'you sent on the lower line of the display.')
        instructions = Instructions(doc_text)
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
        layout.addWidget(instructions)
        layout.addLayout(hbox)
        self.send_tab.setLayout(layout)

    def initReceiveTab(self):
        # define widgets on this tab
        self.receive_display = Display()
        doc_text = ('Here we test your receiving accuracy.  The program '
                    'will sound a random morse character which you should type '
                    'on the keyboard.  The character you typed will appear in '
                    'the bottom row of the display above, along with the '
                    'character the program actually sent in the top row.')
        instructions = Instructions(doc_text)
        self.receive_speeds = Speeds()
        self.receive_groups = Groups()
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
        controls.addWidget(self.receive_speeds)
        controls.addWidget(self.receive_groups)
        controls.addWidget(self.receive_charset)

        hbox = QHBoxLayout()
        hbox.addLayout(controls)
        buttons.addItem(QSpacerItem(10, 1))
        hbox.addLayout(buttons)

        layout = QVBoxLayout()
        layout.addWidget(self.receive_display)
        layout.addWidget(instructions)
        layout.addLayout(hbox)
        self.receive_tab.setLayout(layout)

    def InitStatsTab(self):
        doc_text = ('This shows your sending and receiving accuracy. '
                    'Each bar shows your profiency for a character.  The '
                    'taller the bar the better.  You need to practice the '
                    'characters with shorter bars. The red line shows the Koch '
                    'threshold.\n\n'
                    'Pressing the "Clear" button will clear the statistics.')
        instructions = Instructions(doc_text)
        self.send_status = CharsetStatus('Send Proficiency', utils.Alphabetics,
                                         utils.Numbers, utils.Punctuation)
        percents = self.stats2percent(self.send_stats)
        self.send_status.refresh(percents)
        self.receive_status = CharsetStatus('Receive Proficiency',
                                            utils.Alphabetics, utils.Numbers,
                                            utils.Punctuation)
        percents = self.stats2percent(self.receive_stats)
        self.receive_status.refresh(percents)
        btn_clear = QPushButton('Clear')

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(btn_clear)

        layout = QVBoxLayout()

        layout.addWidget(instructions)
        layout.addWidget(self.send_status)
        layout.addWidget(self.receive_status)
        layout.addLayout(hbox)

        self.stats_tab.setLayout(layout)

        # connect the 'Clear' button to debug code
        btn_clear.clicked.connect(self.xyzzy)

    def xyzzy(self):
        """Make fake data and update the stats."""

        from random import randint

        self.send_stats = {}
        for char in self.send_status.data:
            self.send_stats[char] = (100, randint(50,100))
        percents = self.stats2percent(self.send_stats)
        self.send_status.refresh(percents)

        self.receive_stats = {}
        for char in self.receive_status.data:
            self.receive_stats[char] = (100, randint(50,100))
        percents = self.stats2percent(self.receive_stats)
        self.receive_status.refresh(percents)

    def closeEvent(self, *args, **kwargs):
        """Program close - save the internal state."""

        super().closeEvent(*args, **kwargs)
        self.save_state(StateSaveFile)

    def clear_data(self):
        """Define and clear all internal variables."""

        # clear the send/receive statistics
        # each dictionary contains tuples of (<num_chars>, <num_ok>)
        self.send_stats = {}
        self.receive_stats = {}
        for char in utils.Alphabetics + utils.Numbers + utils.Punctuation:
            self.send_stats[char] = (0, 0)
            self.receive_stats[char] = (0, 0)

    def load_state(self, filename):
        """Load saved state from the given file."""

        if filename is None:
            return

        try:
            with open(filename, 'r') as fd:
                data = json.load(fd)
        except FileNotFoundError:
            return

        try:
            (self.send_stats, self.receive_stats) = data
        except KeyError:
            raise Exception('Invalid data in JSON file %s' % filename)

    def save_state(self, filename):
        """Save saved state to the given file."""

        if filename is None:
            return

        save_data = [self.send_stats, self.receive_stats]
        json_str = json.dumps(save_data, sort_keys=True, indent=4)

        with open(filename, 'w') as fd:
            fd.write(json_str + '\n')

    def stats2percent(self, stats):
        """Convert stats data into a fraction dictionary.

        The 'stats' data has the form {'A':(100,50), ...} where
        the tuple contains (<num tested>, <num OK>).

        The resultant fraction dictionary has the form:
            {'A': 0.50, ...}
        """

        results = {}
        for (char, (num_tested, num_ok)) in stats.items():
            if num_tested == 0:
                fraction = 0.0
            else:
                fraction = num_ok / num_tested
            results[char] = fraction

        return results

    def currentChanged(self, tab_index):
        """Handler when a tab is changed.

        tab_index  index of the new tab
        """

        percents = self.stats2percent(self.send_stats)
        self.send_status.refresh(percents)

        percents = self.stats2percent(self.receive_stats)
        self.receive_status.refresh(percents)



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = MorseTrainer()
    ex.show()
    sys.exit(app.exec())
