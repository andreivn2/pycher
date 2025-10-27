import os
import time
import sys
import random
import argparse

import pyautogui
import sounddevice as sd
import numpy as np
from datetime import datetime, timedelta

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



# Create the parser
parser = argparse.ArgumentParser(description="Script that takes --no-alt-tab flag.")
parser.add_argument('--no-alt-tab', action='store_true', help='Disable Alt-Tab functionality')
parser.add_argument('--retina', action='store_true', help='Adapt to retina screen scaling')
parser.add_argument( "--confidence", type=float, default=0.75, help="Minimum confidence")
parser.add_argument( "--start", type=int, default=0, help="Time before starting (min)")
parser.add_argument( "--duration", type=int, default=600, help="How long to fish (min)")
args = parser.parse_args()

SAMPLE_RATE = 44100
CHUNK_DURATION = 0.1  # seconds
BLOCK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)
THRESHOLD = 0.012
CONFIDENCE_THRESH = args.confidence

print(f"\nUsing device with id ({DEVICE_INDEX}) for monitoring")
print(args)

def main():
    focus_game()
    time.sleep(0.2)

    screen_width, screen_height = pyautogui.size()
    pyautogui.rightClick(screen_width//2, screen_height//2)
    time.sleep(0.1)
    pyautogui.rightClick(screen_width//2, screen_height//2)
    time.sleep(2)
# Take a screenshot of the entire screen
    screenshot = pyautogui.screenshot()
# Save it to a file
    screenshot.save('ss.png')

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
                focus_game()
                random_sleep(0.2,0.5)
                pyautogui.rightClick(x=tarx,y=tary)
                random_sleep(0.5,1)
                break


def random_sleep(min, max):
    time.sleep(random.uniform(min,max))

def focus_game():
    if os.name == 'nt':
        return
    elif os.name == 'posix':
        os.system("osascript -e 'tell application \"Moonlight\" to activate'")

if __name__ == "__main__":
    start_time = datetime.now() + timedelta(minutes=args.start)
    end_time = start_time + timedelta(minutes=args.duration)
    while True:
        if datetime.now() < start_time:
            print(f"Starting at {start_time}. Current time is {datetime.now()}. Waiting...")
            focus_game()
            pyautogui.press('space')
            time.sleep(60)
            continue

        if datetime.now() > end_time:
            sys.exit(0)

        main()
