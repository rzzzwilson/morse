#!/bin/env python3

"""
Generate morse sounds without using numpy.
"""

import math
import random
import struct
import pyaudio
import time

SampleRate = 14400
MaxValue = 2**7 // 2
LeadInOutCycles = 3

def make_tone(frequency=700, duration=1, sample_rate=SampleRate, volume=0.5):
    # get number of samples in one tone cycle, create one cycle of sound
    num_cycle_samples = sample_rate // frequency
    cycle = []
    for n in range(num_cycle_samples):
        value = int((math.sin(2*math.pi*n/num_cycle_samples)*MaxValue + MaxValue) * volume)
        cycle.append(value)

    # generate some noise
    noise = []
    for _ in range(num_cycle_samples):
        noise.append(int(random.random()*MaxValue*volume))

    cycle = noise

    # make complete tone
    data = []
    for _ in range(int(frequency * duration)):
        data.extend(cycle)

    # add lead-in and lead-out
    lead_samples = num_cycle_samples*LeadInOutCycles
    for i in range(lead_samples):
        data[i] = int(data[i] * i/lead_samples)
        data[-i] = int(data[-i] * i/lead_samples)

    tone = bytes(bytearray(data))
    return tone


if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt8, channels=1, rate=SampleRate, output=1)
    dash = make_tone(duration=0.3)
    dot = make_tone(duration=0.1)
    silence = make_tone(duration=0.1, volume=0.0)
    stream.write(dot+silence+dash+silence+dot+silence+dash+silence+silence+silence)
    stream.stop_stream()
    stream.close()
    p.terminate()
