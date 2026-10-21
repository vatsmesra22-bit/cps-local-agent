@echo off
rem Daily run (Windows Task Scheduler): pick up new WhatsApp exports from Downloads and rebuild the report.
rem No windows, no prompts; everything goes to logs\daily.log.
cd /d "%~dp0.."
set PYTHONIOENCODING=utf-8
echo ===== %date% %time% ===== >> logs\daily.log
".venv\Scripts\python.exe" process.py --auto-import >> logs\daily.log 2>&1
echo exit code %errorlevel% >> logs\daily.log
