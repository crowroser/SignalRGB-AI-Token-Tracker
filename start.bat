@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title SignalRGB AI Token Tracker Bridge

echo Starting AI Token Tracker Bridge...

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python -m src.main
    goto check_exit
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 -m src.main
    goto check_exit
)

echo [HATA] Python bulunamadi! Lutfen Python'un kurulu ve PATH'e ekli oldugundan emin olun.
pause
exit /b 1

:check_exit
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Bridge bir hata ile sonlandi (Kod: %ERRORLEVEL%).
    pause
)


