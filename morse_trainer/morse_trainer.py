#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The 'morse trainer' program.

Usage: morse_trainer.py [-d <number>] [-h]

Where -d <number>  sets the debug level
      -h           prints this help AND THEN STOPS
"""

import sys
import getopt
import traceback

import logger
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt5.QtWidgets import QPushButton, QToolTip, QLabel
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


# name and version number of the trainer
ProgName = 'Morse Trainer'
ProgVersion = '0.1'

# the log file
LogFile = 'morse_trainer.log'

# width and height of top-level widget
WidgetWidth = 600
WidgetHeight = 400


class MainWindow(QWidget):

    def __init__(self, debug):
        super().__init__()
        self.initUI(debug)
        self.dirty = True

    def initUI(self, debug):
        QToolTip.setFont(QFont('SansSerif', 10))
        qbtn = QPushButton('Quit', self)
        qbtn.setToolTip('This is a <b>QPushButton</b> widget')
        qbtn.clicked.connect(QCoreApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 50)
        self.setGeometry(300, 300, WidgetWidth, WidgetHeight)
        self.setWindowTitle('%s %s' % (ProgName, ProgVersion))
        self.show()

    def closeEvent(self, event):
        if self.dirty:
            self.save()

    def save(self):
        log.info('saving...')


# to help the befuddled user
def usage(msg=None):
    if msg:
        print(('*'*80 + '\n%s\n' + '*'*80) % msg)
    print(__doc__)

# our own handler for uncaught exceptions
def excepthook(type, value, tb):
    msg = '\n' + '=' * 80
    msg += '\nUncaught exception:\n'
    msg += ''.join(traceback.format_exception(type, value, tb))
    msg += '=' * 80 + '\n'
    print(msg)
    tkinter_error(msg)

# plug our handler into the python system
sys.excepthook = excepthook

# parse the program params
argv = sys.argv[1:]

try:
    (opts, args) = getopt.getopt(argv, 'd:h', ['debug=', 'help'])
except getopt.GetoptError as err:
    usage(err)
    sys.exit(1)

debug = 0              # assume no logging

for (opt, param) in opts:
    if opt in ['-d', '--debug']:
        try:
            debug = int(param)
        except ValueError:
            usage("-d must be followed by an integer, got '%s'" % param)
            sys.exit(1)
    elif opt in ['-h', '--help']:
        usage()
        sys.exit(0)

# start the logging
log = logger.Log(LogFile, debug)

app = QApplication(args)
ex = MainWindow(debug)
log.debug('Starting application')
sys.exit(app.exec_())
