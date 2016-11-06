import pyaudio
import wave

#CHUNK = 1024
CHUNK = 1
FORMAT = pyaudio.paInt16
#CHANNELS = 2
CHANNELS = 1
#RATE = 44100
RATE = 10025
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording, CHUNK=%d" % CHUNK)

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    print('data=%s, len=%d' % (str(data), len(data)))
#    print(str(data))
#    print('%d' % ord(data))

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

