#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Small utility functions.
"""


Alphabetics = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
Numbers = '0123456789'
Punctuation = """?,.!=/()'":;"""
AllUserChars = Alphabetics + Numbers + Punctuation
Koch = """KMRSUAPTLOWI.NJE=F0Y,VG5/Q9ZH38B?427C1D6X?():;!"'"""

StyleCSS = """
/*css stylesheet file that contains all the style information*/

QGroupBox {
    border: 1px solid black;
    border-radius: 3px;
}

QGroupBox:title{
    subcontrol-origin: margin;
/*    subcontrol-origin: content; */
/*    subcontrol-origin: padding; */
    subcontrol-position: top left;
    padding: -8px 5px 0 5;
}
"""


def get_style(path):
    """Read a style file and return the contents."""

    with open(path, 'r') as fd:
        stylesheet = fd.read()

    return str(stylesheet)

def morse2display(morse):
    """Convert a string for a morse character to 'display' morse.

    We use this to display expected/received characters in the
    display as using ./- is not nice.  For example, '.-.' is not
    as nice as '• ━ •'
    """

    # unicode chars
    DOT = '•'    #2022
    DASH = '━'   #2501
    SIX_PER_EM_SPACE = ' '   #2005

    result = []
    for dotdash in morse:
        if dotdash == '.':
            result.append(DOT)
        elif dotdash == '-':
            result.append(DASH)
        else:
            raise Exception("Unrecognized sign in '%s': %s" % (morse, dotdash))

    return SIX_PER_EM_SPACE.join(result)

def list2dict(char_iter):
    """Convert an iterable of chars to a True/False dict.
    
    ie, 'AC' -> {'A':True, 'B':False, 'C':True, ...}
    """
    
    result = {}
    
    for char in AllUserChars:
        result[char] = False
    
    for char in char_iter:
        result[char] = True
    
    return result


if __name__ == '__main__':
    morse = '.'
    while morse:
        morse = input('Enter morse, nothing to exit: ')
        result = morse2display(morse)
        print(result)
