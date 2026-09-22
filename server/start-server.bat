@echo off
rem Runs the Avesta 7.4 server (listens on 127.0.0.1:7171, see config.lua)
title mintwall - Avesta 7.4
cd /d "%~dp0"
avesta74.exe
pause
