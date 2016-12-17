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


# get program name and version
ProgName = sys.argv[0]
if ProgName.endswith('.py'):
        ProgName = ProgName[:-3]

ProgramMajor = 0
ProgramMinor = 1
ProgramVersion = '%d.%d' % (ProgramMajor, ProgramMinor)
log('Morse Trainer %s started' % ProgramVersion)

class MorseTrainer(QTabWidget):

    # set platform-dependent sizes
    if platform.system() == 'Windows':
        MinimumWidth = 815
        MinimumHeight = 675
    elif platform.system() == 'Linux':
        MinimumWidth = 815
        MinimumHeight = 675
    elif platform.system() == 'Darwin':
        MinimumWidth = 815
        MinimumHeight = 675
    else:
        raise Exception('Unrecognized platform: %s' % platform.system())

    # set default speeds
    DefaultWordsPerMinute = 10
    DefaultCharWordsPerMinute = 10

    # constants for the three tabs
    SendTab = 0
    ReceiveTab = 1
    StatisticsTab = 2

    # name for the state save file
    StateSaveFile = '%s.state' % ProgName

    # define names of the state variables to be saved/restored
    StateVarNames = ['send_stats', 'receive_stats',
                     'Koch_send_set', 'Koch_receive_set',
                     'User_receive_set',
                     'receive_wpm', 'receive_cwpm', 'send_wpm',
                     'receive_grouping']


    def __init__(self, parent = None):
        super(MorseTrainer, self).__init__(parent)

        # define internal state variables
        self.clear_data()

        # get state from the save file, if any
        self.load_state(MorseTrainer.StateSaveFile)

        # define the UI
        self.initUI()

        # update visible controls with state values
        self.update_UI()

        # connect events to slots
        self.currentChanged.connect(self.tab_change)    # QTabWidget tab changed
        self.receive_groups.change.connect(self.receive_group_change)

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

        self.setMinimumSize(MorseTrainer.MinimumWidth, MorseTrainer.MinimumHeight)
        self.setMaximumHeight(MorseTrainer.MinimumHeight)
        self.setWindowTitle('Morse Trainer %s' % ProgramVersion)

    def initSendTab(self):
        # define widgets on this tab
        self.send_display = Display()
        doc_text = ('Here we test your sending accuracy.  The program will '
                    'print the character you should send in the top row of the '
                    'display at the top of this tab.  Your job is to send that '
                    'character using your key and code practice oscillator.  '
                    'The program will print what it thinks you sent on the '
                    'lower line of the display.')
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
                    'the bottom row of the display at the top of this tab, '
                    'along with the character the program actually sent in '
                    'the top row.')
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

        # tie events raised here to handlers
        self.receive_speeds.changed.connect(self.receive_speeds_changed)

    def InitStatsTab(self):
        doc_text = ('This shows your sending and receiving accuracy. '
                    'Each bar shows your accuracy for a character.  The '
                    'taller the bar the better.  You need to practice the '
                    'characters with shorter bars.\n\n'
                    'The red line shows the Koch threshold.  In Koch mode '
                    'if all characters in the test set are over the threshold '
                    'the algorithm will add another character to the set you '
                    'are tested with.\n\n'
                    'Pressing the "Clear" button will clear the statistics.')
        instructions = Instructions(doc_text)
        self.send_status = CharsetStatus('Send Accuracy', utils.Alphabetics,
                                         utils.Numbers, utils.Punctuation)
        percents = self.stats2percent(self.send_stats)
        self.send_status.refresh(percents)
        self.receive_status = CharsetStatus('Receive Accuracy',
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
#        btn_clear.clicked.connect(self.xyzzy)

    def update_UI(self):
        """Update controls that show state values."""

        # the receive speeds
        self.receive_speeds.setSpeeds(self.receive_wpm, self.receive_cwpm)

        # the receive test sets (Koch and user-selected)
        self.receive_charset.setValues(self.Using_Koch, self.Koch_number, self.User_receive_set)

    def receive_speeds_changed(self, wpm, cwpm):
        """Something in the "receive speed" group changed."""

        self.receive_wpm = wpm
        self.receive_cwpm = cwpm

    def receive_group_change(self, grouping):
        """Receive grouping changed."""

        self.receive_grouping = grouping

    def closeEvent(self, *args, **kwargs):
        """Program close - save the internal state."""

        super().closeEvent(*args, **kwargs)
        self.save_state(MorseTrainer.StateSaveFile)

    def clear_data(self):
        """Define and clear all internal variables."""

        # clear the send/receive statistics
        # each dictionary contains tuples of (<num_chars>, <num_ok>)
        self.send_stats = {}
        self.receive_stats = {}
        for char in utils.Alphabetics + utils.Numbers + utils.Punctuation:
            self.send_stats[char] = (0, 0)
            self.receive_stats[char] = (0, 0)

        # the character sets we test on and associated variables
        self.Using_Koch = True
        self.Koch_number = 2
        self.Koch_send_set = []
        self.Koch_receive_set = utils.Koch[:self.Koch_number]
        self.User_receive_set = []

        # send and receive speeds
        self.send_wpm = None        # not used yet
        self.receive_wpm = 5
        self.receive_cwpm = 5

        # the receive grouping
        self.receive_grouping = 0

        # set the "previous tab" value
        self.previous_tab = MorseTrainer.SendTab

    def load_state(self, filename):
        """Load saved state from the given file."""

        # read JSON from file, if we can
        if filename is None:
            return

        try:
            with open(filename, 'r') as fd:
                data = json.load(fd)
        except FileNotFoundError:
            return

        # get data from the restore dictionary, if possible
        for var_name in MorseTrainer.StateVarNames:
            try:
                value = data[var_name]
            except KeyError:
                pass
            else:
                setattr(self, var_name, value)

        # now update UI state from state variables

    def save_state(self, filename):
        """Save saved state to the given file."""

        # write data to the save file, if any
        if filename is None:
            return

        # create a dictionary filled with save data
        save_data = {}
        for var_name in MorseTrainer.StateVarNames:
            save_data[var_name] = getattr(self, var_name)

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

    def update_stats(self, stats_dict, char, ok):
        """Update the stats for a single character.

        stats_dict  a reference to the stats dictionary to update
        char        the character that was tested
        ok          True if test was good, else False
        """

        (num_tests, num_ok) = stats_dict[char]
        num_tests += 1
        if ok:
            num_ok += 1
        stats_dict[char] = (num_tests, num_ok)

    def tab_change(self, tab_index):
        """Handler when a tab is changed.

        tab_index  index of the new tab
        """

        # if we left the "send" tab, turn off action, if any
        if self.previous_tab == MorseTrainer.SendTab:
            log('tab_change: turning off send action')

        # if we left the "receive" tab, turn off action, if any
        if self.previous_tab == MorseTrainer.ReceiveTab:
            log('tab_change: turning off receive action')

        # if we changed to the "statistics" tab, refresh the stats widget
        if tab_index == MorseTrainer.StatisticsTab:
            percents = self.stats2percent(self.send_stats)
            self.send_status.refresh(percents)

            percents = self.stats2percent(self.receive_stats)
            self.receive_status.refresh(percents)

        # remember the previous tab for NEXT TIME WE CHANGE
        self.previous_tab = tab_index


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = MorseTrainer()
    ex.show()
    sys.exit(app.exec())
