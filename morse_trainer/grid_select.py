#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 custom widget used by Morse Trainer.

GridSelect a grid of characters.  The user may select/deselect each character
and the display shows if the character is selected or deselected.

The state of the characters is returned as a dictionary:
    d = {'A': True, 'B': False, ...}

grid_select = GridSelect(data, max_cols=12)

d = grid_select.get_status()
grid_select.set_status(d)

"""

import platform
import logger

from PyQt5.QtWidgets import QWidget, QTableWidget, QPushButton, QMessageBox, QToolButton
from PyQt5.QtWidgets import QToolTip, QGroupBox, QGridLayout, QFrame, QLabel
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QFont, QColor, QPen


log = logger.Log('grid_select.log', logger.Log.DEBUG)


class GridSelect(QWidget):
    """Widget to display a grid of selected/unselected characters."""

    # set platform-dependent sizes
    if platform.system() == 'Linux':
        MaxColumns = 12             # default max number of columns
        Font = 'Courier'            # the font to use
        FontSize = 12               # font size
        TopOffset = 5               # top offset of first row
        LeftOffset = 5              # left offset of first column
        RowHeight = 25              # pixel height of a row
        ColWidth = 25               # pixel width of a column
    elif platform.system() == 'Darwin':
        MaxColumns = 12
        Font = 'Courier'
        FontSize = 12
        TopOffset = 5
        LeftOffset = 5
        RowHeight = 20
        ColWidth = 20
    elif platform.system() == 'Windows':
        MaxColumns = 12
        Font = 'Courier'
        FontSize = 12
        TopOffset = 5
        LeftOffset = 5
        RowHeight = 25
        ColWidth = 25
    else:
        raise Exception('Unrecognized platform: %s' % platform.system())

    def __init__(self, data, max_cols=12):
        """Initialize the widget.

        data  a string of characters to be displayed in the widget
        max_cols  the maximum number of columns to display

        The widget figures out how many rows there are from 'data'
        and 'max_cols'.
        """

        super().__init__()

        # declare state variables here so we know what they all are
        self.data = data            # the characters to display
        self.buttons = []           # list of display item button objects
        self.status = {}            # status dict: {'A':True, 'B':False, ...}
        self.max_cols = max_cols    # maximum number of columns to display
        self.num_rows = None        # number of rows in grid
        self.num_cols = None        # number of columns in grid
        self.font = None            # the font used
        self.font_size = None       # size of font

        self.initUI()

    def initUI(self):
        """Set up the UI."""

        self.setAutoFillBackground(True)

        # calculate the number of rows and columns to display
        num_chars = len(self.data)
        if num_chars > self.max_cols:
            self.num_cols = self.max_cols
            self.num_rows = int((num_chars + (self.max_cols-1))/self.max_cols)
        else:
            self.num_cols = num_chars
            self.num_rows = 1

        # figure out the widget size
        widget_width = (2*GridSelect.LeftOffset
                        + self.num_cols*GridSelect.ColWidth)
        widget_height = (2*GridSelect.TopOffset
                         + self.num_rows*GridSelect.RowHeight)

        self.setFixedWidth(widget_width)
        self.setFixedHeight(widget_height)
        self.setMinimumSize(widget_width, widget_height)

        # set the widget internal state
        self.font = QFont(GridSelect.Font, GridSelect.FontSize)
        self.font_size = GridSelect.FontSize

        # draw the characters in the grid, with surround highlight
        grid = QGridLayout(self)
        self.setLayout(grid)

        positions = [(i,j) for i in range(self.num_rows) for j in range(self.num_cols)]
        self.buttons = []

        for (char, pos) in zip(self.data, positions):
            self.status[char] = False
            button = QPushButton(char, self)
            self.buttons.append(button)
            button.setCheckable(True)       # make it a toggle button
            grid.addWidget(button, *pos)
            button.clicked.connect(self.clickButton)

    def clickButton(self, event):
        """Handle user selecting a grid button.

        Update the self.status dictionary.
        """

        source = self.sender()
        label = source.text()
        self.status[label] = not self.status[label]

    def x2index(self, x, y):
        """Convert widget x,y coordinate to row,column indices.

        Returns (row, col) or None if click isn't on a character.
        """

        # what column did we click?
        col = (x - GridSelect.LeftOffset) // GridSelect.ColWidth
        if col < 0 or col >= self.num_cols:
            return None

        # row
        row = (y - GridSelect.TopOffset) // GridSelect.RowHeight
        if row < 0 or row >= self.num_rows:
            return None

        return (row, col)

    def get_status(self):
        """Return widget selection status as a dictionary."""

        return self.status

    def set_status(self, status):
        """Set widget selection according to status dictionary."""

        for button in self.buttons:
            label = button.text()
            button.setChecked(status[label])
            self.status[label] = status[label]


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout

    class GridSelectExample(QWidget):
        """Application to demonstrate the Morse Trainer 'display' widget."""

        def __init__(self):
            super().__init__()
            self.initUI()


        def initUI(self):
            self.display_alphabet = GridSelect('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            self.display_numbers = GridSelect('0123456789')
            self.display_punctuation = GridSelect("""?/,.():;!'"=""")
            invert_button = QPushButton('Invert Selection', self)

            hbox1 = QHBoxLayout()
            hbox1.addWidget(self.display_alphabet)
            hbox1.addWidget(self.display_numbers)
            hbox1.addWidget(self.display_punctuation)

            hbox2 = QHBoxLayout()
            hbox2.addWidget(invert_button)

            vbox = QVBoxLayout()
            vbox.addLayout(hbox1)
            vbox.addLayout(hbox2)
            self.setLayout(vbox)

            invert_button.clicked.connect(self.invertButtonClicked)

            self.setGeometry(100, 100, 800, 200)
            self.setWindowTitle('Example of GridSelect widget')
            self.show()

        def invertButtonClicked(self):
            """Get alphabet (and others) selection, invert, put back."""

            for gd in (self.display_alphabet, self.display_numbers, self.display_punctuation):
                selection = gd.get_status()
                inverted = {key:(not value) for (key, value) in selection.items()}
                gd.set_status(inverted)


    app = QApplication(sys.argv)
    ex = GridSelectExample()
    sys.exit(app.exec_())
