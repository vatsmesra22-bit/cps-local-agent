@echo off
rem One-time setup on a new PC: Python packages, folders, a quick check, and a Desktop shortcut.
cd /d "%~dp0"
title CSP GPS Report - setup

echo.
echo  ==========================================
echo    CSP GPS Complaints - ek baar ka setup
echo  ==========================================
echo.

rem Prefer a Python version the packages are known to work with (3.11 / 3.12), then any python on PATH.
set "PY="
py -3.11 -c "" >nul 2>&1 && set "PY=py -3.11"
if not defined PY py -3.12 -c "" >nul 2>&1 && set "PY=py -3.12"
if not defined PY python -c "import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,13) else 1)" >nul 2>&1 && set "PY=python"
if not defined PY py -3 -c "" >nul 2>&1 && set "PY=py -3"
if not defined PY (
    echo  Python nahi mila.
    echo  1. https://www.python.org/downloads/ se Python 3.11 ya naya install kijiye
    echo  2. Install ke time "Add python.exe to PATH" pe tick lagaiye
    echo  3. Phir ye Setup.bat dobara chalaiye
    echo.
    pause
    exit /b 1
)

echo  Step 1/4: Python environment bana raha hoon...
if not exist ".venv\Scripts\python.exe" (
    %PY% -m venv .venv
    if errorlevel 1 ( echo  Python environment nahi ban paya. & pause & exit /b 1 )
)

echo  Step 2/4: Zaroori packages install ho rahe hain (2-3 minute)...
".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
".venv\Scripts\python.exe" -m pip install --quiet -r requirements-dev.txt
if errorlevel 1 (
    echo  Packages install nahi hue.
    echo   - Internet check kijiye
    echo   - Folder ka path chhota rakhiye, jaise C:\CSP-GPS ^(bahut lambe path pe Windows install rok deta hai^)
    echo  Phir Setup.bat dobara chalaiye.
    pause
    exit /b 1
)

echo  Step 3/4: Folders aur ek chhota test...
if not exist input mkdir input
if not exist input\web_capture\images mkdir input\web_capture\images
if not exist logs mkdir logs
if not exist .env copy /y .env.example .env >nul
".venv\Scripts\python.exe" -m pytest -q tests >logs\setup_test.log 2>&1
if errorlevel 1 (
    echo  Test mein dikkat aayi - logs\setup_test.log dekhiye. Setup phir bhi jaari hai.
) else (
    echo  Test theek hai.
)

echo  Step 4/4: Desktop pe "Update Report" shortcut bana raha hoon...
if not defined NO_SHORTCUT powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\CSP GPS - Update Report.lnk'); $s.TargetPath='%~dp0Update Report.bat'; $s.WorkingDirectory='%~dp0'; $s.Save()" >nul 2>&1

echo.
echo  Setup ho gaya!
echo   - Report banane ke liye: Desktop pe "CSP GPS - Update Report" double-click
echo   - Roz apne aap chalane ke liye: docs\USER_GUIDE.md ka "Step 4" dekhiye
echo.
pause
