Recognize morse code
====================

The code here is my attempt to decode morse code heard on the
external microphone into English.

Uses python 2.x and pyaudio.

Files
-----

record.py

::

    An example program that records 5 seconds of sound and writes it to a
    .WAV file.  From http://people.csail.mit.edu/hubert/pyaudio/ .

test20db.wav

::

    A recording of fast, noisy morse.  If the software gets good try to decode!

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

    ?

gui.py

::

    Example of graphing audio data.

sound_examples/*

::

    Morse audio files from http://www.learnmorsecode.com and other places.
