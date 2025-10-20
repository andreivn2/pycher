import sounddevice as sd
import numpy as np

# Choose the input device: BlackHole 2h
device_name = "BlackHole 2ch"

# Find the device index
device_index = None
for i, dev in enumerate(sd.query_devices()):
    if device_name.lower() in dev['name'].lower() and dev['max_input_channels'] > 0:
        device_index = i
        print(f"Using device #{i}: {dev['name']}")
        break

if device_index is None:
    raise RuntimeError(f"Input device '{device_name}' not found")

# Settings
samplerate = 44100  # Standard audio rate
blocksize = 1024    # How many samples per block

# Callback to process incoming audio
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    volume_norm = np.linalg.norm(indata)  # RMS
    print(f"Volume: {volume_norm:.4f}")

# Start input stream
with sd.InputStream(callback=audio_callback,
                    channels=2,  # Assuming stereo from BlackHole 2h
                    samplerate=samplerate,
                    blocksize=blocksize,
                    device=device_index):
    print("Recording... Press Ctrl+C to stop.")
    try:
        while True:
            sd.sleep(1000)  # Keep the stream alive
    except KeyboardInterrupt:
        print("Stopped.")

