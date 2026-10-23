@echo off
title LAK04 - Permanent Server Runner (Direct Access, No IP Needed)
cd /d "%~dp0"
echo ========================================================
echo  LAK04 Student Notes - Direct Public Host
echo  * Localhost: http://127.0.0.1:5000
echo  * Starting direct public tunnel (No IP entry needed)...
echo ========================================================
start "LAK04 Python Server" /b python app.py
timeout /t 3 /nobreak >nul
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:127.0.0.1:5000 serveo.net
pause
