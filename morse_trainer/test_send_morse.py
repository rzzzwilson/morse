#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the 'send_morse' module.
"""

import sys
import os
import getopt
from send_morse import SendMorse


# get program name from sys.argv
prog_name = sys.argv[0]
if prog_name.endswith('.py'):
    prog_name = prog_name[:-3]

def usage(msg=None):
    if msg:
        print(('*'*80 + '\n%s\n' + '*'*80) % msg)
    print("\n"
          "CLI program to send morse strings from CLI input.\n\n"
          "Usage: %s [-h]\n\n"
          "where -h  means priont this help and stop" % prog_name)


# parse the CLI params
argv = sys.argv[1:]

try:
    (opts, args) = getopt.getopt(argv, 'h', ['help'])
except getopt.GetoptError as err:
    usage(err)
    sys.exit(1)

for (opt, param) in opts:
    if opt in ['-h', '--help']:
        usage()
        sys.exit(0)

morse = SendMorse()
cwpm = 25
wpm = 15
morse.set_speeds(cwpm=cwpm, wpm=wpm)

(cwpm, wpm) = morse.get_speeds()
prompt = '%d/%d> ' % (cwpm, wpm)

while True:
    try:
        code = input(prompt)
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)

    if not code:
        break
    morse.send(code)
