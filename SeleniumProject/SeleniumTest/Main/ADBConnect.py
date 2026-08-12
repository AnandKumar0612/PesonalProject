from ppadb.client import Client as AdbClient
import subprocess


def install_app(apkName, fileLocation):
    apkName = apkName
    fileLocation = fileLocation


    # Check if apk name is empty
    if apkName != "":
        print(f"Checking for apk file : {apkName}")
    else:
        print("No apk file to proceed")
        return False

    #Check if file name is empty
    if fileLocation != "":
        print(f"Installing file!")
    else:
        print("No file location")
        return False

    # Connect to the ADB server
    client = AdbClient(host="127.0.0.1", port=5037)

    # Get a list of connected devices
    devices = client.devices()

    for device in devices:
        if device.is_installed(apkName):
            print(f"{apkName} is already installed")
            return True
        else:
            device.install(fileLocation)
            if device.is_installed(apkName):
                print("App successfully installed")
                return True
            else:
                print("Failed to install app")
                return False

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

def run_adb_command_with_ppadb(udid, uninstallThenInstall, package):
    udid = udid
    package = package
    file_loc = "C:/Users/andy9/Downloads/"
    location = file_loc + "app_tvFireTvGenericStv_1.11.0.0_20260603_release.apk"
    print(location)

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
        app_version = device.shell(f"dumpsys package {package} | grep versionName")
        if app_version == "":
            print(f"No app present with {package}. Need to install first!")
        else:
            print(f"App Version: {app_version.strip()}")
    except Exception as e:
        print(f"Error executing command: {e}")

    if uninstallThenInstall:
        if device.uninstall(package):
            successInstall = install_app(package, location)
            if successInstall:
                Installedapp_version = device.shell(f"dumpsys package {package} | grep versionName")
                if Installedapp_version == "":
                    print(f"No app present with {package}. Need to install first!")
                else:
                    print(f"App Version: {Installedapp_version.strip()}")
            else:
                print(f"Failed to get the installed app version")
        else:
            print(f"Failed to uninstall package {package}")
            return
    else:
        install_app(package, location)

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
        install_process = run_adb_command_with_ppadb("192.168.0.160", True, "com.vodafone.vtv.atv")
        if install_process:
            print("Successfully installed the app")
        else:
            print("Failed to install app")
    else:
        print("Failed to start the adb daemon!")
    stop_adb_daemon()
