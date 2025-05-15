@echo off
echo Terminating any existing Python and Tkinter processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM wish.exe /T >nul 2>&1
timeout /t 1 /nobreak >nul
cd %~dp0..
echo Starting application...
title OW2-Stadium-Build-Auto-Optimizer
set PYTHONPATH=%CD%
python src/main.py

