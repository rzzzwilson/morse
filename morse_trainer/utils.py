#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Small utility functions.
"""


Alphabetics = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
Numbers = '0123456789'
Punctuation = """?/,.():;!'"="""
Koch = """KMRSUAPTLOWI.NJE=F0Y,VG5/Q9ZH38B?427C1D6X?():;!"'"""


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


if __name__ == '__main__':
    morse = '.'
    while morse:
        morse = input('Enter morse, nothing to exit: ')
        result = morse2display(morse)
        print(result)
