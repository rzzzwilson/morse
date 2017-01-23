import math
import numpy
import pyaudio


def sine(frequency, length, rate):
    length = int(length * rate)
    factor = float(frequency) * (math.pi * 2) / rate
    return numpy.sin(numpy.arange(length) * factor)


def play_tone(stream, frequency=440, length=1, rate=44100, volume=0.25):
    chunks = []
    chunks.append(sine(frequency, length, rate))

    chunk = numpy.concatenate(chunks) * volume

    stream.write(chunk.astype(numpy.float32).tostring())


if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1, rate=44100, output=1)

    play_tone(stream, frequency=500, length=1)
    play_tone(stream, frequency=500, length=0.5, volume=0)
    play_tone(stream, frequency=600, length=1)
    play_tone(stream, frequency=500, length=0.5, volume=0)
    play_tone(stream, frequency=700, length=1)
    play_tone(stream, frequency=500, length=0.5, volume=0)
    play_tone(stream, frequency=800, length=1)
    play_tone(stream, frequency=500, length=0.5, volume=0)
    play_tone(stream, frequency=900, length=1)
    play_tone(stream, frequency=500, length=0.5, volume=0)
    play_tone(stream, frequency=1000, length=1)

    stream.close()
    p.terminate()
