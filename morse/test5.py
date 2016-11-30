#!/bin/env python3

"""
Program to read morse sounds from the internal microphone and print
the English characters.  The program attempts to read dynamic parameters
from the default JSON file ({progname}.json).

Usage:  {progname}.py [-f <params_file>] [-h] [-n]

where -f <params_file> means read params from the given file
      -h               means print this help and stop
      -n               means don't read any params JSON file
"""


import_errors = False

import sys
import json
import getopt
import logger

try:
    import pyaudio
except ImportError:
    print("Can't import 'pyaudio'")
    import_errors = True

try:
    import numpy as np
except ImportError:
    print("Can't import 'numpy'")
    import_errors = True

if import_errors:
    sys.exit(10)


# get program name from sys.argv
ProgName = sys.argv[0]
if ProgName.endswith('.py'):
    ProgName = ProgName[:-3]

# path to file holding morse recognition parameters
ParamsFile = '%s.json' % ProgName

# name of the file to log to
LogFile = '%s.log' % ProgName

CHUNK = 16
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000

# lengths of various things (set for my slow speed!)
# most of this is dynamic and loaded/saved in ParamsFile
LenDot = 30
LenDash = LenDot * 3
DotDashThreshold = (LenDot + LenDash)//2       # threshold between dot & dash

MaxSignal = 30000
MinSignalX = 500
SignalThreshold = 10000

# lower sampling rate counters
CharSpace = 3      # number of silences indicates a space
WordSpace = 9      # number of silences to end word

# dict to translate morse code to English chars
Morse = {
         '.-':      'A',
         '-...':    'B',
         '-.-.':    'C',
         '-..':     'D',
         '.':       'E',
         '..-.':    'F',
         '--.':     'G',
         '....':    'H',
         '..':      'I',
         '.---':    'J',
         '-.-':     'K',
         '.-..':    'L',
         '--':      'M',
         '-.':      'N',
         '---':     'O',
         '.--.':    'P',
         '--.-':    'Q',
         '.-.':     'R',
         '...':     'S',
         '-':       'T',
         '..-':     'U',
         '...-':    'V',
         '.--':     'W',
         '-..-':    'X',
         '-.--':    'Y',
         '--..':    'Z',
         '.----':   '1',
         '..---':   '2',
         '...--':   '3',
         '....-':   '4',
         '.....':   '5',
         '-....':   '6',
         '--...':   '7',
         '---..':   '8',
         '----.':   '9',
         '-----':   '0',
         '.-.-.-':  '.',
         '--..--':  ',',
         '..--..':  '?',
         '.----.':  '\'',
         '-.-.--':  '!',
         '-..-.':   '/',
         '-.--.':   '(',
         '-.--.-':  ')',
         '.-...':   '&',
         '---...':  ':',
         '-.-.-.':  ';',
         '-...-':   '=',
         '-....-':  '-',
         '..--.-':  '_',
         '.-..-.':  '"',
         '...-..-': '$',
         '.--.-.':  '@',
        }


def save_params(path):
    """Save recognition params to file."""

    data_dict = {'LenDot': LenDot,
                 'LenDash': LenDash,
                 'DotDashThreshold': DotDashThreshold,
                 'CharSpace': CharSpace,
                 'WordSpace': WordSpace,
                 'MaxSignal': MaxSignal,
                 'MinSignalX': MinSignalX,
                 'SignalThreshold': SignalThreshold
                 }

    log('Saving params in file %s:\n%s' % (path, str(data_dict)))

    json_str = json.dumps(data_dict)

    with open(path, 'w') as fd:
        fd.write(json_str)

def load_params(path):
    """Load recognition params from file, if it exists."""

    global LenDot, LenDash, DotDashThreshold
    global CharSpace, WordSpace
    global MaxSignal, MinSignalX, SignalThreshold

    try:
        with open(path, 'r') as fd:
            data = json.load(fd)
    except FileNotFoundError:
        return

    try:
        LenDot = data['LenDot']
        LenDash = data['LenDash']
        DotDashThreshold = data['DotDashThreshold']
        CharSpace = data['CharSpace']
        WordSpace = data['WordSpace']
        MaxSignal = data['MaxSignal']
        MinSignalX = data['MinSignalX']
        SignalThreshold = data['SignalThreshold']
    except KeyError:
        print('Invalid data in JSON file %s' % path)
        sys.exit(1)

def emit_char(char):
    """Send character to output without newline."""

    print(char, end='')
    sys.stdout.flush()

def decode_morse(morse):
    """Decode morse code and send character to output.

    Also return the decode character.
    """

    try:
        char = Morse[morse]
    except KeyError:
        char = u'\u00bf' + '<%s>' % morse
    print(char, end='')
    sys.stdout.flush()
    return char

