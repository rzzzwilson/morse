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
.clear_upper(index)     # single char removed
.clear_lower(index)     # single char removed

.insert_upper(ch, index=None, fg=None)
.insert_lower(ch, index=None, fg=None)

.show_str_upper(string)
.show_str_lower(string)
.show_str(upper, lower) # fills both upper and lower

.set_tooltip(index, txt)
.clear_tooltip(index)

.left_scroll(num=None)                      # could be automatic?

.set_upper_font(colour=..., size=...)       # set size/colour of display row
.set_lower_font(colour-..., size=...)

.set_upper_colour(index, fg=..., bg=...)    # set fg/bg colour of one char
.set_lower_colour(index, fg=..., bg=...)

.upper_len()
.lower_len()

.set_highlight(index)

Instance variables
------------------

Text is always left-justified in the display.

.text_upper         # list of text in the display row
.text_lower

.cursor_upper       # index of 'next to be filled'
.cursor_lower

.tooltips_upper     # list of tooltip, None means 'not defined'
.tooltips_lower

.highlight_index    # index of column being highlighted
.highlight_colour   # colour of column being highlighted
"""

import platform

from PyQt5.QtWidgets import QWidget, QTableWidget, QPushButton
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
from PyQt5.QtGui import QFontDatabase


# set platform-dependent sizes
if platform.system() == 'Windows':
    DefaultWidgetHeight = 55
    DefaultWidgetWidth = 600
    BaselineOffsetUpper = 24
    BaselineOffsetLower = 48
    FontSize = 30
    TextLeftOffset = 3
elif platform.system() == 'Linux':
    DefaultWidgetHeight = 55
    DefaultWidgetWidth = 600
    BaselineOffsetUpper = 24
    BaselineOffsetLower = 48
    FontSize = 30
    TextLeftOffset = 3
elif platform.system() == 'Darwin':
    DefaultWidgetHeight = 55
    DefaultWidgetWidth = 600
    BaselineOffsetUpper = 24
    BaselineOffsetLower = 48
    FontSize = 30
    TextLeftOffset = 3
else:
    raise Exception('Unrecognized platform: %s' % platform.system())

class Display(QWidget):
    """Widget to display two rows of text for the Morse Trainer."""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Set up the UI for the display and internal state."""

        # do what we can for the widget
        self.setMinimumSize(DefaultWidgetWidth, DefaultWidgetHeight)

        # set the widget internal state
#        self.fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.fixed_font = QFont('Courier', FontSize)
        self.font_size = FontSize
        self.font = self.fixed_font

        # define colours
        self.blue_colour = QColor(128, 128, 255)
        self.black_colour = QColor(0, 0, 0)
        self.red_colour = QColor(255, 0, .64)
        self.yellow_colour = QColor(255, 255, 153)
        self.highlight_edge_colour = QColor(234, 234, 234)
        self.background_colour = QColor(255, 255, 255)

        self.ask_text_colour = self.black_colour
        self.ans_text_good_colour = self.blue_colour
        self.ans_text_bad_colour = self.red_colour

        self.text_upper = []        # tuples of (char, colour)
        self.text_lower = []
        self.cursor_upper = 0       # index of upper/lower cursor
        self.cursor_lower = 0
        self.tooltips_upper = []    # text of upper/lower tooltips
        self.tooltips_lower = []
        self.highlight_index = 39
        self.highlight_index = None
        self.highlight_colour = self.yellow_colour

        # height of widget never changes, width might
        self.height = DefaultWidgetHeight

        # define start positions for upper and lower text
        self.upper_start = QPoint(TextLeftOffset, BaselineOffsetUpper)
        self.lower_start = QPoint(TextLeftOffset, BaselineOffsetLower)

###############  TEMP
        for index in range(40):
            self.insert_upper('U', fg=self.ask_text_colour)

        for index in range(39):
            if index in (5, 32):
                self.insert_lower('L', fg=self.ans_text_bad_colour)
            else:
                self.insert_lower('L', fg=self.ans_text_good_colour)
        self.set_highlight()
