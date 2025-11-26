from ppadb.client import Client as AdbClient
import subprocess


def start_adb_daemon():
    # Command to explicitly start the server
    command = ["adb", "start-server"]

    try:
        # Use subprocess.run to execute the command
        # 'capture_output=True' captures stdout/stderr
        # 'check=True' raises an error if the command fails
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("ADB Daemon started successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error starting ADB daemon: {e.stderr}")
    except FileNotFoundError:
        # This occurs if 'adb' is not in the system's PATH
        print("ERROR: 'adb' command not found. Ensure Android platform-tools is in your system PATH.")

    return result

def run_adb_command_with_ppadb(udid):
    udid = udid

    #Check if UDID is empty
    if udid != "":
        print(f"ADB workflow for : {udid}")
    else:
        print("No UDID to proceed")
        return

    # Connect to the ADB server
    client = AdbClient(host="127.0.0.1", port=5037)


    #Connect to a device
    client.remote_connect(udid, 5555)

    # Get a list of connected devices
    devices = client.devices()

    if len(devices) == 0:
        print("No devices connected. Ensure ADB server is running and devices are connected with USB Debugging enabled.")
        return

    # Select the first connected device
    device = devices[0]
    print(f"Connected to device: {device.serial}")

    # Get App version
    try:
        vodafone_version = device.shell("dumpsys package com.vodafone.vtv.atv.de | grep versionName")
        print(f"VTV Version: {vodafone_version.strip()}")
    except Exception as e:
        print(f"Error executing command: {e}")

    #install_app("com.vodafone.vtv.atv.de")

    #Disconnect device
    client.remote_disconnect(udid)

if __name__ == "__main__":
    connection = start_adb_daemon()
    if connection:
        run_adb_command_with_ppadb("192.168.50.24")
    else:
        print("Failed to start the adb daemon!")
