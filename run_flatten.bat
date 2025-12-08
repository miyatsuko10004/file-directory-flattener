@echo off
chcp 65001 > nul
cd /d %~dp0
echo =======================================================
echo  Running flatten.py with uv...
echo =======================================================
uv run flatten.py
echo.
echo Execution finished.
pause
