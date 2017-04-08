import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt8
#CHANNELS = 2
CHANNELS = 1
#RATE = 44100
RATE = 14400
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "noise.dat"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()

print("* done recording")

data = []
for f in frames:
    for v in f:
        data.append(v)
noise_data = bytes(data)

count = 0
for v in data:
    print('%3d, ' % v, end='')
    count += 1
    if count >= 12:
        print('')
        count = 0
print('')

# sound the noise_data
pyaudio = pyaudio.PyAudio()
stream = pyaudio.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=RATE,
                      output=True)

stream.write(noise_data)

import sys
sys.exit(0)

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
