import os
import time
import requests
import signal
from hendi_logger import update_run_log
import sys

# Configuration
FOLDER_PATH = "/home/nocola/records"  # Replace with the actual folder path
API_URL = "http://157.10.160.232/api/Record/insert"
SUCCESS_FOLDER = "/home/nocola/records/success"  # Replace with the folder where successfully uploaded files should be moved
LOG_FILE = "upload_log.txt"
response_status = 0

def upload_wav_file(file_path):
    try:
        # Prepare data for the HTTP POST request
        files = {'file': open(file_path, 'rb')}
        data = {
            'status': 'DONE',
            'machineId': '',
            'text': ''
        }

        # Make the HTTP POST request
        response = requests.post(API_URL, files=files, data=data)
        global response_status

        if response.status_code == 200:
            print(f"Uploaded {file_path} successfully!")
            response_status = response.status_code
            return True
        else:
            print(f"Failed to upload {file_path}. Status code: {response.status_code}")
            response_status = response.status_code
            return False
    except Exception as e:
        print(f"Error uploading {file_path}: {e}")
        return False

def move_to_success_folder(file_path):
    try:
        new_path = os.path.join(SUCCESS_FOLDER, os.path.basename(file_path))
        os.rename(file_path, new_path)
        print(f"Moved {file_path} to {new_path}")
    except Exception as e:
        print(f"Error moving {file_path} to success folder: {e}")

def log_upload_attempt(file_path, success, status_code):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "r") as existing_log:
        existing_entries = existing_log.read()
    with open(LOG_FILE, "w") as log:
        new_entry = f"{timestamp} - {os.path.basename(file_path)} - Success: {success} - Status code: {status_code}\n"
        log.write(new_entry + existing_entries)

def main():
    while True:
        for filename in os.listdir(FOLDER_PATH):
            if filename.lower().endswith(".wav"):
                file_path = os.path.join(FOLDER_PATH, filename)
                if upload_wav_file(file_path):
                    move_to_success_folder(file_path)
                    log_upload_attempt(file_path, success=True, status_code=response_status)
                else:
                    log_upload_attempt(file_path, success=False, status_code=response_status)

        # Wait for some time before checking again (e.g., every 10 minutes)
        time.sleep(10)

def update_exc_log_ur(exc_code):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("run_log.txt", "r") as existing_log:
        existing_entries = existing_log.read()
    with open("run_log.txt", "w") as log:
        new_entry = f"{timestamp} - Upload Routine is closed with exception code {exc_code}\n"
        log.write(new_entry + existing_entries)

def signal_handler(sig, frame):
    update_exc_log_ur(sig)
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signals


if __name__ == "__main__":
    try:
        update_run_log("Upload Routine")
        main()
    except Exception as e:
        print("Program terminated.")
        update_exc_log_vr(e)

