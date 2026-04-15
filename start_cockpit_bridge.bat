@echo off
cd /d "%~dp0"
echo ============================================================
echo  Teatower Cockpit Bridge  -  http://127.0.0.1:8765
echo ============================================================
pip install --quiet fastapi uvicorn pydantic 2>nul
python cockpit_bridge.py
pause
