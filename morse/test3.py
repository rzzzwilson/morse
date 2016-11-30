#!/bin/env python

from __future__ import print_function
import sys
import logger
try:
    import pyaudio
except ImportError:
    print('You have to do "workon pyopengl" first.')
    sys.exit(10)
import wave
import time
import struct
import math

HOLD = 7
#CHUNK = 1024
CHUNK = 32
FORMAT = pyaudio.paInt16
#FORMAT = pyaudio.paInt32
CHANNELS = 1
#RATE = 14400
RATE = 5000
SHORT_NORMALIZE = (1.0 / 32768.0)

DOT_DASH = 70

MaxBucket = 32

SILENCE = 200

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


def decodeMorse(morse):
    try:
        char = Morse[morse]
    except KeyError:
        char = u'\u00bf' + '<%s>' % morse
    print(char, end='')
    sys.stdout.flush()

def getLevel(frame):
    count = len(frame) / 2
    format = '%dh' % count
    shorts = struct.unpack(format, frame)

    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n * n
    rms = math.pow(sum_squares/count, 0.5)
    return rms * 1000.0

def getSample(stream):
    samples = []
    count = 0

    SIGNAL = 80

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        value = getLevel(data)
        samples.append(value)
        if value < SIGNAL:
            count += 1
            if count > SILENCE:
                return samples
        else:
            count = 0

def readMorse(stream):
    last_floor = [10, 10, 10, 10]
    last_floor_len = len(last_floor)
    while True:
        log('?????')
        samples = getSample(stream)

        # dump samples
        avg = int(sum(samples) / len(samples))
        top = max(samples)
        bot = min(samples)
        delta = top - bot
        bucket_size = (delta) / MaxBucket
        last_floor.append(bot)
        last_floor = last_floor[1:]
        avg_floor = int(sum(last_floor) / last_floor_len)
        #threshold = avg_floor + (top - bot)/2
        threshold = avg + (delta)/4
        log('avg=%d, top=%d, bot=%d, threshold=%d, last_floor=%s' % (avg, top, bot, threshold, str(last_floor)))

        state = False
        count = 0
        hold = HOLD
        morse = ''
        samples = [int(x) for x in samples]
        values = ['*' if x > threshold else x for x in samples]
        log('samples: %s' % str(samples))
        log('values: %s' % str(values))
        for s in samples:
            bucket = int(s / bucket_size)
            if bucket >= MaxBucket:
                bucket = MaxBucket - 1
            s_state = (bucket > threshold)
            if s_state == state:
                count += 1
                hold = HOLD
            else:
                hold -= 1
                if hold <= 0:
                    if state and count > 3:
                        morse += '.' if count < DOT_DASH else '-'
                    hold = HOLD
                    count = 1
                    state = s_state

        if morse:
            log('Morse: %s' % morse)
            decodeMorse(morse)

log = logger.Log('test3.log', logger.Log.DEBUG)

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

readMorse(stream)

stream.stop_stream()
stream.close()
p.terminate()

