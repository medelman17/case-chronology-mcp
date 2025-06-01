@echo off
REM Windows batch file to run the Case Chronology MCP Server
cd /d "%~dp0"

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python not found in PATH >&2
    echo Please install Python 3.10+ >&2
    exit /b 1
)

REM Check if dependencies are installed
python -c "import fastmcp" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing dependencies... >&2
    python -m pip install fastmcp python-dateutil >&2
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install dependencies >&2
        echo Please run: pip install fastmcp python-dateutil >&2
        exit /b 1
    )
)

REM Run the server
python chronology_server.py