@echo off
cd /d "%~dp0"
echo Running index refresh...
echo This may take several minutes on first run.
python index_create.py
pause
