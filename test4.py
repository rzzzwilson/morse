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
    SIGNAL = 5000

    # no SOUND for this time is SILENCE
    SILENCE = 30

    # hang time before silence is noticed
    HOLD = 2

    state = S_SILENCE
    hold = HOLD

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        data = np.fromstring(data, 'int16')
        data = [abs(x) for x in data]
        value = sum(data) // len(data)      # average value
#        if value >= SIGNAL:
#            log('get_sample: value=%d, SIGNAL=%d\t\t%s' % (value, SIGNAL, '********' if value >= SIGNAL else ''))

        if state == S_SILENCE:
            if value < SIGNAL:
                count += 1
#                log('get_sample: continuing SILENCE')
                if count >= SILENCE:
                    return -count
            else:
                # we have a signal, change to SOUND state
#                log('get_sample: start of SOUND')
                state = S_SOUND
                count = 0
        else:
            # in SOUND state
            if value < SIGNAL:
                hold -= 1
                if hold <= 0:
                    # silence at the end of a SOUND period
                    # return SOUND result
#                    log('get_sample: SILENCE after SOUND, send SOUND result')
                    return count
            else:
                hold = HOLD
                count += 1
#                log('get_sample: continuing SOUND, count')

def read_morse(stream):
    """Read Morse data from 'stream' and decode into English."""

    # lengths of various things, most of this is dynamic
    DOT_LENGTH = 7
    DASH_LENGTH = DOT_LENGTH * 3
    CHAR_SPACE = (DOT_LENGTH * 3) // 30
    WORD_SPACE = (DOT_LENGTH * 7) // 30
    DOT_DASH = (DOT_LENGTH + DASH_LENGTH)//2       # threshold between dot & dash
    log('read_morse: DASH_LENGTH=%d, DOT_LENGTH=%d, DOT_DASH=%d, CHAR_SPACE=%d, WORD_SPACE=%d'
        % (DASH_LENGTH, DOT_LENGTH, DOT_DASH, CHAR_SPACE, WORD_SPACE))

    space_count = 0
    morse = ''
    sent_space = False
    sent_word_space = False

    emit_char('*')      # show we are ready to go

    while True:
        sample = get_sample(stream)
        log('read_morse: sample=%s' % str(sample))

        if sample > 0:
            if sample < 3:
                continue
            # got a sound, dot or dash?
            if sample > DOT_DASH:
                morse += '-'
                DASH_LENGTH = (DASH_LENGTH + sample) // 2
                log('got -')
            else:
                morse += '.'
                DOT_LENGTH = (DOT_LENGTH + sample) // 2
                log('got .')
            DOT_DASH = (DOT_LENGTH + DASH_LENGTH) // 2
            CHAR_SPACE = (DOT_LENGTH * 3) // 30
            WORD_SPACE = (DOT_LENGTH * 7) // 30
            sent_space = False
            log('read_morse: DASH_LENGTH=%d, DOT_LENGTH=%d, DOT_DASH=%d, CHAR_SPACE=%d, WORD_SPACE=%d'
                % (DASH_LENGTH, DOT_LENGTH, DOT_DASH, CHAR_SPACE, WORD_SPACE))
        else:
            # got a silence, bump silence counter
            space_count += 1
            log('read_morse: space_count=%d, CHAR_SPACE=%d, WORD_SPACE=%d'
                % (space_count, CHAR_SPACE, WORD_SPACE))

            # if silence long enough, emit a space
            if space_count > CHAR_SPACE:
                if morse:
                    decode = decode_morse(morse)
                    log('Morse: %s (%s)' % (morse, decode))
                    morse = ''
                    space_count = 0
                else:
                    if not sent_space:
                        space_count = 0
                        emit_char(' ')
                        sent_space = True
            if space_count > WORD_SPACE:
                if not sent_word_space:
                    space_count = 0
                    emit_char(' ')
                    sent_word_space = True


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

