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

def enter_text_with_adb(udid, text):
    udid = udid
    text = text

    # Check if text is empty
    if text != "":
        print(f"Text to send using ADB command line is: {text}")
    else:
        print("No text to proceed")
        return False

    # Check if UDID is empty
    if udid != "":
        print(f"ADB workflow for : {udid}")
    else:
        print("No UDID to proceed")
        return False

    # Connect to the ADB server
    client = AdbClient(host="127.0.0.1", port=5037)

    # Connect to a device
    client.remote_connect(udid, 5555)

    # Get a list of connected devices
    devices = client.devices()

    if len(devices) == 0:
        print(
            "No devices connected. Ensure ADB server is running and devices are connected with USB Debugging enabled.")
        return False

    # Select the first connected device
    device = devices[0]
    print(f"Connected to device: {device.serial}")

    # Append a success marker to the shell command
    outputString = device.shell(f'input text "{text}" && echo "success"')

    if "success" in outputString:
        print(f'Successfully sent text')
        return True
    else:
        print(f'Failed to send text (Actual output: {outputString})')
        return False

def stop_adb_daemon():
    cmdLine = ["adb", "kill-server"]

    try:
        # Run the adb kill-server command
        stop = subprocess.run(cmdLine, capture_output=True, text=True, check=True)
        print("ADB server stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping ADB server: {e.stderr}")
    return stop

if __name__ == "__main__":
    connection = start_adb_daemon()
    if connection:
        sendText = enter_text_with_adb("192.168.0.160", "florianseidl.vodafone+1@gmail.com#")
        if sendText:
            print("Successfully send the text")
        else:
            print("Failed to send text")
    else:
        print("Failed to start the adb daemon!")
    stop_adb_daemon()