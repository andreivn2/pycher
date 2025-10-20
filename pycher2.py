import os
import time
import sys
import random
import argparse

import pyautogui
import sounddevice as sd
import numpy as np

from findtar import find_target_coordinates

# Specify the desired device name
desired_device_name = "BlackHole 2ch"  # Replace with your actual device name
devices = sd.query_devices()
print(f"Audio devices detected: \n {devices}")
DEVICE_INDEX = None  # Or set to a specific device indexinates
for idx, device in enumerate(devices):
    print(device)
    if desired_device_name.lower() in device['name'].lower():  # Case-insensitive search
        DEVICE_INDEX = idx
        break
if DEVICE_INDEX is None:
    raise ValueError("unable to find audio interface to monitor")


SAMPLE_RATE = 44100
CHUNK_DURATION = 0.1  # seconds
BLOCK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)
THRESHOLD = 0.012
CONFIDENCE_THRESH = 0.65



# Create the parser
parser = argparse.ArgumentParser(description="Script that takes --no-alt-tab flag.")
parser.add_argument('--no-alt-tab', action='store_true', help='Disable Alt-Tab functionality')
parser.add_argument('--retina', action='store_true', help='Adapt to retina screen scaling')
args = parser.parse_args()

print(f"\nUsing device with id ({DEVICE_INDEX}) for monitoring")
print(args)

def main():
    print("\nListening for audio...")

    os.system("osascript -e 'tell application \"Moonlight\" to activate'")
    time.sleep(0.2)

    pyautogui.press('y')
    time.sleep(2)
# Take a screenshot of the entire screen
    screenshot = pyautogui.screenshot()
# Save it to a file
    screenshot.save('ss.png')

    print(args)

    if not args.no_alt_tab:
        os.system("osascript -e 'tell application \"System Events\" to key code 48 using {command down}'")


    coords, confidence = find_target_coordinates()
    tarx, tary = coords

    if (confidence < CONFIDENCE_THRESH):
        print("Confidence too low. Recasting.")
        return

    if args.retina:
        tarx = tarx//2
        tary = tary//2

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                        blocksize=BLOCK_SIZE, dtype='float32',
                        device=DEVICE_INDEX) as stream:
        # Record the start time
        start_time = time.time()

        while True & (time.time() - start_time < 30):
            audio, _ = stream.read(BLOCK_SIZE)
            rms = np.sqrt(np.mean(audio**2))
            sys.stdout.write(f'\rRMS: {rms:.4f}')
            sys.stdout.flush()
            if rms > THRESHOLD:
                os.system("osascript -e 'tell application \"Moonlight\" to activate'")
                random_sleep(0.2,0.5)
                pyautogui.rightClick(x=tarx,y=tary)
                random_sleep(0.5,1)
                break


def random_sleep(min, max):
    time.sleep(random.uniform(min,max))

if __name__ == "__main__":
    while True:
        main()
