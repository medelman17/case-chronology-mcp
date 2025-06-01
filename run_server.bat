@echo off
REM Windows batch file to run the Case Chronology MCP Server

REM Check if uvx is available
where uvx >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Running with uvx...
    uvx --with fastmcp --with python-dateutil chronology_server.py
) else (
    REM Check if Python is available
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo Running with Python...
        python chronology_server.py
    ) else (
        echo Error: Neither uvx nor Python found in PATH
        echo Please install Python 3.10+ or uv
        exit /b 1
    )
)