###############  TEMP

        # force a draw
        self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        qp.setFont(self.font)

        # get size of strng of 10 chars
        test_str = 'HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH'
        str_width = qp.fontMetrics().boundingRect(test_str).width()
        str_height = qp.fontMetrics().boundingRect(test_str).height()
        char_width = str_width // len(test_str) + 1

        # clear the display
        window_size = self.size()
        width = window_size.width()
        height = window_size.height()
        qp.setPen(self.background_colour)
        qp.setBrush(self.background_colour)
        qp.drawRect(0, 0, width, height)

        # draw any highlights
        if self.highlight_index is not None:
            # calculate pixel offset of X start of highlight
            hl_x = TextLeftOffset + char_width * self.highlight_index
            # draw highlight rectangle
            qp.setPen(self.highlight_edge_colour)
            qp.setBrush(self.highlight_colour)
            qp.drawRect(hl_x, 0, char_width, DefaultWidgetHeight)

        # draw upper text
        x = TextLeftOffset
        last_colour = None
        for (char, colour) in self.text_upper:
            if last_colour != colour:
                qp.setPen(colour)
                last_colour = colour
            qp.drawText(x, BaselineOffsetUpper, char)
            x += char_width

        # draw lower text
        x = TextLeftOffset
        last_colour = None
        for (char, colour) in self.text_lower:
            if last_colour != colour:
                qp.setPen(colour)
                last_colour = colour
            qp.drawText(x, BaselineOffsetLower, char)
            x += char_width

    def resizeEvent(self, e):
        """Handle widget resize.

        The main focus here is that we must scroll the display ytexy if the
        width becomes small enough.
        """

        print('resizeEvent: e=%s' % str(e))
#        print('e: %s' % str(dir(e)))
#        print('e.GraphicsSceneResize=%s' % str(e.GraphicsSceneResize))

    def upper_len(self):
        return len(self.text_upper)

    def lower_len(self):
        return len(self.text_lower)

    def clear(self):
        """Clear the widget display."""

        pass

    def clear_upper(self, index):
        """Remove character in upper row at index."""

        pass

    def clear_lower(self, index):
        """Remove character in lower row at index."""

        pass

    def insert_upper(self, ch, index=None, fg=None):
        """Insert char at end of upper row.

        ch     the character to insert
        fg     foreground colour of char
        """

        if fg is None:
            fg = self.ask_text_colour

        if index is None:
            self.text_upper.append((ch, fg))

    def insert_lower(self, ch, index=None, fg=None):
        """Insert char at end of lower row.

        ch     the character to insert
        fg     foreground colour of char
        """

        if fg is None:
            fg = self.ans_text_good_colour

        if index is None:
            self.text_lower.append((ch, fg))

    def show_text_upper(self, text):
        """Replace upper row with text.

        The existing upper row is replaced entirely, tooltips/highlight cleared.
        """

        pass

    def show_text_lower(self, text):
        """Replace lower row with text.

        The existing lower row is replaced entirely, tooltips/highlight cleared.
        """

        pass

    def show_str(self, upper, lower):
        """Replace upper AND lower rows with text.

        The existing rows are replaced entirely, tooltips/highlight cleared.
        """

        pass

    def set_tooltip(self, index, text=None):
        """"Set tooltip text at a column.

        text  the new tooltip text

        If 'text' is None, remove the tooltip.
        """

        pass

    def left_scroll(self, num=None):
        """Left scroll display.

        num  number of columns to scroll left by

        If 'num' not supplied, scroll left a default amount.
        """

        pass

    def set_upper_font(self, size=None, colour=None):
        """Set size/colour of upper font.

        size    the font size
        colour  the font foreground colour

        If either param is None, use a default value.
        """

        pass

    def set_lower(self, size=None, colour=None):
        """Set size/colour of lower font.

        size    the font size
        colour  the font foreground colour

        If either param is None use a default value.
        """

        pass

    def set_highlight(self, index=None):
        """Show a highlight at index position 'index'.

        If index is None, set highlight at end of upper text.
        Throws an IndexError exception if 'index' not within upper text.
        """

        if index is None:
            index = self.upper_len() - 1

        if not 0 <= index < self.upper_len():
            raise IndexError('Highlight index %d is out of range [0, %d]'
                             % (index, self.upper_len()))

        self.highlight_index = index
        return index

    def get_highlight(self):
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

        def leftButtonClicked(self):
            """Move highlight to the left, if possible."""

            index = self.display.get_highlight()
            index -= 1
            print('index=%d' % index)
            if index >= 0:
                self.display.set_highlight(index)
            self.display.update()

        def rightButtonClicked(self):
            """Move highlight to the left, if possible."""

            self.display.set_highlight()
            self.display.update()


    app = QApplication(sys.argv)
    ex = DisplayExample()
    sys.exit(app.exec_())
