import os
import time
import subprocess

def kill_steam():
    while True:
        steam_pids = subprocess.check_output("ps aux | grep steam | grep -v grep | awk '{print $2}'", shell=True).decode().strip().split()
        if steam_pids:
            print("Killing Steam processes...")
            for pid in steam_pids:
                try:
                    os.kill(int(pid), 9)
                except Exception as e:
                    print(f"Failed to kill Steam process {pid}: {e}")
        time.sleep(5)  # Check every 5 seconds
