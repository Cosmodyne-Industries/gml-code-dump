@echo off
cd /d "%~dp0"
echo GML Code Extractor
echo Usage: enter object or script name when prompted, e.g. obj_player or scr_my_script
echo For objects, include the event: obj_player:Create_0
echo Separate multiple requests with spaces: obj_player:Create_0 scr_my_script
echo.
set /p REQUEST="Enter request(s): "
python extract.py %REQUEST%
pause
