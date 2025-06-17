#!/usr/bin/env powershell
<#
.SYNOPSIS
    Installation script for Sentinair on Windows
.DESCRIPTION
    This script installs Sentinair - AI-powered behavioral threat detection system
    for Windows systems. It handles Python installation, dependency management,
    and system configuration.
.NOTES
    Author: Sentinair Development Team
    Version: 1.0.0
    Requires: PowerShell 5.1 or later
#>

param(
    [switch]$SkipPython,
    [switch]$DevMode,
    [string]$InstallDir = "$env:ProgramFiles\Sentinair"
)

# Set execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = $Reset
    )
    Write-Host "$Color$Message$Reset"
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Python {
    Write-ColorOutput "Checking Python installation..." $Blue
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.([8-9]|1[0-9])") {
            Write-ColorOutput "✓ Python 3.8+ found: $pythonVersion" $Green
            return $true
        }
    }
    catch {
        Write-ColorOutput "Python not found in PATH" $Yellow
    }
    
    if ($SkipPython) {
        Write-ColorOutput "Skipping Python installation as requested" $Yellow
        return $false
    }
    
    Write-ColorOutput "Installing Python 3.11..." $Blue
    
    # Download Python installer
    $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
        
        # Install Python silently
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        
        # Verify installation
        Start-Sleep -Seconds 5
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.") {
            Write-ColorOutput "✓ Python installed successfully: $pythonVersion" $Green
            return $true
        }
        else {
            Write-ColorOutput "✗ Python installation verification failed" $Red
            return $false
        }
    }
    catch {
        Write-ColorOutput "✗ Failed to install Python: $($_.Exception.Message)" $Red
        return $false
    }
    finally {
        if (Test-Path $pythonInstaller) {
            Remove-Item $pythonInstaller -Force
        }
    }
}

function Install-Dependencies {
    Write-ColorOutput "Installing Python dependencies..." $Blue
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    if (Test-Path "requirements.txt") {
        python -m pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Dependencies installed successfully" $Green
        }
        else {
            Write-ColorOutput "✗ Failed to install some dependencies" $Red
            return $false
        }
    }
    else {
        Write-ColorOutput "✗ requirements.txt not found" $Red
        return $false
    }
    
    return $true
}

function Install-Sentinair {
    param([string]$TargetDir)
    
    Write-ColorOutput "Installing Sentinair to $TargetDir..." $Blue
    
    try {
        # Create installation directory
        if (-not (Test-Path $TargetDir)) {
            New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
        }
        
        # Copy files
        $excludePatterns = @("*.pyc", "__pycache__", ".git", ".pytest_cache", "*.log", "install")
        
        Get-ChildItem -Path "." -Recurse | Where-Object {
            $exclude = $false
            foreach ($pattern in $excludePatterns) {
                if ($_.Name -like $pattern -or $_.FullName -match $pattern.Replace("*", ".*")) {
                    $exclude = $true
                    break
                }
            }
            -not $exclude
        } | Copy-Item -Destination {
            $dest = $_.FullName.Replace((Get-Location).Path, $TargetDir)
            $destDir = Split-Path $dest -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            $dest
        } -Force
        
        Write-ColorOutput "✓ Files copied successfully" $Green
        
        # Install as Python package
        Push-Location $TargetDir
        python setup.py install
        Pop-Location
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Sentinair installed as Python package" $Green
        }
        else {
            Write-ColorOutput "⚠ Package installation completed with warnings" $Yellow
        }
        
        return $true
    }
    catch {
        Write-ColorOutput "✗ Installation failed: $($_.Exception.Message)" $Red
        return $false
    }
}

function Create-StartupScript {
    param([string]$InstallDir)
    
    Write-ColorOutput "Creating startup scripts..." $Blue
    
    # Create batch file for easy execution
    $batchContent = @"
@echo off
cd /d "$InstallDir"
python main.py %*
pause
"@
    
    $batchFile = "$InstallDir\sentinair.bat"
    $batchContent | Out-File -FilePath $batchFile -Encoding ASCII
    
    # Create PowerShell script
    $psContent = @"
#!/usr/bin/env powershell
Set-Location "$InstallDir"
python main.py @args
"@
    
    $psFile = "$InstallDir\sentinair.ps1"
    $psContent | Out-File -FilePath $psFile -Encoding UTF8
    
    # Create desktop shortcut
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Sentinair.lnk")
    $Shortcut.TargetPath = "python"
    $Shortcut.Arguments = "$InstallDir\main.py"
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.IconLocation = "python.exe"
    $Shortcut.Description = "Sentinair - AI-powered behavioral threat detection system"
    $Shortcut.Save()
    
    Write-ColorOutput "✓ Startup scripts created" $Green
    Write-ColorOutput "  - Batch file: $batchFile" $Blue
    Write-ColorOutput "  - PowerShell: $psFile" $Blue
    Write-ColorOutput "  - Desktop shortcut: $env:USERPROFILE\Desktop\Sentinair.lnk" $Blue
}

function Configure-WindowsDefender {
    Write-ColorOutput "Configuring Windows Defender exclusions..." $Blue
    
    if (Test-Administrator) {
        try {
            # Add Sentinair directory to exclusions
            Add-MpPreference -ExclusionPath $InstallDir -ErrorAction SilentlyContinue
            
            # Add Sentinair processes to exclusions
            Add-MpPreference -ExclusionProcess "python.exe" -ErrorAction SilentlyContinue
            Add-MpPreference -ExclusionProcess "sentinair.exe" -ErrorAction SilentlyContinue
            
            Write-ColorOutput "✓ Windows Defender exclusions configured" $Green
        }
        catch {
            Write-ColorOutput "⚠ Could not configure Windows Defender exclusions" $Yellow
        }
    }
    else {
        Write-ColorOutput "⚠ Administrator privileges required for Windows Defender configuration" $Yellow
    }
}

