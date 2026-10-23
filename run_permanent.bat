@echo off
title LAK04 - Permanent Server & Public Link Runner
cd /d "%~dp0"
echo ========================================================
echo  LAK04 Student Notes - Permanent Hosting Service
echo ========================================================
echo  * Public Internet Link: https://lak04-notes.loca.lt
echo  * Localhost:            http://127.0.0.1:5000
echo ========================================================
start "LAK04 Server" /b python app.py
timeout /t 3 /nobreak >nul
npx -y localtunnel --port 5000 --subdomain lak04-notes
pause
