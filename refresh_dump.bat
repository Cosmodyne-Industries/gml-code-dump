@echo off
cd /d "%~dp0"
echo Running dump builder...
python dump_create.py
pause
