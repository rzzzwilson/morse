#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 custom widget used by Morse Trainer.

ShowStatus shows the error rate for a GridDisplay data set.

show_status = ShowStatus(data)

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


class ShowStatus(QWidget):
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


    def __init__(self, data):
        """Initialize the widget.

        data  a string of characters to be displayed in the widget

        The widget figures out how many bars there are from 'data'.
        """

        super().__init__()

        # declare state variables here so we know what they all are
        self.data = data            # the characters to display
        self.font = None            # the font used
        self.font_size = None       # size of font
        self.widget_width = None    # set in initUI()
        self.widget_height = None   # set in initUI()
        self.percent = None         # list of percentages matching self.data

        # set up the UI
        self.initUI()

    def initUI(self):
        """Set up the UI."""

        # automatically fill widget with system colours on redraw
        self.setAutoFillBackground(True)

        # calculate the number of display bars we will have
        num_chars = len(self.data)

        # figure out the widget size
        widget_width = (ShowStatus.LeftMargin + num_chars*ShowStatus.BarWidth
                        + (num_chars-1)*ShowStatus.InterBarMargin + ShowStatus.RightMargin)
        widget_height = (ShowStatus.TopMargin + ShowStatus.BarHeight + ShowStatus.BottomMargin)

        self.setFixedWidth(widget_width)
        self.setFixedHeight(widget_height)
        self.setMinimumSize(widget_width, widget_height)

        self.widget_width = widget_width
        self.widget_height = widget_height

        # set the widget internal state
        self.font = QFont(ShowStatus.Font, ShowStatus.FontSize)
        self.font_size = ShowStatus.FontSize

        # draw the bars, with surround border

        # draw data char headers (well, really 'bottomers' here)

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

#        qp.setPen(Qt.black)
#        qp.drawRect(0, 0, self.widget_width, self.widget_height)

        # draw outline of each bar
        qp.setPen(Qt.gray)
        x = ShowStatus.LeftMargin
        y = ShowStatus.TopMargin
        for _ in self.data:
            qp.drawRect(x, y, ShowStatus.BarWidth, ShowStatus.BarHeight)
            x += ShowStatus.BarWidth + ShowStatus.InterBarMargin

        # draw the percentage bar
        if self.percent:
            x = ShowStatus.LeftMargin
            y = ShowStatus.TopMargin
            qp.setBrush(Qt.blue)
            for (char, percent) in zip(self.data, self.percent):
                pct_height = int(ShowStatus.BarHeight * percent)
                if pct_height == 0:     # force *some* display if 0
                    pct_height = 1
                top_height = ShowStatus.BarHeight - pct_height
                qp.drawRect(x, y+top_height, ShowStatus.BarWidth, pct_height)
                x += ShowStatus.BarWidth + ShowStatus.InterBarMargin

        # draw column 'footer' header
        x = ShowStatus.LabelLeftMargin
        y = self.widget_height - ShowStatus.LabelBottomMargin
        qp.setPen(Qt.black)
        for char in self.data:
            qp.drawText(x, y, char)
            x += ShowStatus.BarWidth + ShowStatus.InterBarMargin

    def refresh(self, data):
        """Update self.percent with values matching 'data'."""

        self.percent = []
        for char in self.data:
            try:
                value = data[char]
            except KeyError:
                value = 0
            self.percent.append(value)

        self.update()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout

    class ShowStatusExample(QWidget):
        """Application to demonstrate the Morse Trainer 'display' widget."""

        def __init__(self):
            super().__init__()
            self.initUI()


        def initUI(self):
            self.alphabet_status = ShowStatus('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            self.numbers_status = ShowStatus('0123456789')
            self.punctuation_status = ShowStatus("""?/,.():;!'"=""")
            redisplay_button = QPushButton('Redisplay', self)

            hbox1 = QHBoxLayout()
            hbox1.addWidget(self.alphabet_status)
            hbox1.addWidget(self.numbers_status)
            hbox1.addWidget(self.punctuation_status)

            hbox2 = QHBoxLayout()
            hbox2.addWidget(redisplay_button)

            vbox = QVBoxLayout()
            vbox.addLayout(hbox1)
            vbox.addLayout(hbox2)
            self.setLayout(vbox)

            redisplay_button.clicked.connect(self.redisplayButtonClicked)

            self.setGeometry(100, 100, 800, 200)
            self.setWindowTitle('Example of ShowStatus widget')
            self.show()

        def redisplayButtonClicked(self):
            """Regenerate some data (random) and display it."""

            for gd in (self.alphabet_status, self.numbers_status, self.punctuation_status):
                # generate random data
                new = {}
                for char in gd.data:
                    new[char] = randint(0,100)/100
                # set first character to 0
                new[gd.data[0]] = 0
                # redisplay
                gd.refresh(new)


    app = QApplication(sys.argv)
    ex = ShowStatusExample()
    sys.exit(app.exec_())
