@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

where pythonw >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" pythonw bridge.py
    exit /b 0
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" python bridge.py --background
    exit /b 0
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" pyw -3 bridge.py
    exit /b 0
)

exit /b 1
