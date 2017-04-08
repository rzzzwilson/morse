import pyaudio
import random

stream=pyaudio.PyAudio().open(format=pyaudio.paInt8,channels=1,rate=22050,output=True)

last_noise = [32]
for n in range(220000):
    new_noise = int(random.random()*256)
    last_noise.append(new_noise)
    last_noise = last_noise[:2]
    average_noise = sum(last_noise) // len(last_noise)
    print('average_noise=%d, new_noise=%d' % (average_noise, new_noise))
    stream.write(chr(average_noise))

stream.close()
pyaudio.PyAudio().terminate()
