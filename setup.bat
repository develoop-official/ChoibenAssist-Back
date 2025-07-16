@echo off
setlocal

REM ChoibenAssist AI Backend - Setup Script
REM Python環境セットアップと開発タスクの自動化

set PYTHON=python
set VENV=.venv
set REQUIREMENTS=requirements.txt
set REQUIREMENTS_DEV=requirements-dev.txt


REM Create virtual environment
if not exist "%VENV%" (
    echo Creating virtual environment...
    %PYTHON% -m venv %VENV%
    echo Virtual environment created at %VENV%
) else (
    echo Virtual environment already exists
)

REM Install dependencies
if exist "%VENV%" (
    echo Installing dependencies...
    %VENV%\Scripts\pip install --upgrade pip setuptools wheel
    %VENV%\Scripts\pip install --no-cache-dir -r %REQUIREMENTS%
    %VENV%\Scripts\pip install --no-cache-dir -r %REQUIREMENTS_DEV%
    echo Dependencies installed
) else (
    echo Virtual environment not found. Please create it first.
)

REM Setup environment variables
if not exist ".env" (
    echo Setting up environment variables...
    copy .env.example .env
    echo .env file created from .env.example
    echo Please edit .env file with your actual values
) else (
    echo .env file already exists
)

REM Verify setup
if exist "%VENV%" (
    echo Verifying setup...
    %VENV%\Scripts\python --version
    %VENV%\Scripts\pip --version
    if exist ".env" (
        echo Environment file exists
    ) else (
        echo Environment file missing
    )
    echo Setup verification complete
) else (
    echo Virtual environment not found. Please create it first.
)

endlocal
