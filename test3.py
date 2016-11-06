import sys
import pyaudio
import wave
import time
import struct
import math

HOLD = 5
#CHUNK = 1024
CHUNK = 32
FORMAT = pyaudio.paInt16
#FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 14400
RECORD_SECONDS = 2
SHORT_NORMALIZE = (1.0 / 32768.0)

DOT_DASH = 70

MaxBucket = 32

SILENCE = 200

Morse = {
         '.-': 'A',
         '-...': 'B',
         '-.-.': 'C',
         '-..': 'D',
         '.': 'E',
         '..-.': 'F',
         '--.': 'G',
         '....': 'H',
         '..': 'I',
         '.---': 'J',
         '-.-': 'K',
         '.-..': 'L',
         '--': 'M',
         '-.': 'N',
         '---': 'O',
         '.--.': 'P',
         '--.-': 'Q',
         '.-.': 'R',
         '...': 'S',
         '-': 'T',
         '..-': 'U',
         '...-': 'V',
         '.--': 'W',
         '-..-': 'X',
         '-.--': 'Y',
         '--..': 'Z',
         '.----': '1',
         '..---': '2',
         '...--': '3',
         '....-': '4',
         '.....': '5',
         '-....': '6',
         '--...': '7',
         '---..': '8',
         '----.': '9',
         '-----': '0',
         '.-.-.-': '.',
         '--..--': ',',
         '..--..': '?',
         '.----.': '\'',
         '-.-.--': '!',
         '-..-.': '/',
         '-.--.': '(',
         '-.--.-': ')',
         '.-...': '&',
         '---...': ':',
         '-.-.-.': ';',
         '-...-': '=',
         '-....-': '-',
         '..--.-': '_',
         '.-..-.': '"',
         '...-..-': '$',
         '.--.-.': '@',
        }


def decodeMorse(morse):
    try:
        char = Morse[morse]
    except KeyError:
        char = u'\u00bf'
    print char,
    sys.stdout.flush()

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

def getSample(stream):
    samples = []
    count = 0

    SIGNAL = 80

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        value = getLevel(data)
        samples.append(value)
        if value < SIGNAL:
            count += 1
            if count > SILENCE:
                return samples
        else:
            count = 0

def readMorse(stream):
    while True:
        samples = getSample(stream)

        # dump samples
        top = max(samples)
        bot = min(samples)
        bucket_size = (top-bot) / MaxBucket
        threshold = MaxBucket / 4
        #print('top=%d, bot=%d, bucket_size=%d, b_s*MaxBucket=%d, threshold=%d'
        #      % (top, bot, bucket_size, bucket_size*MaxBucket, threshold))

        state = False
        count = 0
        hold = HOLD
        morse = ''
        for s in samples:
            bucket = int(s / bucket_size)
            if bucket >= MaxBucket:
                bucket = MaxBucket - 1
            s_state = (bucket > threshold)
#            print('state=%s, s_state=%s' % (str(state), str(s_state)))
            if s_state == state:
                count += 1
                hold = HOLD
#                print('~~ SAME: count=%d' % count)
            else:
#                print('~~ DIFFERENT: hold=%d' % hold)
                hold -= 1
                if hold <= 0:
                    if state and count > 2:
#                        print('#### %s %d %s' % (str(state), count, 'DOT' if count < DOT_DASH else 'DASH'))
                        morse += '.' if count < DOT_DASH else '-'
                    hold = HOLD
                    count = 1
                    state = s_state

        #if state and count > 0:
        #    print('#### %s %d' % (str(state), count))

        if morse:
            decodeMorse(morse)
#            print morse,
#            sys.stdout.flush()

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

readMorse(stream)

stream.stop_stream()
stream.close()
p.terminate()

