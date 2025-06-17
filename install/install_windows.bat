@echo off
REM Sentinair Windows Installation Script (Batch Version)
REM This is a simplified batch version of the PowerShell installer
REM For full features, use install_windows.ps1

setlocal enabledelayedexpansion

echo =====================================
echo Sentinair Windows Installation Script
echo =====================================
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo ERROR: main.py not found!
    echo Please run this script from the Sentinair source directory.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found!
    echo Please run this script from the Sentinair source directory.
    pause
    exit /b 1
)

REM Set installation directory
set "INSTALL_DIR=%ProgramFiles%\Sentinair"

echo Checking Python installation...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to add Python to PATH during installation.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python !PYTHON_VERSION!

REM Check Python version (basic check for 3.x)
echo !PYTHON_VERSION! | findstr /r "^3\.[8-9]\|^3\.1[0-9]" >nul
if !errorlevel! neq 0 (
    echo WARNING: Python 3.8+ recommended. Current version: !PYTHON_VERSION!
    echo Continue anyway? (Y/N)
    set /p CONTINUE=
    if /i "!CONTINUE!" neq "Y" exit /b 1
)

echo.
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Creating installation directory...
if not exist "!INSTALL_DIR!" (
    mkdir "!INSTALL_DIR!" 2>nul
    if !errorlevel! neq 0 (
        echo ERROR: Could not create installation directory: !INSTALL_DIR!
        echo Try running as Administrator or choose a different location.
        pause
        exit /b 1
    )
)

echo.
echo Copying files to installation directory...
xcopy /E /Y /Q . "!INSTALL_DIR!\" >nul
if !errorlevel! neq 0 (
    echo ERROR: Failed to copy files!
    pause
    exit /b 1
)

REM Remove installation files from target directory
if exist "!INSTALL_DIR!\install" rmdir /s /q "!INSTALL_DIR!\install"

echo.
echo Installing Sentinair as Python package...
cd /d "!INSTALL_DIR!"
python setup.py install >nul 2>&1

echo.
echo Creating startup script...
(
echo @echo off
echo cd /d "!INSTALL_DIR!"
echo python main.py %%*
echo pause
) > "!INSTALL_DIR!\sentinair.bat"

echo.
echo Creating desktop shortcut...
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Sentinair.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '!INSTALL_DIR!\main.py'; $Shortcut.WorkingDirectory = '!INSTALL_DIR!'; $Shortcut.Description = 'Sentinair - AI-powered behavioral threat detection system'; $Shortcut.Save()}" >nul 2>&1

echo.
echo =====================================
echo Installation Complete!
echo =====================================
echo.
echo Installation Directory: !INSTALL_DIR!
echo.
echo Quick Start:
echo   1. Run: "!INSTALL_DIR!\sentinair.bat"
echo   2. Or: cd "!INSTALL_DIR!" ^&^& python main.py
echo   3. Or: Double-click Desktop shortcut
echo.
echo Configuration:
echo   Main config: !INSTALL_DIR!\config\default.yaml
echo   Signatures: !INSTALL_DIR!\signatures\default.yar
echo.
echo Documentation:
echo   README: !INSTALL_DIR!\README.md
echo   User Guide: !INSTALL_DIR!\USER_GUIDE.md
echo.
echo For help: python main.py --help
echo.
echo NOTE: For advanced features (Windows service, etc.),
echo       use the PowerShell version: install_windows.ps1
echo =====================================

cd /d "!INSTALL_DIR!"
pause
