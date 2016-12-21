#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 custom widget used by Morse Trainer.

Shows a grid of characters.  The user may select/deselect each character
and the display shows if the character is selected or deselected.

grid_select = GridSelect(data, max_cols=12)

d = grid_select.get_selection()
grid_select.set_selection(d)

grid_select.clear()

The state of the characters is returned (and set) as a dictionary:
    d = {'A': True, 'B': False, ...}

Raises a '.changed' signal on any state change.  Event includes self.status.
"""

import platform

from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont


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

    # prepare the signals
    changed = pyqtSignal(dict, name='changed')

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

        # set up the UI
        self.initUI()
        self.clear()

    def initUI(self):
        """Set up the UI."""

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

        positions = [(i,j) for i in range(self.num_rows)
                               for j in range(self.num_cols)]
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

        Update the self.status dictionary and emit a 'changed' signal.
        """

        # update the internal status dictionary
        source = self.sender()
        label = source.text()
        self.status[label] = not self.status[label]

        # emit a 'changed' signal
        self.changed.emit(self.status)

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

    def getState(self):
        """Return widget selection status as a dictionary."""

        return self.status

    def setState(self, status):
        """Set widget selection according to status dictionary."""

        # set status and state of each button
        for button in self.buttons:
            label = button.text()
            new_status = True
            try:
                new_status = status[label]
            except KeyError:
                pass
            else:
                button.setChecked(new_status)
                self.status[label] = new_status

    def clear(self):
        """Set all grid buttons to OFF."""

        for char in self.data:
            self.status[char] = False
        for btn in self.buttons:
            btn.setChecked(False)
        self.update()
