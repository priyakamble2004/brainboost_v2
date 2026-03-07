@echo off
title Brain Boost V2 Launcher
echo ================================
echo    BRAIN BOOST V2 - STARTING
echo ================================
echo.

echo Starting MySQL...
net start MySQL81 >nul 2>&1
echo MySQL Ready!

echo Starting Brain Boost Server...
cd /d C:\Users\Asus\Downloads\Brainboost
start /min cmd /c python app.py

echo Waiting for server to start...
timeout /t 4 /nobreak >nul

echo Opening Browser...
start http://localhost:5000

echo.
echo Brain Boost is running!
echo Close this window anytime.
pause