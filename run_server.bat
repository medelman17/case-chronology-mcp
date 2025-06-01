@echo off
REM Windows batch file to run the Case Chronology MCP Server

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python "%~dp0chronology_server.py"
) else (
    echo Error: Python not found in PATH >&2
    echo Please install Python 3.10+ >&2
    exit /b 1
)