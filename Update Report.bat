@echo off
rem One click: read the WhatsApp exports in input\, rebuild the Excel report, open the dashboard.
cd /d "%~dp0"
title CSP GPS Report - updating

echo.
echo  ==========================================
echo    CSP GPS Complaints - report update
echo  ==========================================
echo.
echo  Step 1: WhatsApp export padh raha hoon (input folder)...
echo.

".venv\Scripts\python.exe" process.py --auto-import
if errorlevel 1 (
    echo.
    echo  Kuch galat hua. Upar ka message padhiye.
    echo  Sabse aam wajah: input folder mein WhatsApp export ^(.zip^) nahi hai.
    echo.
    pause
    exit /b 1
)

echo.
echo  Step 2: Dashboard khol raha hoon...
netstat -ano | findstr /r /c:":8501 .*LISTENING" >nul
if errorlevel 1 (
    start "CSP GPS Dashboard (is window ko band mat kijiye)" /min ".venv\Scripts\python.exe" -m streamlit run dashboard\app.py --server.port 8501 --server.headless true
    timeout /t 6 /nobreak >nul
)
if not defined NO_OPEN start "" "http://csp-gps.localhost:8501"

echo.
echo  Ho gaya!
echo   - Excel report : output\CSP_GPS_Issue_Report.xlsx
echo   - Dashboard    : http://csp-gps.localhost:8501
echo.
pause
