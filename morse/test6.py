#!/bin/env python3

"""
Generate mpprse sounds without using numpy.
"""

from struct import pack
from math import sin, pi
import wave

SampleRate = 44100
Frequency = 500
Duration = 3
MaximumVolume = 2**15-1.0

wv = wave.open('test_mono.wav', 'w')
wv.setparams((1, 2, SampleRate, 0, 'NONE', 'not compressed'))
wvData = b""
for i in range(0, SampleRate*Duration):
    wvData += pack('h', round(MaximumVolume * sin(i*2*pi*Frequency/SampleRate)))
wv.writeframes(wvData)
wv.close()
