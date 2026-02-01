@echo off
REM EchoLog Windows Launcher
REM ========================
REM Run this script to start EchoLog on Windows

REM Get the directory where the script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..\..\

REM Activate virtual environment
if exist "%PROJECT_ROOT%\venv\Scripts\activate.bat" (
    call "%PROJECT_ROOT%\venv\Scripts\activate.bat"
) else (
    echo Creating virtual environment...
    python -m venv "%PROJECT_ROOT%\venv"
    call "%PROJECT_ROOT%\venv\Scripts\activate.bat"
    pip install -r "%PROJECT_ROOT%\requirements.txt"
)

REM Check if .env file exists
if not exist "%PROJECT_ROOT%\.env" (
    echo .env file not found. Creating from example...
    if exist "%PROJECT_ROOT%\.env.example" (
        copy "%PROJECT_ROOT%\.env.example" "%PROJECT_ROOT%\.env"
        echo Please edit .env file to add your DEEPGRAM_API_KEY
    )
)

REM Run the Windows GUI
cd /d "%PROJECT_ROOT%"
python main_gui.py