def get_sample(stream):
    """Return a sample number that indicates sound or silence.

    Returned values are:
        -N  silence for N samples
        N   N samples of sound (terminated by silence)
    """

    # state values
    S_SOUND = 1
    S_SILENCE = 2

    # count of silence or sound time
    count = 0

    # no SOUND for this time is SILENCE
    SILENCE = 20

    # hang time before silence is noticed
    HOLD = 2

    state = S_SILENCE
    hold = HOLD

    values = []

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        data = np.fromstring(data, 'int16')
        data = [abs(x) for x in data]
        value = int(sum(data) // len(data))      # average value
        values.append(value)

        if state == S_SILENCE:
            # in SILENCE state
            if value < SignalThreshold:
                count += 1
                if count >= SILENCE:
                    return (-count, sum(values) // len(values))
            else:
                # we have a signal, change to SOUND state
                state = S_SOUND
                count = 0
                values = []     # start value samples fresh
        else:
            # in SOUND state
            if value < SignalThreshold:
                hold -= 1
                if hold <= 0:
                    # silence at the end of a SOUND period
                    # return SOUND result
                    return (count, sum(values) // len(values))
            else:
                hold = HOLD
                count += 1

def read_morse(stream):
    """Read Morse data from 'stream' and decode into English."""

    global LenDot, LenDash, DotDashThreshold, CharSpace, WordSpace
    global MaxSignal, MinSignalX, SignalThreshold

    log('read_morse: LenDot=%d, LenDash=%d, DotDashThreshold=%d, CharSpace=%d, WordSpace=%d'
        % (LenDot, LenDash, DotDashThreshold, CharSpace, WordSpace))

    space_count = 0
    word_count = 0
    morse = ''
    sent_space = True
    sent_word_space = True

    emit_char('*')      # show we are ready to go

    while True:
        (count, level) = get_sample(stream)
        log('count=%d, level=%d, space_count=%d, word_count=%d'
            % (count, level, space_count, word_count))

        if count > 0:
            MaxSignal = level
            if count < 3:
                log('got short sound, count=%d' % count)
                continue
            sent_word_space = False
            # got a sound, dot or dash?
            if count > DotDashThreshold:
                morse += '-'
                LenDash = (LenDash*2 + count) // 3
                log('got -')
            else:
                morse += '.'
                LenDot = (LenDot*2 + count) // 3
                log('got .')
            DotDashThreshold = (LenDot + LenDash) // 2
#            CharSpace = 2
#            WordSpace = 6
            sent_space = False
            space_count = 0
            word_count = 0
        else:
            # got a silence, bump silence counters & capture minimum
            space_count += 1
            word_count += 1
            MinSignalX = level

            # if silence long enough, emit a space
            if space_count >= CharSpace:
                space_count = 0
                if morse:
                    decode = decode_morse(morse)
                    log('Morse: %s (%s)' % (morse, decode))
                    morse = ''
                    log('modified: LenDot=%d, LenDash=%d, DotDashThreshold=%d, CharSpace=%d, WordSpace=%d'
                        % (LenDot, LenDash, DotDashThreshold, CharSpace, WordSpace))
                    word_count = 0
                elif not sent_space:
                    emit_char(' ')
                    sent_space = True

            if word_count >= WordSpace:
                if not sent_word_space:
                    emit_char(' ')
                    sent_word_space = True
                word_count = 0

        # set new signal threshold
        SignalThreshold = (MinSignalX + 2*MaxSignal)//3

        log('LenDot=%d, LenDash=%d, DotDashThreshold=%d, CharSpace=%d, WordSpace=%d'
            % (LenDot, LenDash, DotDashThreshold, CharSpace, WordSpace))

def usage(msg=None):
    if msg:
        print(('*'*80 + '\n%s\n' + '*'*80) % msg)
    print(__doc__.format(progname=ProgName))


# start the logging
log = logger.Log(LogFile, logger.Log.DEBUG)

# parse the CLI params
argv = sys.argv[1:]

try:
    (opts, args) = getopt.getopt(argv, 'f:hn', ['file=', 'help', 'noparams'])
except getopt.GetoptError as err:
    usage(err)
    sys.exit(1)

params_file = ParamsFile
for (opt, param) in opts:
    if opt in ['-f', '--file']:
        params_file = param
    elif opt in ['-h', '--help']:
        usage()
        sys.exit(0)
    elif opt in ['-n', '--noparams']:
        params_file = None

if params_file:
    load_params(params_file)

p = pyaudio.PyAudio()

morse = p.open(format=FORMAT,
               channels=CHANNELS,
               rate=RATE,
               input=True,
               frames_per_buffer=CHUNK)
try:
    read_morse(morse)
except KeyboardInterrupt:
    pass

save_params(ParamsFile)

morse.stop_stream()
morse.close()
p.terminate()

