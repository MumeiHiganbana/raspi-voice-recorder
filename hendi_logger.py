import os
import sys
import time
import signal


def update_run_log(script_name):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("run_log.txt", "r") as existing_log:
        existing_entries = existing_log.read()
    with open("run_log.txt", "w") as log:
        new_entry = f"{timestamp} - {script_name} - is running...\n"
        log.write(new_entry + existing_entries)
