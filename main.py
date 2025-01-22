import time
import threading
import numpy as np
import sounddevice as sd
from pynput.mouse import Button, Controller
import zipfile
import os
import subprocess
import sys
import requests


def check_vb_audio_installed():
    devices = sd.query_devices()
    for device in devices:
        if "CABLE Output (VB-Audio Virtual" in device['name']:
            return True
    return False


def download_and_install_vb_audio():
    # URL of the ZIP file
    url = 'https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack43.zip'

    # Path where the ZIP file will be downloaded
    zip_path = os.path.join(os.getcwd(), 'VBCABLE_Driver_Pack43.zip')

    # Download the ZIP file
    print("Downloading VB Audio Virtual Cable...")
    response = requests.get(url)
    with open(zip_path, 'wb') as f:
        f.write(response.content)

    print("Download completed.")

    # Destination folder for extraction
    extract_path = os.path.join(os.getcwd(), 'vbcable_driver')

    # Extract the ZIP archive
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
        print("ZIP file successfully extracted.")

    # Path to the installation file once decompressed
    installer_path = os.path.join(extract_path, 'VBCABLE_Setup.exe')

    # Run the installer in silent mode
    try:
        subprocess.run([installer_path, '/S'], check=True)
        print("VB Audio Virtual Cable successfully installed.")
    except subprocess.CalledProcessError:
        print("Error during VB Audio installation. Manual installation required")
        sys.exit("Error: Unable to install VB Audio Virtual Cable.")

print("error : VB audio not installed " if check_vb_audio_installed()==False else print("VB audio is installed"))
if check_vb_audio_installed()==False:
    input("press any key to install VB audio")
    download_and_install_vb_audio()



print("démarrage du bot")
def get_device_index(target_device_name):
    # Retrieve all available devices
    devices = sd.query_devices()

    # Iterate through each device to find a match
    for index, device in enumerate(devices):
        if target_device_name in device['name']:  # If the name matches the device
            return index  # Return the index if found

    # If the device is not found
    return None

# Name of the target device
target_device_name = "CABLE Output (VB-Audio Virtual"

# Get the index of the corresponding device
device_index = get_device_index(target_device_name)
last_sound_time = time.time()  # Initialize the variable here
action_pending = False
threshold = 0.00400  # Detection threshold
mouse = Controller()  # To control the mouse
lock = threading.Lock()  # Create a lock to synchronize threads

def perform_fishing_action():
    global action_pending
    with lock:  # Use a lock to ensure synchronization
        print("Fishing sound detected: Performing action...")
        mouse.click(Button.right)  # Simulate a right click
        time.sleep(1)  # Wait for the action to complete
        mouse.click(Button.right)
        time.sleep(1.5)
        print("Action completed.")
        action_pending = False  # Mark the action as completed

def change_item():
    global action_pending
    with lock:  # Use a lock to synchronize
        print("Changing item")
        mouse.scroll(0, 1)
        time.sleep(1)
        mouse.click(Button.right)
        time.sleep(3)  # Wait for the action to complete
        print("Done")
        action_pending = False  # Mark the action as completed

def calculate_rms(indata):
    # Calculate the RMS (Root Mean Square) for the audio data
    audio_data = np.array(indata, dtype=np.float32)
    rms = np.sqrt(np.mean(audio_data**2))
    return rms

def audio_callback(indata, frames, time_info, status):
    global last_sound_time, action_pending  # Make last_sound_time global

    rms_value = calculate_rms(indata)
    #print(f"RMS: {rms_value:.5f}", f"delta:{time.time()-last_sound_time:.5f}")

    # Check if the threshold is exceeded and no action is pending
    if not action_pending:
        if time.time() - last_sound_time < 45 and rms_value > threshold :  # Use system time here
            action_pending = True  # Mark that the action is pending
            threading.Thread(target=perform_fishing_action).start()  # Start the action
            last_sound_time = time.time()  # Update the time of the last action
        elif time.time() - last_sound_time > 45:  # Allow item change if necessary
            action_pending = True
            threading.Thread(target=change_item).start()  # Start the item change
            last_sound_time = time.time()  # Update the time of the last action

def start_audio_stream():
    print("Starting listening...")
    with sd.InputStream(device=device_index, callback=audio_callback, channels=8, samplerate=44100):
        while True:
            time.sleep(100)  # Infinite loop with pause

start_audio_stream()
