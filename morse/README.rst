Recognize morse code
====================

The code here is my attempt to decode morse code heard on the
external microphone into English.

Uses python 3.x with pyaudio and numpy.  Run the program and make morse sounds
after the program prints an asterisk:

::

    $ make
    Sound: maximum, ANR off
    python3 morse.py
    *TEST  ^C
    $

The design is described here_.

.. _here: https://github.com/rzzzwilson/morse/blob/master/morse/design.rst


Files
-----

morse.py

::

    The latest production code.

record.py

::

    An example program that records 5 seconds of sound and writes it to a
    .WAV file.  From http://people.csail.mit.edu/hubert/pyaudio/ .

FZGHBQHIMJGBA19.ino

::

    An arduino sketch that decodes morse.  I *think* I got this from
    http://dementedhacker.nl/tag/morse .

test.py

::

    Basic program to sense audio levels.

test2.py

::

    A more sophisticated program to find dots or dashes.

test3.py

::

    Code to try to decode morse single characters.
    Part-way done.  Needs a *lot* of fiddling with sound levels on MacOS.  Still
    injects 'noise' characters.

test4.py

::

    This program steals the initial data handling from gui.py and also decodes
    the sound data in a different way.  Each 32 sample frame is averaged and 
    classified as SOUND or SILENT, with the count of silent/sound samples
    returned.  Later code then decides if we have a DOT, DASH or SILENCE.

gui.py

::

    Example of graphing audio data.

sound_examples/*

::

    Real morse sound files from various sources.  Most useful files are from the
    ARRL code practice site (http://www.arrl.org/code-practice-files).  Various
    other files contain noisy morse that I might try recognizing later.

Example/Ideas Code
------------------

http://flothesof.github.io/pyqt-microphone-fft-application.html

https://healthyalgorithms.com/2013/08/22/dsp-in-python-active-noise-reduction-with-pyaudio/

http://bastibe.de/2012-11-02-real-time-signal-processing-in-python.html


