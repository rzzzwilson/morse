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

"""

import platform
import logger

from PyQt5.QtWidgets import QWidget, QTableWidget, QPushButton, QMessageBox
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
        self.max_cols = max_cols    # maximum number of columns to display
        self.num_rows = None        # number of rows in grid
        self.num_cols = None        # number of columns in grid
        self.font = None            # the font used
        self.font_size = None       # size of font

        self.initUI()

        # force a draw
#        self.update()

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

        log('initUI: .num_cols=%s, .num_rows=%s' % (str(self.num_cols), str(self.num_rows)))

        # figure out the widget size
        widget_width = (2*GridSelect.LeftOffset
                        + self.num_cols*GridSelect.ColWidth)
        widget_height = (2*GridSelect.TopOffset
                         + self.num_rows*GridSelect.RowHeight)

        log('initUI: widget_width=%d, widget_height=%d' % (widget_width, widget_height))

        self.setFixedWidth(widget_width)
        self.setFixedHeight(widget_height)
        self.setMinimumSize(widget_width, widget_height)

        # set the widget internal state
        self.font = QFont(GridSelect.Font, GridSelect.FontSize)
        self.font_size = GridSelect.FontSize

        # draw the characters in the grid, with surround highlight
        positions = [(i,j) for i in range(self.num_rows) for j in range(self.num_cols)]
        log('positions=%s' % str(positions))
        grid = QGridLayout(self)
        self.setLayout(grid)
        for (char, pos) in zip(self.data, positions):
            button = QPushButton(char, self)
            log('button.? = %s' % str(dir(button)))
            button.setCheckable(True)       # make it a toggle button
            grid.addWidget(button, *pos)

    def mousePressEvent(self, e):
        """Left click handler - decide which character clicked, if any."""

        # coding for e.button() and e.type() values
        # button = {1:'left', 2:'right', 4:'middle'}
        # type = {2:'single', 4:'double'}

        log('mousePressEvent: mouse click, e.button()=%d, e.type()=%d'
            % (e.button(), e.type()))

        # single click, left button, show tooltip, if any at position
        if e.type() == 2 and e.button() == 1:
            log('mousePressEvent: left single mouse click')

            # figure out what index test we clicked on
            indices = self.x2index(e.x(), e.y())
            log('mousePressEvent: indices=%s' % str(indices))
            if indices:
                (row, col) = indices

                # check - the last row may be short
                if row == self.num_rows - 1:
                    # we ARE on the last row, check X position
                    if (self.num_cols * row) + col < len(self.data):
                        # clicked on a cell
                        log('mousePressEvent: left click at %s' % str(indices))
                        print('mousePressEvent: left click at %s' % str(indices))
                    else:
                        log('mousePressEvent: clicked off a cell')
                        print('mousePressEvent: clicked off a cell')
                else:
                    log('mousePressEvent: left click at %s' % str(indices))
                    print('mousePressEvent: left click at %s' % str(indices))
            else:
                log('mousePressEvent: clicked off a cell')
                print('mousePressEvent: clicked off a cell')

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

#    def paintEvent(self, e):
#        """Prepare to draw the widget."""
#
#        qp = QPainter()
#        qp.begin(self)
#        self.drawWidget(qp)
#        qp.end()
#
#    def drawWidget(self, qp):
#        """Draw the widget from internal state."""
#
#        # set to the font we use in the widget
#        qp.setFont(self.font)
#
#        # figure out display size
#        window_size = self.size()
#        width = window_size.width()
#        height = window_size.height()
#        self.display_width = width
#
#        # draw some squares
##        for i in range(self.num_cols):
##            self.draw_square(qp,
##                             GridSelect.LeftOffset+i*GridSelect.ColWidth,
##                             GridSelect.TopOffset, i%8)
#
##        qp.setPen(GridSelect.WidgetBGColour)
##        qp.setBrush(GridSelect.WidgetBGColour)
##        qp.drawRect(0, 0, width, height)
#
#        qp.setPen(Qt.black)
#        qp.drawRect(0, 0, width, height)


    def draw_square(self, qp, x, y, shape):

        colorTable = [0x666666, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

#        log('draw_square: x=%d, y=%d, shape=%d' % (x, y, shape))
#        log('draw_square: .num_cols=%d, .ColWidth=%d, .RowHeight=%d' % (self.num_cols, GridSelect.ColWidth, GridSelect.RowHeight))

        color = QColor(colorTable[shape])
        qp.fillRect(x, y, GridSelect.ColWidth - 1, GridSelect.RowHeight - 1, color)
#        log('draw_square: COLOUR .fillRect(%d, %d, %d, %d)'
#                % (x, y, GridSelect.ColWidth - 1, GridSelect.RowHeight - 1))

        qp.setPen(color.lighter())
        qp.drawLine(x, y + GridSelect.RowHeight - 1, x, y)
#        log('draw_square: LIGHTER .drawLine(%d, %d, %d, %d)' % (x, y + GridSelect.RowHeight - 1, x, y))
        qp.drawLine(x, y, x + GridSelect.ColWidth - 1, y)
#        log('draw_square: LIGHTER .drawLine(%d, %d, %d, %d)' % (x, y, x + GridSelect.ColWidth - 1, y))

        qp.setPen(color.darker())
        qp.drawLine(x + 1, y + GridSelect.RowHeight - 1,
            x + GridSelect.ColWidth - 1, y + GridSelect.RowHeight - 1)
#        log('draw_square: DARKER .drawLine(%d, %d, %d, %d)' % (x + 1, y + GridSelect.RowHeight - 1,
#                x + GridSelect.ColWidth - 1, y + GridSelect.RowHeight - 1))
        qp.drawLine(x + GridSelect.ColWidth - 1,
            y + GridSelect.RowHeight - 1, x + GridSelect.ColWidth - 1, y + 1)
#        log('draw_square: DARKER .drawLine(%d, %d, %d, %d)' % (x + GridSelect.ColWidth - 1,
#                y + GridSelect.RowHeight - 1, x + GridSelect.ColWidth - 1, y + 1))

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
            left_button = QPushButton('Left ⬅', self)
            right_button = QPushButton('Right ➡', self)

            hbox1 = QHBoxLayout()
            hbox1.addWidget(self.display_alphabet)
            hbox1.addWidget(self.display_numbers)
            hbox1.addWidget(self.display_punctuation)

            hbox2 = QHBoxLayout()
            hbox2.addWidget(left_button)
            hbox2.addWidget(right_button)

            vbox = QVBoxLayout()
            vbox.addLayout(hbox1)
            vbox.addLayout(hbox2)
            self.setLayout(vbox)

            left_button.clicked.connect(self.leftButtonClicked)
            right_button.clicked.connect(self.rightButtonClicked)

            self.setGeometry(100, 100, 800, 200)
            self.setWindowTitle('Example of GridSelect widget')
            self.show()

        def leftButtonClicked(self):
            """Move highlight to the left, if possible."""

            pass

        def rightButtonClicked(self):
            """Clear display, reenter new test text.."""

            pass


    app = QApplication(sys.argv)
    ex = GridSelectExample()
    sys.exit(app.exec_())
