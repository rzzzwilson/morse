#!/bin/env python3

"""
Program to read morse sounds from the internal microphone and print
the English characters.

Usage:  morse.py [-x]

where the -x option means don't read the params JSON file
"""


import_errors = False

import sys
import json

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


# path to file holding morse recognition parameters
PARAMS_FILE = 'morse_params.json'

CHUNK = 16
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000

# lengths of various things
# most of this is dynamic and loaded/saved in PARAMS_FILE
DOT_LENGTH = 19
DASH_LENGTH = DOT_LENGTH * 3
DOT_DASH = (DOT_LENGTH + DASH_LENGTH)//2       # threshold between dot & dash

# lower sampling rate counters
CHAR_SPACE = 2      # number of silences indicates a space
WORD_SPACE = 8      # number of silences to end word

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

    data_dict = {'DOT_LENGTH': DOT_LENGTH,
                 'DASH_LENGTH': DASH_LENGTH,
                 'DOT_DASH': DOT_DASH,
                 'CHAR_SPACE': CHAR_SPACE,
                 'WORD_SPACE': WORD_SPACE}
    json_str = json.dumps(data_dict)

    with open(path, 'w') as fd:
        fd.write(json_str)

def load_params(path):
    """Load recognition params from file, if it exists."""

    global DOT_LENGTH, DASH_LENGTH, DOT_DASH, CHAR_SPACE, WORD_SPACE

    try:
        with open(path, 'r') as fd:
            data = json.load(fd)
    except FileNotFoundError:
        return

    try:
        DOT_LENGTH = data['DOT_LENGTH']
        DASH_LENGTH = data['DASH_LENGTH']
        DOT_DASH = data['DOT_DASH']
        CHAR_SPACE = data['CHAR_SPACE']
        WORD_SPACE = data['WORD_SPACE']
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

    # signal threshold, should be dynamic
    SIGNAL = 5000

    # no SOUND for this time is SILENCE
    SILENCE = 20

    # hang time before silence is noticed
    HOLD = 2

    state = S_SILENCE
    hold = HOLD

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        data = np.fromstring(data, 'int16')
        data = [abs(x) for x in data]
        value = sum(data) // len(data)      # average value

        if state == S_SILENCE:
            if value < SIGNAL:
                count += 1
                if count >= SILENCE:
                    return -count
            else:
                # we have a signal, change to SOUND state
                state = S_SOUND
                count = 0
        else:
            # in SOUND state
            if value < SIGNAL:
                hold -= 1
                if hold <= 0:
                    # silence at the end of a SOUND period
                    # return SOUND result
                    return count
            else:
                hold = HOLD
                count += 1

def read_morse(stream):
    """Read Morse data from 'stream' and decode into English."""

    global DOT_LENGTH, DASH_LENGTH, DOT_DASH, CHAR_SPACE, WORD_SPACE

    space_count = 0
    word_count = 0
    morse = ''
    sent_space = True
    sent_word_space = True

    emit_char('*')      # show we are ready to go

    while True:
        sample = get_sample(stream)

        if sample > 0:
            if sample < 3:
                continue
            sent_word_space = False
            # got a sound, dot or dash?
            if sample > DOT_DASH:
                morse += '-'
                DASH_LENGTH = (DASH_LENGTH*2 + sample) // 3
            else:
                morse += '.'
                DOT_LENGTH = (DOT_LENGTH*2 + sample) // 3
            DOT_DASH = (DOT_LENGTH + DASH_LENGTH) // 2
            #CHAR_SPACE = DOT_LENGTH * 3
            #WORD_SPACE = DOT_LENGTH * 7
            CHAR_SPACE = 2
            WORD_SPACE = 6
            sent_space = False
            space_count = 0
            word_count = 0
        else:
            # got a silence, bump silence counters
            space_count += 1
            word_count += 1

            # if silence long enough, emit a space
            if space_count >= CHAR_SPACE:
                space_count = 0
                if morse:
                    decode = decode_morse(morse)
                    morse = ''
                    word_count = 0
                elif not sent_space:
                    emit_char(' ')
                    sent_space = True

            if word_count >= WORD_SPACE:
                if not sent_word_space:
                    emit_char(' ')
                    sent_word_space = True
                word_count = 0

if not '-x' in sys.argv[1:]:
    load_params(PARAMS_FILE)

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

save_params(PARAMS_FILE)

morse.stop_stream()
morse.close()
p.terminate()

