#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Class to make morse sounds from English characters.  We use a state
machine to send well-formed morse code.

morse = SendMorse()
-------------------

morse.set_speeds(chars_per_minute, words_per_minute)
----------------------------------------------------

morse.set_volume(volume)
------------------------

morse.set_frequency(frequency)
------------------------------

morse.send_morse(string)
------------------------
Send a string of characters.

morse.close()
-------------

"""


import sys
import numpy as np
import pyaudio

import logger
# start the logging
log = logger.Log('send_morse.log', logger.Log.DEBUG)


class SendMorse:

    # the default settings
    DefaultCPM = 10            # character speed (characters per minute)
    DefaultWPM = 5             # word speed (words per minute)
    DefaultVolume = 0.7         # in range [0.0, 1.0]
    DefaultFrequency = 750      # hertz

    # internal settings
    SampleRate = 8000           # samples per second
    Format = pyaudio.paFloat32  # sample must be in range [0.0, 1.0]

    # Words/minute below which we use the Farnsworth timing method
    FarnsworthThreshold = 18

    # dict to translate characters into morse code strings
    Morse = {
             '!': '-.-.--', '"': '.-..-.', '$': '...-..-', '&': '.-...',
             "'": '.----.', '(': '-.--.', ')': '-.--.-', ',': '--..--',
             '-': '-....-', '.': '.-.-.-', '/': '-..-.', ':': '---...',
             ';': '-.-.-.', '=': '-...-', '?': '..--..', '@': '.--.-.',
             '_': '..--.-', '+': '.-.-.',

             '0': '-----', '1': '.----', '2': '..---', '3': '...--',
             '4': '....-', '5': '.....', '6': '-....', '7': '--...',
             '8': '---..', '9': '----.',

             'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
             'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
             'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
             'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
             'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
             'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
             'Y': '-.--', 'Z': '--..'
            }

    # order of learning with the Koch method
    KochOrder = 'KMRSUAPTLOWI.NJE=F0Y,VG5/Q9ZH38B?427C1D6X'


    def __init__(self, volume=DefaultVolume, frequency=DefaultFrequency,
                       cpm=DefaultCPM, wpm=DefaultWPM):
        """Prepare the SendMorse object."""

        # set send params to defaults
        self.cpm = cpm
        self.wpm = wpm
        self.volume = volume
        self.frequency = frequency

        # prepare variables for created sound bites
        self.dot_sound = None
        self.dash_sound = None
        self.dot_silence = None
        self.dash_silence = None
        self.word_silence = None

        # create morse sound samples
        self.create_sounds()

        # prepare the audio device
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self.pyaudio.open(format=SendMorse.Format,
                                        channels=1,
                                        rate=SendMorse.SampleRate,
                                        output=True)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

    def __del__(self):
        self.close()
        print('')

    def create_sounds(self):
        """Create morse sounds from state variables.

        We use the ARRL documentation to set various timings.  Look in
        "Morse_Farnsworth.pdf" for the details.

        The input variables are:
            self.cpm
            self.wpm
            self.frequency
            SendMorse.SampleRate
        """

        dot_duration = 1.2 / self.wpm
        dash_duration = 3 * dot_duration
        word_duration = 7 * dot_duration

        # generate samples, note conversion to float32 array
        dot_data = np.arange(SendMorse.SampleRate*dot_duration)*self.frequency/SendMorse.SampleRate
        dash_data = np.arange(SendMorse.SampleRate*dash_duration)*self.frequency/SendMorse.SampleRate
        silence_data = np.arange(SendMorse.SampleRate*dot_duration)*self.frequency/SendMorse.SampleRate
        char_data = np.arange(SendMorse.SampleRate*dash_duration)*self.frequency/SendMorse.SampleRate
        word_data = np.arange(SendMorse.SampleRate*word_duration)*self.frequency/SendMorse.SampleRate

        self.dot_sound = (np.sin(2*np.pi*dot_data)).astype(np.float32)
        self.dash_sound = (np.sin(2*np.pi*dash_data)).astype(np.float32)
        self.dot_silence = (np.sin(0*silence_data)).astype(np.float32)
        self.dash_silence = (np.sin(0*char_data)).astype(np.float32)
        self.word_silence = (np.sin(0*word_data)).astype(np.float32)

        # then decide if we are going to use Farnsworth
        if self.wpm < SendMorse.FarnsworthThreshold:
            # use Farnsworth timing, as per the ARRL doc
            t_a = 60*self.wpm - 37.2*self.cpm
            t_c = 3*t_a/19
            t_w = 7*t_a/19

            log('create_sounds: t_a=%s' % str(t_a))
            log('create_sounds: t_c=%s' % str(t_c))
            log('create_sounds: t_w=%s' % str(t_w))

            dot_duration += t_c
            dash_duration += t_c
            word_duration + t_w

            log('create_sounds: dot_duration=%s (Farnsworth)' % str(dot_duration))
            log('create_sounds: dash_duration=%s (Farnsworth)' % str(dash_duration))
            log('create_sounds: word_duration=%s (Farnsworth)' % str(word_duration))

        log('create_sounds: len(self.dot_sound)=%d' % len(self.dot_sound))
        log('create_sounds: len(self.dash_sound)=%d' % len(self.dash_sound))
        log('create_sounds: len(self.dot_silence)=%d' % len(self.dot_silence))
        log('create_sounds: len(self.dash_silence)=%d' % len(self.dash_silence))
        log('create_sounds: len(self.word_silence)=%d' % len(self.word_silence))

    def set_speeds(self, cpm=None, wpm=None):
        """Set morse speeds."""

        if cpm or wpm:
            self.cpm = cpm
            self.wpm = wpm
            self.create_sounds()

    def set_volume(self, volume):
        """Set morse volume."""

        self.volume = volume

    def set_frequency(self, frequency):
        """Set tone frequency."""

        self.frequency = frequency
        self.create_sounds()

    def send(self, code):
        """Send characters in 'code' to speakers as morse."""

        for char in code:
            char = char.upper()
            if char == ' ':
                self.stream.write(self.word_silence)
            elif char in SendMorse.Morse:
                code = SendMorse.Morse[char]
                for s in code:
                    if s == '.':
                        self.stream.write(self.volume*self.dot_sound)
                    elif s == '-':
                        self.stream.write(self.volume*self.dash_sound)
                    self.stream.write(self.dot_silence)
            else:
                log("Unrecognized character '%s' in morse to send" % char)

            self.stream.write(self.word_silence)


if __name__ == '__main__':
    import sys
    import os
    import getopt

    # get program name from sys.argv
    prog_name = sys.argv[0]
    if prog_name.endswith('.py'):
        prog_name = prog_name[:-3]

    def usage(msg=None):
        if msg:
            print(('*'*80 + '\n%s\n' + '*'*80) % msg)
        print("\n"
              "CLI program to send morse strings from CLI input.\n\n"
              "Usage: send_morse [-h]\n\n"
              "where -h  means priont this help and stop")


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

    while True:
        try:
            code = input('>')
        except EOFError:
            sys.exit(0)
        if not code:
            break
        morse.send(code)
