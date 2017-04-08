#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A PyQt5 custom widget used by Morse Trainer.

Shows the characters to be used in the send/receive tests.  Use either
the Koch suggested set or a custom set.

charset = Charset(Koch_status, Koch_number, User_charset)

charset.setState(Koch_status, Koch_number, User_charset)
(Koch_status, Koch_number, User_charset) = charset.getSelected()

Raises a '.changed' signal on any state change.  The event receives a tuple:
    (Koch_status, Koch_number, User_charset)
"""

import platform

from PyQt5.QtWidgets import QWidget, QGridLayout, QButtonGroup, QVBoxLayout
from PyQt5.QtWidgets import QGroupBox, QSpacerItem
from PyQt5.QtWidgets import QPushButton, QRadioButton, QSpinBox, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

from grid_select import GridSelect
import utils


class Charset(QWidget):
    """Widget to display/select the characters used during send/receive ."""

    # set platform-dependent sizes
    if platform.system() == 'Linux':
        pass
    elif platform.system() == 'Darwin':
        pass
    elif platform.system() == 'Windows':
        pass
    else:
        raise Exception('Unrecognized platform: %s' % platform.system())

    # set Koch max/min numbers
    KochMin = 2
    KochMax = len(utils.Koch)


    # signal raised when internal state changes
    changed = pyqtSignal(tuple)


    def __init__(self, koch_selected=True, koch_num=2, user_charset=None):
        """Initialize the widget.

        koch_selected  True if the Koch suggested characters are to be used
        koch_num       the number of Koch characters being used
        user_selected  a dict of the selected user-defined characters
        """

        super().__init__()

        # declare state variables here so we know what they all are
        self.make_signal = False            # turn off signals until ready

        self.koch = koch_selected           # True if we are using Koch
        self.koch_num = koch_num            # the number of Koch characters used
        if user_charset is None:
            user_charset = {}
        self.user_charset = user_charset    # user-selected characters

        # set up the UI
        self.initUI()

        # set status of the widget (would signal here if we didn't inhibit)
        self.setKoch(koch_selected)
        self.setKochNumber(koch_num)
        self.setSelected(user_charset)

        # tie widgets into change handlers
        self.rb_Koch.clicked.connect(self.changeRBKoch)
        self.rb_User.clicked.connect(self.changeRBUser)
        self.sb_KochNumber.valueChanged.connect(self.changeKochNumberHandler)
        self.btn_Alphas.clicked.connect(self.setAllAlphasHandler)
        self.btn_Numbers.clicked.connect(self.setAllNumbersHandler)
        self.btn_Punct.clicked.connect(self.setAllPunctHandler)

        self.gs_Alphas.changed.connect(self.gs_item_clicked)
        self.gs_Numbers.changed.connect(self.gs_item_clicked)
        self.gs_Punct.changed.connect(self.gs_item_clicked)

        # arrange for widget to start signalling now
        self.make_signal = True

        self.setFixedHeight(270)
        self.show()

    def initUI(self):
        """Set up the UI."""

        # create all the sub-widgets
        self.rb_Koch = QRadioButton('Use the Koch character set')
        koch_using = QLabel('Using:')
        self.sb_KochNumber = QSpinBox(self)
        self.sb_KochNumber.setMinimum(Charset.KochMin)
        self.sb_KochNumber.setMaximum(Charset.KochMax)
        self.rb_User = QRadioButton('Select the characters to use')
        user_using = QLabel('Using:')
        self.lbl_UserNumber = QLabel('0')
        self.btn_Alphas = QPushButton('Alphabet', self)
        self.gs_Alphas = GridSelect(utils.Alphabetics)
        self.btn_Numbers = QPushButton('Numbers', self)
        self.gs_Numbers = GridSelect(utils.Numbers)
        self.btn_Punct = QPushButton('Punctuation', self)
        self.gs_Punct = GridSelect(utils.Punctuation)

        layout = QVBoxLayout()
        groupbox = QGroupBox('Test character set')
        groupbox.setStyleSheet(utils.StyleCSS)
        layout.addWidget(groupbox)

        # tie the radio buttons into a group
        rb_group = QButtonGroup(self)
        rb_group.addButton(self.rb_Koch)
        rb_group.addButton(self.rb_User)

        # put widgets into a grid
        grid = QGridLayout()
        grid.setSpacing(1)
        grid.setHorizontalSpacing(2)
        grid.setVerticalSpacing(1)

        row = 0
        grid.addWidget(self.rb_Koch, row, 0, 1, 3,
                       alignment=Qt.AlignLeft|Qt.AlignVCenter)
        grid.addWidget(koch_using, row, 3,
                       alignment=Qt.AlignRight|Qt.AlignVCenter)
        grid.addWidget(self.sb_KochNumber, row, 4,
                       alignment=Qt.AlignLeft|Qt.AlignVCenter)

        row += 1
        grid.addWidget(self.rb_User, row, 0, 1, 3, alignment=Qt.AlignLeft)
        grid.addWidget(user_using, row, 3,
                       alignment=Qt.AlignRight|Qt.AlignVCenter)
        grid.addWidget(self.lbl_UserNumber, row, 4,
                       alignment=Qt.AlignLeft|Qt.AlignVCenter)

        row += 1
        grid.addWidget(self.btn_Alphas, row, 1,
                       alignment=Qt.AlignRight|Qt.AlignVCenter)
        grid.addWidget(self.gs_Alphas, row, 2, 2, 3,
                       alignment=Qt.AlignLeft|Qt.AlignCenter)

        row += 2
        grid.addWidget(self.btn_Numbers, row, 1, 2, 1,
                       alignment=Qt.AlignRight|Qt.AlignVCenter)
        grid.addWidget(self.gs_Numbers, row, 2, 2, 3,
                       alignment=Qt.AlignLeft|Qt.AlignVCenter)

        row += 2
        grid.addWidget(self.btn_Punct, row, 1, 2, 1,
                       alignment=Qt.AlignRight|Qt.AlignVCenter)
        grid.addWidget(self.gs_Punct, row, 2, 2, 3,
                       alignment=Qt.AlignLeft|Qt.AlignVCenter)

        # add empty column that stretches
        grid.addItem(QSpacerItem(1,1), row, 4)
        grid.setColumnStretch(4, 1)

        groupbox.setLayout(grid)
        self.setLayout(layout)

        self.setMinimumSize(550, 250)

        self.setWindowTitle('Test of Charset widget')
        self.show()

        # tie widgets to change handlers
        self.gs_Alphas.changed.connect(self.was_changed)
        self.gs_Numbers.changed.connect(self.was_changed)
        self.gs_Punct.changed.connect(self.was_changed)

    def setKoch(self, status):
        """Set the charset used, Koch or User.

        status  True if Koch used, else False
        """

        self.koch = status
        if status:
            self.rb_Koch.setChecked(True)
            self.sb_KochNumber.setEnabled(True)

            self.rb_User.setChecked(False)
            self.btn_Alphas.setDisabled(True)
            self.gs_Alphas.setDisabled(True)
            self.btn_Numbers.setDisabled(True)
            self.gs_Numbers.setDisabled(True)
            self.btn_Punct.setDisabled(True)
            self.gs_Punct.setDisabled(True)
        else:
            self.rb_Koch.setChecked(False)
            self.sb_KochNumber.setDisabled(True)

            self.rb_User.setChecked(True)
            self.btn_Alphas.setDisabled(False)
            self.gs_Alphas.setDisabled(False)
            self.btn_Numbers.setDisabled(False)
            self.gs_Numbers.setDisabled(False)
            self.btn_Punct.setDisabled(False)
            self.gs_Punct.setDisabled(False)

        self.update()

    def setKochNumber(self, koch_num):
        """Set the 'Koch number'."""

        self.sb_KochNumber.setValue(koch_num)
        # worry about the spinbox being disabled

        self.update()

    def setSelected(self, selected):
        """Sets the user-selected characters.

        selected  a dict showing which chars are selected

        The dict has the form:`
            {'A':True, 'B':False, ..., '0':True, ..., '!':False}
        """

        # worry about the grid displays being disabled?
        self.user_charset = selected
        self.gs_Alphas.setState(selected)
        self.gs_Numbers.setState(selected)
        self.gs_Punct.setState(selected)

        self.update()

    def getSelected(self):
        """Gets a dict containing the user-selected characters.

        Returns a dict:``
            {'A':True, 'B':False, ..., '0':True, ..., '!':False}
        """

        # worry about the grid displays being disabled?
        alpha_selected = self.gs_Alphas.getState()
        num_selected = self.gs_Numbers.getState()
        punct_selected = self.gs_Punct.getState()

        # combine the three dictionaries
        return {**alpha_selected, **num_selected, **punct_selected}

    def changeRBKoch(self, signal):
        """Handle a click on the Koch radiobutton."""

        self.setKoch(True)
        self.was_changed()

    def changeRBUser(self, signal):
        """Handle a click on the User radiobutton."""

        self.setKoch(False)
        self.was_changed()

    def changeKochNumberHandler(self, signal):
        """User changed the Koch number spin box."""

        self.koch_num = self.sb_KochNumber.value()
        self.was_changed()

    def gs_item_clicked(self):
        """A grid select item was clicked.  Update the user "in use" count."""

        # update the self.user_charset dict
        self.user_charset = self.getSelected()

        # update "in use" count for user chars
        self.setUserCount()

        self.was_changed()

    def was_changed(self):
        """Something changed inside the widget.  Tell the world."""

        self.changed.emit(self.getState())

    def setAllAlphasHandler(self, signal):
        """User clicked on the 'use all alphas' button."""

        self.handleCharsetButton(self.gs_Alphas)

    def setAllNumbersHandler(self, signal):
        """User clicked on the 'use all numbers' button."""

        self.handleCharsetButton(self.gs_Numbers)

    def setAllPunctHandler(self, signal):
        """User clicked on the 'use all punctuation' button."""

        self.handleCharsetButton(self.gs_Punct)

    def handleCharsetButton(self, gs):
        """Handle a click on any charset button.

        gs  reference to the GridSelect object
        """

        # if all already selected, clear
        selection = gs.getState()
        all_true = all([value for (key, value) in selection.items()])

        if all_true:
            # all selected, turn all off
            new_dict = {key:False for key in selection}
        else:
            # one or more not selected, turn all on
            new_dict = {key:True for key in selection}

        gs.setState(new_dict)

        # update "in use" count for user chars
        self.user_charset = self.getSelected()
        self.setUserCount()
        self.update()

        self.was_changed()

    def setUserCount(self):
        """Update the "in use" count for user characters."""

        count = 0

        for gs in (self.gs_Alphas, self.gs_Numbers, self.gs_Punct):
            status = gs.getState()
            for (_, v) in status.items():
                if v:
                    count += 1

        self.lbl_UserNumber.setText(str(count))
        self.lbl_UserNumber.update()

    def getState(self):
        """Returns state of the widget.

        Returns a tuple: (koch, koch_number, user_charset)
        """

        return (self.koch, self.koch_num, self.user_charset)

    def setState(self, koch, koch_num, user_charset):
        """Update internal values and redraw.

        koch          True if using Koch, False if using user charset
        koch_num      number of Koch characters being used
        user_charset  the user charset being used
        """

        self.koch = koch
        self.koch_num = koch_num
        self.user_charset = user_charset

        # now set the UI to show the above state
        self.rb_Koch.setChecked(koch)
        self.rb_User.setChecked(not koch)
        self.sb_KochNumber.setValue(koch_num)

        # set buttons in all grid select sub-widgets
        self.gs_Alphas.changed.connect(self.gs_item_clicked)
        self.gs_Numbers.changed.connect(self.gs_item_clicked)
        self.gs_Punct.changed.connect(self.gs_item_clicked)
        for gs in (self.gs_Alphas, self.gs_Numbers, self.gs_Punct):
            gs.setState(user_charset)

        self.setUserCount()

        self.update()
