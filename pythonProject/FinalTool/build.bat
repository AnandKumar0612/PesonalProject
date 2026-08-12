@echo off
:: ─────────────────────────────────────────────────────────────────────────────
::  build.bat  —  Packages app.py into a standalone Windows .exe
::  Smart TV ADB Manager (Install + Text Sender)
:: ─────────────────────────────────────────────────────────────────────────────

echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║  Smart TV ADB Manager  •  Builder         ║
echo  ║  (APK Install + Text Sender combined)     ║
echo  ╚═══════════════════════════════════════════╝
echo.

echo [1/4] Installing Python dependencies...
pip install pure-python-adb pyinstaller --quiet
if %ERRORLEVEL% neq 0 (
    echo  ERROR: pip install failed. Make sure Python is in your PATH.
    pause & exit /b 1
)
echo       Done.
echo.

echo [2/4] Cleaning previous build artefacts...
if exist build    rmdir /s /q build
if exist dist     rmdir /s /q dist
if exist app.spec del /q app.spec
echo       Done.
echo.

echo [3/4] Building executable (this may take ~60 seconds)...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "SmartTV-ADB-Manager" ^
    --hidden-import ppadb ^
    --hidden-import ppadb.client ^
    --hidden-import ppadb.device ^
    app.py

if %ERRORLEVEL% neq 0 (
    echo  ERROR: PyInstaller failed. See output above.
    pause & exit /b 1
)
echo       Done.
echo.

echo [4/4] Build complete!
echo.
echo  ┌──────────────────────────────────────────────────────────────┐
echo  │  Output:  dist\SmartTV-ADB-Manager.exe                      │
echo  │                                                              │
echo  │  Workflow:                                                   │
echo  │   1. Select device from dropdown                            │
echo  │   2. Browse APK → Install APK  (connects automatically)     │
echo  │   3. Send Text  (reuses same session, no reconnect)         │
echo  │   4. Click Stop ADB Server when fully done                  │
echo  │                                                              │
echo  │  Colleagues need adb in their PATH:                         │
echo  │   → developer.android.com/tools/releases/platform-tools     │
echo  └──────────────────────────────────────────────────────────────┘
echo.
pause
