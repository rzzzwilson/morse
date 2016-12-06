#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 custom widget used by Morse Trainer.

Display two lines of English text.  Allow colour change to background
for individual characters.  Allow outline highlighting for any group
of two vertical characters.  Allow tooltip text for any group of two
vertical characters.

display = Display(...)

.clear()                # whole display cleared

.insert_upper(ch, index=None, fg=None)
.insert_lower(ch, index=None, fg=None)

.set_tooltip(index, txt)
.clear_tooltip(index)

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
    HoverEdgeColour = QColor(255, 255, 255, alpha=0)

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

        # turn on mouse tracking
        self.setMouseTracking(True)

        # force a draw
        self.update()

    def initUI(self):
        """Set up the UI."""

        # set the widget internal state
        self.setMinimumSize(Display.DefaultWidgetWidth,
                            Display.DefaultWidgetHeight)
        self.fixed_font = QFont('Courier', Display.FontSize)
        self.font_size = Display.FontSize
        self.font = self.fixed_font

        # height of widget never changes, width might
        self.height = Display.DefaultWidgetHeight

        # define start positions for upper and lower text
        self.upper_start = QPoint(Display.TextLeftOffset, Display.BaselineOffsetUpper)
        self.lower_start = QPoint(Display.TextLeftOffset, Display.BaselineOffsetLower)

        # cache for pixel size of one character in display (set in drawWidget())
        self.char_width = None
        self.char_height = None

    def clear(self):
        """Clear the widget display."""

        # clear actual data in display
        self.text_upper = []        # tuples of (char, colour)
        self.text_lower = []

        self.tooltips = []          # list of tooltip text or None

        self.highlight_index = None # index of current highlight

        self.hover_index = None     # mouse hovering over this column

        self.update()               # force a redraw

    def mouseMoveEvent(self, e):
        index = self.x2index(e.x())
        self.hover_index = index
        if index is not None:
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
            if index >= 0:
                try:
                    text = self.tooltips[index]
                except IndexError:
                    text = None

                if text:
                    num_newlines = text.count('\n')
                    offset = (Display.TooltipOffset +
                              Display.TooltipLineOffset*num_newlines)
                    posn = e.globalPos() + QPoint(0, -offset)
                    QToolTip.showText(posn, text)

    def paintEvent(self, e):
        """Prepare to draw the widget."""

        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def x2index(self, x):
        """Convert widget x coordinate to column index.

        Returns None if 'x' isn't in a column that is displayed.
        """

        index = (x - Display.TextLeftOffset + 1) // self.char_width
        max_length = max(self.upper_len(), self.lower_len())

        if not 0 <= index < max_length:
            index = None

        return index

    def drawWidget(self, qp):
        """Draw the widget from internal state."""

        # set to the font we use in the widget
        qp.setFont(self.font)

        # get char sizes in pixels from a test string (once)
        # we do this here because we need a context and font before measurement
        if self.char_width is None:
            test_str = 'H' * Display.TestStringLength
            str_width = qp.fontMetrics().boundingRect(test_str).width()
            self.char_width = str_width // Display.TestStringLength + 1
            self.char_height = qp.fontMetrics().boundingRect(test_str).height()

        # clear the display
        window_size = self.size()
        width = window_size.width()
        height = window_size.height()
        qp.setPen(Qt.white)
        qp.setBrush(Qt.white)
        qp.drawRect(0, 0, width, height)

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
            qp.setBrush(Display.HoverEdgeColour)
            qp.drawRoundedRect(hl_x, 0, self.char_width,
                               Display.DefaultWidgetHeight,
                               Display.RoundedRadius,
                               Display.RoundedRadius)

    def resizeEvent(self, e):
        """Handle widget resize.

        The main focus here is that we must scroll the display text if the
        width becomes small and limits the view.
        """

        pass
#        print('e: %s' % str(dir(e)))
#        print('e.GraphicsSceneResize=%s' % str(e.GraphicsSceneResize))

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
#        if len(self.text_upper) > len(self.tooltips):
#            self.tooltips.append(None)
        self.tooltips.append(None)

    def insert_lower(self, ch, fg=None):
        """Insert char at end of lower row.

        ch     the character to insert
        fg     foreground colour of char
        """

        if fg is None:
            fg = Display.AnsTextGoodColour

        self.text_lower.append((ch, fg))
#        if len(self.text_lower) > len(self.tooltips):
#            self.tooltips.append(None)
        self.tooltips.append(None)

    def set_tooltip(self, index, text):
        """"Set tooltip text at a column.

        index  index of the tooltip to set
        text   the new tooltip text
        """

        self.tooltips[index] = text

    def clear_tooltip(self, index):
        """"Clear tooltip text at a column.

        index  index of the tooltip to clear
        """

        self.tooltips[index] = None

    def left_scroll(self, num=None):
        """Left scroll display.

        num  number of columns to scroll left by

        If 'num' not supplied, scroll left a default amount.
        """

        pass

    def set_highlight(self, index=None):
        """Show a highlight at index position 'index'.

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


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout

    class DisplayExample(QWidget):
        """Application to demonstrate the Morse Trainer 'display' widget."""

        def __init__(self):
            super().__init__()
            self.initUI()


        def initUI(self):
            self.display = Display()
            left_button = QPushButton('Left ⬅', self)
            right_button = QPushButton('Right ➡', self)

            hbox1 = QHBoxLayout()
            hbox1.addWidget(self.display)

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
            self.setWindowTitle('Example of Display widget')
            self.show()

            # populate the display widget a bit
            for index in range(40):
                if index in (7, 21):
                    self.display.insert_upper('U', fg=Display.AnsTextBadColour)
                else:
                    self.display.insert_upper('U', fg=Display.AskTextColour)

            for index in range(39):
                if index in (5, 19):
                    self.display.insert_lower('L', fg=Display.AnsTextBadColour)
                else:
                    self.display.insert_lower('L', fg=Display.AnsTextGoodColour)
            self.display.set_highlight(40)
            self.display.set_tooltip(0, "Expected 'A', got 'N'\nweqweqwe")
            self.display.set_tooltip(5, 'Tooltip at index 5, rewyerewrewtrewtrewtrewtrewrtewtrewrewtrewtrewtrewtrewtrew')
            self.display.set_tooltip(19, "Expected 'A', got 'N'\nweqweqwe\nasdasdadasd\na\na\na\na\na")

        def leftButtonClicked(self):
            """Move highlight to the left, if possible."""

            index = self.display.get_highlight()
            if index is not None:
                index -= 1
                if index >= 0:
                    self.display.set_highlight(index)

        def rightButtonClicked(self):
            """Clear display, reenter new test text.."""

            self.display.clear()

            for index in range(25):
                if index in (7, 21):
                    self.display.insert_upper('1', fg=Display.AnsTextBadColour)
                else:
                    self.display.insert_upper('1', fg=Display.AskTextColour)

            self.display.insert_upper(' ', fg=Display.AskTextColour)

            for index in range(25):
                if index in (5, 19):
                    self.display.insert_lower('8', fg=Display.AnsTextBadColour)
                else:
                    self.display.insert_lower('8', fg=Display.AnsTextGoodColour)
            self.display.set_highlight(10)
            self.display.set_tooltip(0, 'Tooltip at index 0')
            self.display.set_tooltip(5, 'Tooltip at index 5')
            self.display.set_tooltip(19, 'Tooltip at index 19')




    app = QApplication(sys.argv)
    ex = DisplayExample()
    sys.exit(app.exec_())
