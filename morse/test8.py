#!/bin/env python3

"""
Generate morse sounds without using numpy.
"""

import math
import time
import pyaudio

#sudo apt-get install python-pyaudio
PyAudio = pyaudio.PyAudio

#See http://en.wikipedia.org/wiki/Bit_rate#Audio
BITRATE = 22050 #number of frames per second/frameset.

#See http://www.phy.mtu.edu/~suits/notefreqs.html
FREQUENCY = 700.00 #Hz, waves per second, 261.63=C4-note.
LENGTH = 10.0000 #seconds to play sound

NUMBEROFFRAMES = int(BITRATE * LENGTH)
RESTFRAMES = NUMBEROFFRAMES % BITRATE

start = time.time()

WAVEDATA = ''
for x in range(NUMBEROFFRAMES):
    WAVEDATA = WAVEDATA+chr(int(math.sin(x/((BITRATE/FREQUENCY)/math.pi))*127+128))

delta = time.time() - start
print('time=%f' % delta)

p = PyAudio()
stream = p.open(format = p.get_format_from_width(1),
                channels = 1,
                rate = BITRATE,
                output = True)
stream.write(WAVEDATA)
stream.stop_stream()
stream.close()
p.terminate()
