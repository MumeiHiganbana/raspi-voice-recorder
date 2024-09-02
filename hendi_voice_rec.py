import pyaudio
import wave
import numpy as np
import time
from datetime import datetime
import signal
from hendi_logger import update_run_log
import sys

# Audio settings
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of channels (mono)
RATE = 44100  # Sampling rate (44.1 kHz)
CHUNK = 1024  # Buffer size
START_THRESHOLD = 17000
SILENCE_THRESHOLD = 12000  # Silence threshold
START_DURATION = 2
SILENCE_DURATION = 2  # Duration of silence to stop recording (in seconds)
MAX_RECORD_TIME = 115  # Maximum recording time (in seconds)
MAX_REASON = False

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Function to create a new audio stream
def create_stream():
    return audio.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=RATE,
                      input=True,
                      frames_per_buffer=CHUNK)

# Function to check if the audio data is silent
def is_silent(data):
    return np.max(np.frombuffer(data, dtype=np.int16)) < SILENCE_THRESHOLD

def is_start(data):
    return np.max(np.frombuffer(data, dtype=np.int16)) < START_THRESHOLD

def main():
    print("Listening for sound...")
    stream = create_stream()
    
    while True:
        frames = []
        silent_chunks = 0
        recording = False
        
        while True:
            data = stream.read(CHUNK,exception_on_overflow = False)
            frames.append(data)
            
            if(recording == False):
                if is_start(data):
                    silent_chunks += 1
                else:
                    silent_chunks = 0
                    recording = True
                    print("Sound detected")
                if silent_chunks > START_DURATION * RATE / CHUNK:
                    print("Attempt to listen.")
                    break
            else:
                if is_silent(data):
                    silent_chunks += 1
                else:
                    silent_chunks = 0
                if (silent_chunks > SILENCE_DURATION * RATE / CHUNK) :
                    print("Silence detected, stopping recording.")
                    MAX_REASON = False
                    break
                if (len(frames) >= MAX_RECORD_TIME * RATE / CHUNK):
                    print("Maximum recording time reached, stopping recording.")
                    MAX_REASON = True
                    break
        
        if recording:
            # Save the recorded data to a .wav file with timestamp
            timestamp = int(time.time())*1000
            if (MAX_REASON == True):
                filename = f"{timestamp}_M.wav"
            else:
                filename = f"{timestamp}_S.wav"
            wf = wave.open("records/"+filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            print(f"Recording saved as {filename}")

        frames = []

def update_exc_log_vr(exc_code):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("run_log.txt", "r") as existing_log:
        existing_entries = existing_log.read()
    with open("run_log.txt", "w") as log:
        new_entry = f"{timestamp} -  Voice Rec is closed with exception code {exc_code}\n"
        log.write(new_entry + existing_entries)

def signal_handler(sig, frame):
    update_exc_log_vr(sig)
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signals


if __name__ == "__main__":
    try:
        update_run_log("Voice Rec")
        main()
    except Exception as e:
        print("Program terminated.")
        update_exc_log_vr(e)
    finally:
        #stream.stop_stream()
        #stream.close()
        audio.terminate()
