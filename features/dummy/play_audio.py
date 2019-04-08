import pyaudio
import wave
import sys
import time

CHUNK = 1024

print(sys.argv[1])
if len(sys.argv) < 2:
    print("Plays a wave file.\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

data = wf.readframes(CHUNK)
start_time = time.time()

while data != '':
    stream.write(data)
    data = wf.readframes(CHUNK)

    if time.time() - start_time > 5:
        break

stream.stop_stream()
stream.close()

p.terminate()
