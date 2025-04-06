@echo off
echo Creating virtual environment...

call python -m venv venv

echo Installing dependencies...
REM Activate virtual environment
call %~dp0\venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

echo.
echo Installation complete.
echo You can now use 'run.bat' to execute the tools.

REM Deactivate virtual environment
deactivate

pause
