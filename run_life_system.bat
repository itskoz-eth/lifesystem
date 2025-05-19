@echo off
echo Starting Life System batch script...

REM Set the working directory to where the batch file is located
cd /D "%~dp0"
echo Current directory set to: %CD%
pause

REM Activate the virtual environment
echo Activating virtual environment...
CALL .\venv311\Scripts\activate.bat
if errorlevel 1 (
    echo FAILED TO ACTIVATE VIRTUAL ENVIRONMENT.
    pause
    exit /b
)
echo Virtual environment activated.
echo Current directory after venv activation: %CD%
echo Python executable should be: %VIRTUAL_ENV%\Scripts\python.exe
pause

REM Run the main Python script as a module
echo Attempting to run: python -m src.main
python -m src.main
if errorlevel 1 (
    echo PYTHON SCRIPT FAILED TO EXECUTE OR EXITED WITH ERROR.
) else (
    echo Python script completed.
)

echo Script finished. Press any key to close this window...
pause 