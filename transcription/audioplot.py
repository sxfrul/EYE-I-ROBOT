import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import wave

# Parameters
CHUNK = 2048  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format (bytes per sample)
CHANNELS = 1  # Single channel for microphone input
RATE = 44100  # Sampling rate (samples/second)
UPDATE_INTERVAL = 50  # Milliseconds between each update
MATCH_THRESHOLD = 1000  # Adjust this threshold as needed

# Load the sample WAV file
sample_wav_file = "eyero.wav"
with wave.open(sample_wav_file, 'rb') as wf:
    sample_rate = wf.getframerate()
    sample_width = wf.getsampwidth()
    sample_frames = wf.readframes(wf.getnframes())

# Convert sample frames to numpy array
sample_data = np.frombuffer(sample_frames, dtype=np.int16)

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open the microphone stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Initialize plot
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK) / RATE  # Time axis in seconds
line, = ax.plot(x, np.random.rand(2 * CHUNK), '-', lw=2)  # Make y-array match the length of x-array
ax.set_ylim(-32768, 32767)  # Assuming 16-bit signed integer
ax.set_xlim(0, 2 * CHUNK / RATE)

# Function to update plot
def update_plot(frame):
    data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
    line.set_ydata(np.concatenate([line.get_ydata()[CHUNK:], data]))  # Shift old data and append new data
    

    mse = np.mean((data - sample_data) ** 2)
    # Compare microphone input with sample audio

    return line,

# Create animation
ani = animation.FuncAnimation(fig, update_plot, blit=True, interval=UPDATE_INTERVAL)

# Show plot
plt.show()

# Close the microphone stream
stream.stop_stream()
stream.close()
p.terminate()
