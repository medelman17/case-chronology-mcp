@echo off
REM Windows batch file to run the Case Chronology MCP Server
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found >&2
    echo Please run setup.bat first >&2
    exit /b 1
)

REM Activate virtual environment and run the server
call venv\Scripts\activate.bat && python chronology_server.py