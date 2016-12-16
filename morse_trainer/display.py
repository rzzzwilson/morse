#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 custom 'display' widget used by Morse Trainer.

Display two lines of English text.  Allow colour change to background
for individual characters.  Allow outline highlighting for any group
of two vertical characters.  Allow tooltip text for any group of two
vertical characters.

display = Display(...)

.clear()                # whole display cleared

.insert_upper(ch, index=None, fg=None)
.insert_lower(ch, index=None, fg=None)

display_id = .set_tooltip(txt, display_id=None)
.clear_tooltip(display_id)

.left_scroll(num=None)                      # could be automatic?

.upper_len()
.lower_len()

.set_highlight(index)

Instance variables
------------------

Text is always left-justified in the display.

.text_upper         # list of text in the display row
.text_lower         # a list of (char, colour) tuples

.tooltips_upper     # list of tooltip, None means 'not defined'
.tooltips_lower

.highlight_index    # index of column being highlighted
.highlight_colour   # colour of column being highlighted
"""

import platform

from PyQt5.QtWidgets import QWidget, QTableWidget, QPushButton, QMessageBox
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QFont, QColor, QPen


class Display(QWidget):
    """Widget to display two rows of text for the Morse Trainer."""

    # define colours
    AskTextColour = Qt.black
    AnsTextGoodColour = Qt.blue
    AnsTextBadColour = Qt.red
    HighlightColour = QColor(255, 255, 153)
    HighlightEdgeColour = QColor(234, 234, 234)
    HoverColour = Qt.black
    HoverBGNoneColour = QColor(255, 255, 255, alpha=0)
    HoverBGTooltipColour = QColor(255, 0, 0, alpha=100)

    # set platform-dependent sizes
    if platform.system() == 'Windows':
        DefaultWidgetHeight = 55
        DefaultWidgetWidth = 600
        BaselineOffsetUpper = 24
        BaselineOffsetLower = 48
        FontSize = 30
        TextLeftOffset = 3
        RoundedRadius = 3.0
        TooltipOffset = 33
        TooltipLineOffset = 13
    elif platform.system() == 'Linux':
        DefaultWidgetHeight = 55
        DefaultWidgetWidth = 600
        BaselineOffsetUpper = 24
        BaselineOffsetLower = 48
        FontSize = 30
        TextLeftOffset = 3
        RoundedRadius = 3.0
        TooltipOffset = 33
        TooltipLineOffset = 13
    elif platform.system() == 'Darwin':
        DefaultWidgetHeight = 55
        DefaultWidgetWidth = 600
        BaselineOffsetUpper = 24
        BaselineOffsetLower = 48
        FontSize = 30
        TextLeftOffset = 3
        RoundedRadius = 3.0
        TooltipOffset = 33
        TooltipLineOffset = 13
    else:
        raise Exception('Unrecognized platform: %s' % platform.system())

    # length of the test string used to determine character pixel width
    TestStringLength = 100

    def __init__(self):
        super().__init__()
        self.initUI()

        # clear the internal state
        self.clear()
        self.num_columns = 999999999

        # turn on mouse tracking
        self.setMouseTracking(True)

        # force a draw
        self.update()

        # get current width/height
        # height of widget never changes, width might
        self.display_width = self.width()
        self.display_height = self.height()

    def initUI(self):
        """Set up the UI."""

        # set the widget internal state
        self.setFixedHeight(Display.DefaultWidgetHeight)
        self.fixed_font = QFont('Courier', Display.FontSize)
        self.font_size = Display.FontSize
        self.font = self.fixed_font

        # define start positions for upper and lower text
        self.upper_start = QPoint(Display.TextLeftOffset,
                                  Display.BaselineOffsetUpper)
        self.lower_start = QPoint(Display.TextLeftOffset,
                                  Display.BaselineOffsetLower)

        # cache for pixel size of one character in display (set in drawWidget())
        self.char_width = None

    def clear(self):
        """Clear the widget display."""

        # clear actual data in display
        self.text_upper = []        # tuples of (char, colour)
        self.text_lower = []

        self.tooltips = []          # list of tooltip text or None

        self.next_display_id = 0    # ID of next tooltip display ID

        self.highlight_index = None # index of current highlight

        self.hover_index = None     # mouse hovering over this column
        self.hover_rect_bg = False  # show hover rectangle background if True

        self.update()               # force a redraw

    def mouseMoveEvent(self, e):
        # remove any artifacts
        self.hover_rect_bg = False  # clear hover background flag

        index = self.x2index(e.x())
        self.hover_index = index
        if index is not None:
            # if we have tooltip text at this column, flag for display
            text = self.tooltips[index][1]
            if text:
                self.hover_rect_bg = True
            self.update()

    def leaveEvent(self, e):
        self.hover_index = None
        self.update()

    def mousePressEvent(self, e):
        """Left click handler - maybe show 'tooltip'."""

        # coding for e.button() and e.type() values
        # button = {1:'left', 2:'right', 4:'middle'}
        # type = {2:'single', 4:'double'}

        # single click, left button, show tooltip, if any at position
        if e.type() == 2 and e.button() == 1:
            # figure out what index test we clicked on
            index = self.x2index(e.x())
            if index is not None and index >= 0:
                try:
                    (_, text) = self.tooltips[index]
                except IndexError:
                    text = None

                if text:
                    num_newlines = text.count('\n')
                    offset = (Display.TooltipOffset +
                              Display.TooltipLineOffset*num_newlines)
                    posn = e.globalPos() + QPoint(0, -offset)
                    QToolTip.showText(posn, text)

    def x2index(self, x):
        """Convert widget x coordinate to column index.

        Returns None if 'x' isn't in a column that is displayed.
        """

        index = (x - Display.TextLeftOffset + 1) // self.char_width
        max_length = max(self.upper_len(), self.lower_len())

        if not 0 <= index < max_length:
            index = None

        return index

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

        # calculate with of characters
        test_str = 'H' * Display.TestStringLength
        str_width = qp.fontMetrics().boundingRect(test_str).width()
        self.char_width = str_width // Display.TestStringLength

        # figure out display size
        window_size = self.size()
        width = window_size.width()
        height = window_size.height()
        self.display_width = width

        # calc the max # chars we can fit on display
        self.num_columns = (width - Display.TextLeftOffset) // self.char_width

        # clear the display area
        qp.setPen(Qt.white)
        qp.setBrush(Qt.white)
        qp.drawRoundedRect(0, 0, width, height,
                           Display.RoundedRadius, Display.RoundedRadius)

        # draw an outline
        qp.setPen(Qt.black)
#        qp.setBrush(Display.HoverBGNoneColour)
        qp.drawRoundedRect(0, 0, self.display_width, self.display_height,
                           Display.RoundedRadius,
                           Display.RoundedRadius)

        # draw any highlights
        if self.highlight_index is not None:
            # calculate pixel offset of X start of highlight
            hl_x = Display.TextLeftOffset + self.char_width * self.highlight_index
            # draw highlight rectangle
            qp.setPen(Display.HighlightEdgeColour)
            qp.setBrush(Display.HighlightColour)
            qp.drawRoundedRect(hl_x, 0, self.char_width,
                               Display.DefaultWidgetHeight,
                               Display.RoundedRadius,
                               Display.RoundedRadius)

        # draw upper text
        x = Display.TextLeftOffset
        last_colour = None
        for (char, colour) in self.text_upper:
            if last_colour != colour:
                qp.setPen(colour)
                last_colour = colour
            qp.drawText(x, Display.BaselineOffsetUpper, char)
            x += self.char_width

        # draw lower text
        x = Display.TextLeftOffset
        last_colour = None
        for (char, colour) in self.text_lower:
            if last_colour != colour:
                qp.setPen(colour)
                last_colour = colour
            qp.drawText(x, Display.BaselineOffsetLower, char)
            x += self.char_width

        # draw hover selection, if any
        if self.hover_index is not None:
            # calculate pixel offset of X start of hover selection
            hl_x = Display.TextLeftOffset + self.char_width * self.hover_index
            # draw hover selection rectangle
            qp.setPen(Display.HoverColour)
            qp.setBrush(Display.HoverBGNoneColour)
            if self.hover_rect_bg:
                qp.setBrush(Display.HoverBGTooltipColour)
            qp.drawRoundedRect(hl_x, 0, self.char_width,
                               Display.DefaultWidgetHeight,
                               Display.RoundedRadius,
                               Display.RoundedRadius)

    def resizeEvent(self, e):
        """Handle widget resize.

        The main focus here is that we must scroll the display text if the
        width becomes small and limits the view.
        """

        # refresh display width and height
        self.display_width = self.width()
        self.display_height = self.height()

        # do we need to scroll?
        max_length = max(self.upper_len(), self.lower_len())
        if self.num_columns < max_length:
            self.left_scroll(max_length - self.num_columns)

    def upper_len(self):
        """Return length of the upper text."""

        return len(self.text_upper)

    def lower_len(self):
        """Return length of the lower text."""

        return len(self.text_lower)

    def insert_upper(self, ch, fg=None):
        """Insert char at end of upper row.

        ch     the character to insert
        fg     foreground colour of char
        """

        if fg is None:
            fg = Display.AskTextColour

        self.text_upper.append((ch, fg))
        if len(self.text_upper) > len(self.tooltips):
            self.tooltips.append((self.next_display_id, None))
            self.next_display_id += 1

        # decide if we have to scroll
        max_length = max(self.upper_len(), self.lower_len())
        if max_length > self.num_columns:
            self.left_scroll(max_length - self.num_columns)

    def insert_lower(self, ch, fg=None):
        """Insert char at end of lower row.

        ch     the character to insert
        fg     foreground colour of char
        """

        if fg is None:
            fg = Display.AnsTextGoodColour

        self.text_lower.append((ch, fg))
        if len(self.text_lower) > len(self.tooltips):
            self.tooltips.append((self.next_display_id, None))
            self.next_display_id += 1

        # decide if we have to scroll
        max_length = max(self.upper_len(), self.lower_len())
        if max_length > self.num_columns:
            self.left_scroll(max_length - self.num_columns)

    def set_tooltip(self, display_id, text):
        """"Set tooltip text at a column.

        display_id  display ID of the tooltip to set
        text        the new tooltip text
        """

        # calculate index from display ID
        # subtract display ID of first in tooltips
        index = display_id - self.tooltips[0][0]

        # update tooltip text, catch error if index wrong
        try:
            self.tooltips[index] = (display_id, text)
        except IndexError:
            raise Exception("Sorry, display ID '%d' not found in .tooltips '%s'"
                            % (display_id, str(self.tooltips)))

    def clear_tooltip(self, display_id):
        """"Clear tooltip text at a column.

        display_id  display ID of the tooltip to clear
        """

        self.set_tooltip(display_id, None)

    def left_scroll(self, num=None):
        """Left scroll display.

        num  number of columns to scroll left by

        If 'num' not supplied, scroll left a default amount.
        """

        # default the value for number of columns to scroll left
        if num is None:
            num = 1

        # do the scrolling
        self.text_upper = self.text_upper[num:]
        self.text_lower = self.text_lower[num:]
        self.tooltips = self.tooltips[num:]
        self.set_highlight()
        self.update()

    def set_highlight(self, index=None):
        """Show a highlight at display index position 'index'.

        Throws an IndexError exception if 'index' not within upper text
        or one position past the right end of the longest text.
        """

        max_length = max(self.upper_len(), self.lower_len())
        if index is None:
            index = max_length - 1

        if not 0 <= index <= max_length:
            raise IndexError('Highlight index %d is out of range [0, %d]'
                             % (index, max_length))

        self.highlight_index = index
        self.update()

    def get_highlight(self):
        """Return the current highlight index."""

        return self.highlight_index
