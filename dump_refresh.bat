@echo off
echo Running digest builder...
cd d %~dp0
python dump_create.py
echo.
pause