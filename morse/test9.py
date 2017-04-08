#!/bin/env python3

"""
Generate morse sounds without using numpy.
"""

import math
import struct
import pyaudio
import time

SampleRate = 14400
MaxValue = 2**7 // 2

def make_tone(frequency=700, duration=1, sample_rate=SampleRate, volume=0.5):
    # get number of samples in one tone cycle, create one cycle of sound
    num_cycle_samples = sample_rate // frequency
    cycle = []
    for n in range(num_cycle_samples):
        value = int((math.sin(2*math.pi*n/num_cycle_samples)*MaxValue + MaxValue) * volume)
        cycle.append(value)

    # make complete tone
    data = []
    for _ in range(frequency * duration):
        data.extend(cycle)
    tone = bytes(bytearray(data))

    return tone

if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt8, channels=1, rate=SampleRate, output=1)
    start = time.time()
    tone = make_tone(duration=1)
    delta = time.time() - start
    print('delta=%f' % delta)
    stream.write(tone)
    stream.close()
    p.terminate()
