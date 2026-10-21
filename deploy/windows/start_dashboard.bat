@echo off
rem Server: run the dashboard for the whole network (http://<server-ip>:8501). Started at boot by install_tasks.ps1.
cd /d "%~dp0..\.."
set PYTHONIOENCODING=utf-8
if not exist logs mkdir logs
".venv\Scripts\python.exe" -m streamlit run dashboard\app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --browser.gatherUsageStats false >> logs\dashboard_server.log 2>&1
