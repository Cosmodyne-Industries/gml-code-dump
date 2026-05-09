@echo off
echo Running dump builder...
cd d %~dp0
python dump_create.py
echo.
pause