#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A class that reads morse from the microphone.

Will be used in its own thread by Morse Trainer.
"""

import platform

import receive_morse
from display import Display
from speeds import Speeds
from groups import Groups
from charset import Charset
from charset_proficiency import CharsetProficiency
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


ProgramMajor = 0
ProgramMinor = 1
ProgramVersion = '%d.%d' % (ProgramMajor, ProgramMinor)

# set defaults
DefaultWordsPerMinute = 10
DefaultCharWordsPerMinute = 10

StateSaveFile = ''

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

        # define internal state variables
        self.clear_data()

    def clear_data(self):
        """Define and clear all internal variables."""

        # clear the send/receive statistics
        # each dictionary contains tuples of (<num_chars>, <num_ok>)
        self.send_stats = {}
        self.receive_stats = {}
        for char in utils.Alphabetics:
            self.send_stats[char] = (0, 0)
            self.receive_stats[char] = (0, 0)
        for char in utils.Numbers:
            self.send_stats[char] = (0, 0)
            self.receive_stats[char] = (0, 0)
        for char in utils.Punctuation:
            self.send_stats[char] = (0, 0)
            self.receive_stats[char] = (0, 0)

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
        self.setGeometry(100, 100, 815, 545)
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
                    'characters with shorter bars.\n\n'
                    'Pressing the "Clear" button will clear the statistics.')
        instructions = Instructions(doc_text)
        self.send_status = CharsetProficiency('Send Proficiency', utils.Alphabetics,
                                         utils.Numbers, utils.Punctuation)
        self.receive_status = CharsetProficiency('Receive Proficiency',
                                            utils.Alphabetics, utils.Numbers,
                                            utils.Punctuation)
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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = MorseTrainer()
    ex.show()
    sys.exit(app.exec())
