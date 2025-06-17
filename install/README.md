# Sentinair Installation Scripts

This directory contains installation scripts for different operating systems and distributions.

## Linux Installation

### Ubuntu/Debian
```bash
chmod +x install_ubuntu.sh
sudo ./install_ubuntu.sh
```

### CentOS/RHEL/Fedora
```bash
chmod +x install_centos.sh
sudo ./install_centos.sh
```

### Kali Linux
```bash
chmod +x install_kali.sh
sudo ./install_kali.sh
```

## Windows Installation

### PowerShell Script (Recommended)
The PowerShell script provides full functionality including:
- Automatic Python installation
- Windows service creation
- Windows Defender configuration
- Desktop shortcuts

```powershell
# Run as Administrator for full functionality
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install_windows.ps1
```

**Parameters:**
- `-SkipPython`: Skip Python installation
- `-DevMode`: Install in development mode
- `-InstallDir`: Custom installation directory

**Examples:**
```powershell
# Basic installation
.\install_windows.ps1

# Skip Python installation
.\install_windows.ps1 -SkipPython

# Custom installation directory
.\install_windows.ps1 -InstallDir "C:\MyPrograms\Sentinair"

# Development mode
.\install_windows.ps1 -DevMode
```

### Batch Script (Simple)
For users who prefer traditional batch scripts:

```cmd
REM Run as Administrator
install_windows.bat
```

## Prerequisites

### Linux
- Python 3.8 or higher
- pip (Python package manager)
- System package manager (apt, yum, dnf, or pacman)
- Root/sudo access

### Windows
- Windows 10 or later
- PowerShell 5.1 or later (for PowerShell script)
- Administrator privileges (recommended)

## Post-Installation

After successful installation, Sentinair will be available:

### Linux
- Command line: `sentinair` or `python -m sentinair`
- Service: `systemctl start sentinair`
- Configuration: `/etc/sentinair/` or `~/.config/sentinair/`

### Windows
- Command line: `sentinair.bat` or `python main.py`
- Service: Use `service.ps1` script
- Desktop shortcut: Available on desktop
- Configuration: `%ProgramFiles%\Sentinair\config\`

## Troubleshooting

### Common Issues

1. **Permission Denied**: Run with administrator/root privileges
2. **Python Not Found**: Ensure Python 3.8+ is installed and in PATH
3. **Package Installation Failed**: Check internet connection and proxy settings
4. **Service Won't Start**: Check logs in the installation directory

### Getting Help

- Check the main README.md for detailed documentation
- Review USER_GUIDE.md for usage instructions
- Check logs in the installation directory
- Report issues on the project repository

## Uninstallation

### Linux
```bash
# Remove service
sudo systemctl stop sentinair
sudo systemctl disable sentinair
sudo rm /etc/systemd/system/sentinair.service

# Remove files
sudo rm -rf /opt/sentinair
sudo rm -rf /etc/sentinair
sudo rm /usr/local/bin/sentinair

# Remove Python package
pip uninstall sentinair
```

### Windows
```powershell
# Stop and remove service (if installed)
.\service.ps1 stop
.\service.ps1 uninstall

# Remove installation directory
Remove-Item -Path "C:\Program Files\Sentinair" -Recurse -Force

# Remove desktop shortcut
Remove-Item -Path "$env:USERPROFILE\Desktop\Sentinair.lnk"

# Remove Python package
pip uninstall sentinair
```
