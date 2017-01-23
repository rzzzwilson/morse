#!/bin/env python3

"""
Generate moprse sounds without using numpy.
"""

import math
import time
from struct import pack

from pyaudio import PyAudio

SampleRate = 22050


def sine_tone(frequency, duration, volume=0.5, sample_rate=22050):
    n_samples = int(sample_rate * duration)
    print('n_samples=%s' % str(n_samples))

    s = lambda t: volume * math.sin(2 * math.pi * frequency * t / sample_rate)
    samples = (int(s(t) * 0x7f + 0x80) for t in range(n_samples))

    buff = b""
    for buf in zip(*[samples]*sample_rate):             # write several samples at a time
        buff += bytes(bytearray(buf))

    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(1),  # 8 bit
                    channels=1,                         # mono
                    rate=SampleRate,
                    output=True)
    stream.write(buff)
    stream.stop_stream()
    stream.close()
    p.terminate()

    return buff

dot = sine_tone(frequency=1000.0,
                duration=0.2,
                volume=0.50,
                sample_rate=SampleRate)

silence = sine_tone(frequency=1000.0,
                    duration=0.2,
                    volume=0.00,
                    sample_rate=SampleRate)

dash = sine_tone(frequency=1000.0,
                 duration=0.6,
                 volume=0.50,
                 sample_rate=SampleRate)

p = PyAudio()
stream = p.open(format=p.get_format_from_width(1),  # 8 bit
                channels=1,                         # mono
                rate=SampleRate,
                output=True)

stream.write(dot)
print('.', end="")
stream.write(silence)
stream.write(dash)
print('_')

stream.stop_stream()
stream.close()
p.terminate()