function Create-ServiceScript {
    param([string]$InstallDir)
    
    Write-ColorOutput "Creating Windows service script..." $Blue
    
    $serviceScript = @"
#!/usr/bin/env powershell
# Sentinair Windows Service Management Script

param(
    [Parameter(Mandatory=`$true)]
    [ValidateSet("install", "uninstall", "start", "stop", "restart", "status")]
    [string]`$Action
)

`$ServiceName = "Sentinair"
`$ServicePath = "$InstallDir\main.py"
`$PythonPath = (Get-Command python).Source

function Install-Service {
    sc.exe create `$ServiceName binPath= "`"`$PythonPath`" `"`$ServicePath`" --service" start= auto
    if (`$LASTEXITCODE -eq 0) {
        Write-Host "✓ Service installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install service" -ForegroundColor Red
    }
}

function Uninstall-Service {
    sc.exe delete `$ServiceName
    if (`$LASTEXITCODE -eq 0) {
        Write-Host "✓ Service uninstalled successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to uninstall service" -ForegroundColor Red
    }
}

function Start-SentinairService {
    sc.exe start `$ServiceName
    if (`$LASTEXITCODE -eq 0) {
        Write-Host "✓ Service started successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to start service" -ForegroundColor Red
    }
}

function Stop-SentinairService {
    sc.exe stop `$ServiceName
    if (`$LASTEXITCODE -eq 0) {
        Write-Host "✓ Service stopped successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to stop service" -ForegroundColor Red
    }
}

function Get-ServiceStatus {
    sc.exe query `$ServiceName
}

switch (`$Action) {
    "install" { Install-Service }
    "uninstall" { Uninstall-Service }
    "start" { Start-SentinairService }
    "stop" { Stop-SentinairService }
    "restart" { 
        Stop-SentinairService
        Start-Sleep -Seconds 2
        Start-SentinairService
    }
    "status" { Get-ServiceStatus }
}
"@
    
    $serviceFile = "$InstallDir\service.ps1"
    $serviceScript | Out-File -FilePath $serviceFile -Encoding UTF8
    
    Write-ColorOutput "✓ Service management script created: $serviceFile" $Green
}

function Show-PostInstallInfo {
    param([string]$InstallDir)
    
    Write-ColorOutput "`n" + "="*60 $Green
    Write-ColorOutput "Sentinair Installation Complete!" $Green
    Write-ColorOutput "="*60 $Green
    
    Write-ColorOutput "`nInstallation Directory: $InstallDir" $Blue
    Write-ColorOutput "`nQuick Start:" $Yellow
    Write-ColorOutput "  1. Run from command line: cd `"$InstallDir`" && python main.py" $Blue
    Write-ColorOutput "  2. Use batch file: $InstallDir\sentinair.bat" $Blue
    Write-ColorOutput "  3. Use PowerShell: $InstallDir\sentinair.ps1" $Blue
    Write-ColorOutput "  4. Double-click desktop shortcut: Sentinair.lnk" $Blue
    
    Write-ColorOutput "`nService Management:" $Yellow
    Write-ColorOutput "  Install service: $InstallDir\service.ps1 install" $Blue
    Write-ColorOutput "  Start service: $InstallDir\service.ps1 start" $Blue
    Write-ColorOutput "  Stop service: $InstallDir\service.ps1 stop" $Blue
    
    Write-ColorOutput "`nConfiguration:" $Yellow
    Write-ColorOutput "  Main config: $InstallDir\config\default.yaml" $Blue
    Write-ColorOutput "  Signatures: $InstallDir\signatures\default.yar" $Blue
    
    Write-ColorOutput "`nDocumentation:" $Yellow
    Write-ColorOutput "  README: $InstallDir\README.md" $Blue
    Write-ColorOutput "  User Guide: $InstallDir\USER_GUIDE.md" $Blue
    
    Write-ColorOutput "`nFor help: python main.py --help" $Yellow
    Write-ColorOutput "="*60 $Green
}

function Main {
    Write-ColorOutput "Sentinair Windows Installation Script" $Green
    Write-ColorOutput "=====================================" $Green
    
    # Check if running as administrator
    if (-not (Test-Administrator)) {
        Write-ColorOutput "⚠ Not running as administrator. Some features may not work correctly." $Yellow
        Write-ColorOutput "  Consider running as administrator for full functionality." $Yellow
    }
    
    # Check current directory
    if (-not (Test-Path "main.py") -or -not (Test-Path "requirements.txt")) {
        Write-ColorOutput "✗ Please run this script from the Sentinair source directory" $Red
        Write-ColorOutput "  Expected files: main.py, requirements.txt" $Red
        exit 1
    }
    
    # Install Python if needed
    if (-not (Install-Python)) {
        Write-ColorOutput "✗ Python installation failed. Please install Python 3.8+ manually." $Red
        exit 1
    }
    
    # Install dependencies
    if (-not (Install-Dependencies)) {
        Write-ColorOutput "✗ Dependency installation failed" $Red
        exit 1
    }
    
    # Install Sentinair
    if (-not (Install-Sentinair -TargetDir $InstallDir)) {
        Write-ColorOutput "✗ Sentinair installation failed" $Red
        exit 1
    }
    
    # Create startup scripts
    Create-StartupScript -InstallDir $InstallDir
    
    # Create service script
    Create-ServiceScript -InstallDir $InstallDir
    
    # Configure Windows Defender
    Configure-WindowsDefender
    
    # Show post-install information
    Show-PostInstallInfo -InstallDir $InstallDir
    
    Write-ColorOutput "`nInstallation completed successfully!" $Green
}

# Run main function
Main
