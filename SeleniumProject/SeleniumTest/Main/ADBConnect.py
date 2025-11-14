from ppadb.client import Client as AdbClient

def run_adb_command_with_ppadb(udid):
    udid = udid
    try:
        if udid != "":
            print(f"ADB workflow for : {udid}")
        else:
            print("No UDID to proceed")
            return
    except Exception as e:
        print(f"No UDID: {e}")

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

    #Disconnect device
    client.remote_disconnect(udid)

if __name__ == "__main__":
    run_adb_command_with_ppadb("192.168.50.24")