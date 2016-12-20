#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 custom widget used by Morse Trainer.

Status shows the error rate for a GridDisplay data set.

show_status = Status(data)

where 'data' is the string used to establish a GridDisplay.

show_status.refresh(dict)

where 'dict' is a dictionary: {'A':10, 'B':26, ...} that maps the
character to a 'success' percentage.
"""

import platform
from random import randint

from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QFont


class Status(QWidget):
    """Widget to display a set of bars displaying success percentages."""

    # set platform-dependent sizes
    if platform.system() == 'Linux':
        Font = 'Courier'            # the font to use
        FontSize = 12               # font size
        TopMargin = 5               # top margin to bar
        LeftMargin = 5              # left margin to bar
        RightMargin = 5             # right margin to bar
        BottomMargin = 14           # bottom margin to bar
        LabelBottomMargin = 3       # bottom margin to text
        LabelLeftMargin = 7         # left margin to text
        InterBarMargin = 3          # margin between bars
        BarWidth = 11               # width of bar in pixels
        BarHeight = 100             # height of bar in pixels
    elif platform.system() == 'Darwin':
        Font = 'Courier'
        FontSize = 12
        TopMargin = 5
        LeftMargin = 5
        RightMargin = 5
        BottomMargin = 14
        LabelBottomMargin = 3
        LabelLeftMargin = 7
        InterBarMargin = 3
        BarWidth = 11
        BarHeight = 100
    elif platform.system() == 'Windows':
        Font = 'Courier'
        FontSize = 12
        TopMargin = 5
        LeftMargin = 5
        RightMargin = 5
        BottomMargin = 14
        LabelBottomMargin = 3
        LabelLeftMargin = 7
        InterBarMargin = 3
        BarWidth = 11
        BarHeight = 100
    else:
        raise Exception('Unrecognized platform: %s' % platform.system())

    # proficiency at which Koch system adds another character
    KochThreshold = 0.9


    def __init__(self, data, threshold=KochThreshold):
        """Initialize the widget.

        data       a string of characters to be displayed in the widget
        threshold  the fraction at which the Koch system adds a character

        The widget figures out how many bars there are from 'data'.
        """

        super().__init__()

        # declare state variables here so we know what they all are
        self.data = data            # the characters to display (in order)
        self.fraction = None        # list of fractions matching self.data
        self.threshold = threshold  # where we draw the threshold line
        self.font = None            # the font used
        self.font_size = None       # size of font
        self.widget_width = None    # set in initUI()
        self.widget_height = None   # set in initUI()

        # set up the UI
        self.initUI()

    def initUI(self):
        """Set up the UI."""

        # calculate the number of display bars we will have
        num_chars = len(self.data)

        # figure out the widget size
        widget_width = (Status.LeftMargin + num_chars*Status.BarWidth
                        + (num_chars-1)*Status.InterBarMargin
                        + Status.RightMargin)
        widget_height = (Status.TopMargin + Status.BarHeight
                         + Status.BottomMargin)

        self.setFixedWidth(widget_width)
        self.setFixedHeight(widget_height)
        self.setMinimumSize(widget_width, widget_height)

        self.widget_width = widget_width
        self.widget_height = widget_height

        # set the widget internal state
        self.font = QFont(Status.Font, Status.FontSize)
        self.font_size = Status.FontSize

    def paintEvent(self, e):
        """Prepare to draw the widget."""

        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        """Draw the widget from internal state."""

        # set to the font we use in the widget
        qp.setFont(self.font)

        # draw the threshold line
        threshold_height = int(Status.BarHeight * self.threshold)
        line_y = Status.TopMargin + Status.BarHeight - threshold_height
        qp.setPen(Qt.red)
        qp.drawLine(0, line_y, self.widget_width, line_y)

        # draw outline of each bar
        qp.setPen(Qt.gray)
        x = Status.LeftMargin
        y = Status.TopMargin
        for _ in self.data:
            qp.drawRect(x, y, Status.BarWidth, Status.BarHeight)
            x += Status.BarWidth + Status.InterBarMargin

        # draw the percentage bar
        if self.fraction:
            x = Status.LeftMargin
            y = Status.TopMargin
            qp.setBrush(Qt.blue)
            for (char, percent) in zip(self.data, self.fraction):
                pct_height = int(Status.BarHeight * percent)
                if pct_height == 0:     # force *some* display if 0
                    pct_height = 1
                top_height = Status.BarHeight - pct_height
                qp.drawRect(x, y+top_height, Status.BarWidth, pct_height)
                x += Status.BarWidth + Status.InterBarMargin

        # draw column 'footer' header
        x = Status.LabelLeftMargin
        y = self.widget_height - Status.LabelBottomMargin
        qp.setPen(Qt.black)
        for char in self.data:
            qp.drawText(x, y, char)
            x += Status.BarWidth + Status.InterBarMargin

    def setState(self, data):
        """Update self.fraction with values matching 'data'.

        data  a dict of {char: percent} values
        """

        self.fraction = []
        for char in self.data:
            try:
                value = data[char]
            except KeyError:
                value = 0
            self.fraction.append(value)

        self.update()
