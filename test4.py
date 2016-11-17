#!/bin/env python3

from __future__ import print_function
import sys
import logger
try:
    import pyaudio
except ImportError:
    print('You have to do "workon pyopengl" first.')
    sys.exit(10)
import time
import struct
import math
import numpy as np


#CHUNK = 1024
CHUNK = 32
#FORMAT = pyaudio.paFloat32
#FORMAT = pyaudio.paInt32
FORMAT = pyaudio.paInt16
CHANNELS = 1
#RATE = 14400
RATE = 5000
SHORT_NORMALIZE = (1.0 / 32768.0)

DOT_DASH = 70

MaxBucket = 32

SILENCE = 10

Morse = {
         '.-': 'A',
         '-...': 'B',
         '-.-.': 'C',
         '-..': 'D',
         '.': 'E',
         '..-.': 'F',
         '--.': 'G',
         '....': 'H',
         '..': 'I',
         '.---': 'J',
         '-.-': 'K',
         '.-..': 'L',
         '--': 'M',
         '-.': 'N',
         '---': 'O',
         '.--.': 'P',
         '--.-': 'Q',
         '.-.': 'R',
         '...': 'S',
         '-': 'T',
         '..-': 'U',
         '...-': 'V',
         '.--': 'W',
         '-..-': 'X',
         '-.--': 'Y',
         '--..': 'Z',
         '.----': '1',
         '..---': '2',
         '...--': '3',
         '....-': '4',
         '.....': '5',
         '-....': '6',
         '--...': '7',
         '---..': '8',
         '----.': '9',
         '-----': '0',
         '.-.-.-': '.',
         '--..--': ',',
         '..--..': '?',
         '.----.': '\'',
         '-.-.--': '!',
         '-..-.': '/',
         '-.--.': '(',
         '-.--.-': ')',
         '.-...': '&',
         '---...': ':',
         '-.-.-.': ';',
         '-...-': '=',
         '-....-': '-',
         '..--.-': '_',
         '.-..-.': '"',
         '...-..-': '$',
         '.--.-.': '@',
        }


#def movingaverage(interval, window_size):
#    window = np.ones(int(window_size))/float(window_size)
#    return np.convolve(interval, window, 'same')

def emit_char(char):
    """Send character to output 'raw'."""

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
    SIGNAL = 10000

    # hang time before silence is noticed
    HOLD = 7

    state = S_SILENCE
    hold = HOLD

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        data = np.fromstring(data, 'int16')
        data = [abs(x) for x in data]
        value = sum(data) // len(data)      # average value
#        log('get_sample: value=%d, SIGNAL=%d' % (value, SIGNAL))

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

    MIN_DOT_LENGTH = 3
    DOT_LENGTH = 10
    DASH_LENGTH = DOT_LENGTH * 3

    DOT_DASH = 30       # threshold between dot & dash

    ELEM_LENGTH = DOT_LENGTH
    CHAR_SPACE = DOT_LENGTH * 3
    WORD_SPACE = DOT_LENGTH * 7

    SPACE_LENGTH = 3
    space_count = 0
    morse = ''
    sent_space = False

    emit_char('*')

    while True:
        sample = get_sample(stream)
        log('read_morse: sample=%s' % str(sample))

        if sample > 0:
            if sample <= MIN_DOT_LENGTH:
                continue
            # got a dot or dash
            if sample > DOT_DASH:
                morse += '-'
            else:
                morse += '.'
            sent_space = False
        else:
            # got a silence, bump silence counter
            space_count += 1

            # if silence long enough, emit a space
            if space_count > SPACE_LENGTH:
                if morse:
                    decode = decode_morse(morse)
                    log('Morse: %s (%s)' % (morse, decode))
                    morse = ''
                else:
                    if not sent_space:
                        space_count = 0
                        emit_char(' ')
                        sent_space = True


log = logger.Log('test4.log', logger.Log.DEBUG)

p = pyaudio.PyAudio()

morse = p.open(format=FORMAT,
               channels=CHANNELS,
               rate=RATE,
               input=True,
               frames_per_buffer=CHUNK)

read_morse(morse)

morse.stop_stream()
morse.close()
p.terminate()

