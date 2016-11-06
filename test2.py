import pyaudio
import wave
import time
import struct
import math

HOLD = 4
#CHUNK = 1024
CHUNK = 32
FORMAT = pyaudio.paInt16
#FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 14400
RECORD_SECONDS = 2
SHORT_NORMALIZE = (1.0 / 32768.0)

DOT_DASH = 70

graph = [
         "--------------------------------",
         "*-------------------------------",
         "**------------------------------",
         "***-----------------------------",
         "****----------------------------",
         "*****---------------------------",
         "******--------------------------",
         "*******-------------------------",
         "********------------------------",
         "*********-----------------------",
         "**********----------------------",
         "***********---------------------",
         "************--------------------",
         "*************-------------------",
         "**************------------------",
         "***************-----------------",
         "****************----------------",
         "*****************---------------",
         "******************--------------",
         "*******************-------------",
         "********************------------",
         "*********************-----------",
         "**********************----------",
         "***********************---------",
         "************************--------",
         "*************************-------",
         "**************************------",
         "***************************-----",
         "****************************----",
         "*****************************---",
         "******************************--",
         "*******************************-",
         "********************************",
        ]
MaxBucket = len(graph)

def getLevel(frame):
    count = len(frame) / 2
    format = '%dh' % count
    shorts = struct.unpack(format, frame)

    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n * n
    rms = math.pow(sum_squares/count, 0.5)
    return rms * 1000.0

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

samples = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK, exception_on_overflow=False)
    value = getLevel(data)
    samples.append(value)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

# dump samples
top = max(samples)
bot = min(samples)
bucket_size = (top-bot) / MaxBucket
threshold = MaxBucket / 4
print('top=%d, bot=%d, bucket_size=%d, b_s*MaxBucket=%d, threshold=%d'
      % (top, bot, bucket_size, bucket_size*MaxBucket, threshold))
for s in samples:
    value = s
    bucket = int(value / bucket_size)
    if bucket >= MaxBucket:
        bucket = MaxBucket - 1
    print('%f: %s' % (time.time(), graph[bucket]))

print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

state = False
count = 0
hold = HOLD
for s in samples:
    bucket = int(s / bucket_size)
    if bucket >= MaxBucket:
        bucket = MaxBucket - 1
    s_state = (bucket > threshold)
    print('state=%s, s_state=%s' % (str(state), str(s_state)))
    if s_state == state:
        count += 1
        hold = HOLD
        print('~~ SAME: count=%d' % count)
    else:
        print('~~ DIFFERENT: hold=%d' % hold)
        hold -= 1
        if hold <= 0:
            if state and count > 2:
                print('#### %s %d %s' % (str(state), count, 'DOT' if count < DOT_DASH else 'DASH'))
            hold = HOLD
            count = 1
            state = s_state

#if state and count > 0:
#    print('#### %s %d' % (str(state), count))
