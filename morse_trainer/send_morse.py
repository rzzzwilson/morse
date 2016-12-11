#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Class to make morse sounds from English characters.  We use a state
machine to send well-formed morse code.

morse = SendMorse()
-------------------

morse.set_speeds(chars_per_minute, words_per_minute)
----------------------------------------------------

(cwpm, wpm) = morse.get_speeds()
-------------------------------

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
import math
import numpy as np
import pyaudio


class SendMorse:

    # the default settings
    DefaultCWPM = 10             # character speed (characters per minute)
    DefaultWPM = 5              # word speed (words per minute)
    DefaultVolume = 0.7         # in range [0.0, 1.0]
    DefaultFrequency = 750      # hertz

    # internal settings
    SampleRate = 44000          # samples per second
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
                       cwpm=DefaultCWPM, wpm=DefaultWPM):
        """Prepare the SendMorse object."""

        # set send params to defaults
        self.cwpm = cwpm            # the character word speed
        self.wpm = wpm              # the word speed
        self.volume = volume        # volume
        self.frequency = frequency  # audio frequency

        # prepare variables for created sound bites
        self.dot_sound = None
        self.dash_sound = None
        self.inter_element_silence = None
        self.inter_char_silence = None
        self.inter_word_silence = None

        # create sounds at default speeds
        #self.create_one_cycle()
        self.create_sounds()

        # prepare the audio device
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self.pyaudio.open(format=SendMorse.Format,
                                        channels=1,
                                        rate=SendMorse.SampleRate,
                                        #frames_per_buffer=len(self.one_cycle),
                                        output=True)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

    def __del__(self):
        print('')

    def make_tone(self, duration, volume):
        """Create a strin full of sinewave data.

        Code modified from:
            http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
        """

        def sine(frequency, duration, sample_rate):
            length = int(duration * sample_rate)
            factor = float(frequency) * (math.pi * 2) / sample_rate
            return np.sin(np.arange(length) * factor)

        chunks = []
        chunks.append(sine(self.frequency, duration, SendMorse.SampleRate))
        chunk = np.concatenate(chunks) * volume
        return chunk.astype(np.float32).tostring()

    def farnsworth_times(self, cwpm, wpm):
        """Calculate Farnsworth spacing.

        cwpm  character speed, words/minute
        wpm   overall speed, words/minute

        Returns (dot_time, stretched_dot_time) times (in seconds).
        The 'stretched_dot_time' is used to calculate the inter-char and
        inter_word spacings in Farnsworth mode.
        """

        dot_time = (1.2 / cwpm)
        word_time_cwpm = 60 / cwpm
        word_time_wpm = 60 / wpm

        delta_per_word = word_time_wpm - word_time_cwpm
        stretched_dot_time = dot_time + delta_per_word/19

        return (dot_time, stretched_dot_time)

    def create_sounds(self):
        """Create morse sounds from state variables.

        We use the ARRL documentation to set various timings.  Look in
        "Morse_Farnsworth.pdf" for the details.  NOTE: didn't actually
        use the data in that document as I couldn't make it work.  The
        spacing is calculated from first principles below.

        The input variables are:
            self.cwpm
            self.wpm
            self.frequency
            SendMorse.SampleRate
        """

        # calculate dot and dash times, normal and Farnsworth
        (dot_time, dot_time_f) = self.farnsworth_times(self.cwpm, self.wpm)

        dash_time = 3 * dot_time
        inter_elem_time = dot_time
        inter_char_time = 3 * dot_time
        inter_word_time = 7 * dot_time

        if self.wpm < SendMorse.FarnsworthThreshold:
            # if using Farnsworth, stretch inter char/word times
            inter_char_time = 3 * dot_time_f
            inter_word_time = 7 * dot_time_f

        self.dot_sound = self.make_tone(dot_time, volume=self.volume)
        self.dash_sound = self.make_tone(dash_time, volume=self.volume)
        self.inter_element_silence = self.make_tone(inter_elem_time, volume=0.0)
        self.inter_char_silence = self.make_tone(inter_char_time, volume=0.0)
        self.inter_word_silence = self.make_tone(inter_word_time, volume=0.0)

    def set_speeds(self, cwpm=None, wpm=None):
        """Set morse speeds."""

        if cwpm or wpm:
            self.cwpm = cwpm
            self.wpm = wpm
            self.create_sounds()

    def get_speeds(self):
        """Get morse speeds."""

        return (self.cwpm, self.wpm)

    def set_volume(self, volume):
        """Set morse volume."""

        self.volume = volume
        self.create_sounds()

    def set_frequency(self, frequency):
        """Set tone frequency."""

        self.frequency = frequency
        self.create_sounds()

    def send(self, code):
        """Send characters in 'code' to speakers as morse."""

        # if, by some mischance we haven't created the sounds, do it now
        if self.dot_sound is None:
            self.create_sounds()

       # send the morse
        for char in code:
            char = char.upper()
            if char == ' ':
                self.stream.write(self.inter_word_silence)
            elif char in SendMorse.Morse:
                code = SendMorse.Morse[char]
                for s in code:
                    if s == '.':
                        self.stream.write(self.dot_sound)
                    elif s == '-':
                        self.stream.write(self.dash_sound)
                    self.stream.write(self.inter_element_silence)
            else:
                print("Unrecognized character '%s' in morse to send" % char)

            self.stream.write(self.inter_word_silence)


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
