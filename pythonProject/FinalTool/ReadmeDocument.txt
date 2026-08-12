# Smart TV ADB Manager

A Windows GUI tool for installing and managing APKs on Android Smart TVs over ADB.

---

## For Colleagues — Running the App

### Pre-requisites

1. **Android Platform Tools** (provides the `adb` command)
   - Download: https://developer.android.com/tools/releases/platform-tools
   - Extract the zip and add the folder to your system `PATH`
   - Verify: open a terminal and run `adb version`

2. **Wi-Fi** — your PC and the Smart TV must be on the same network.

3. **Enable Developer Mode & ADB on your TV**
   - Go to *Settings → Device Preferences → About → Build* and click it 7 times
   - Then enable *ADB Debugging* under Developer Options

### Using the App

| Step | Action |
|------|--------|
| 1 | Enter the IP of the device (verify device IP in *Settings → Network → About*) |
| 2 | Click **Connect** — the TV should appear in the device list |
| 3 | Enter the **Package Name** (e.g. `com.vodafone.vtv.atv`) |
| 4 | Click **Browse** and select the `.apk` file |
| 5 | Tick options as needed, then click **▶ Install APK** |

The **Output Log** at the bottom shows real-time progress.

---
## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `adb not found` | Add platform-tools folder to system PATH |
| Device doesn't appear | Confirm ADB Debugging is on; try reconnecting |
| Install fails | Check the package name matches the APK exactly |
| TV asks to authorise | Accept the RSA fingerprint prompt on the TV screen |