# Installation Guide

This guide provides complete installation instructions for Sentinair on all supported platforms.

## 📋 System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 18.04+, Debian 10+, Kali Linux) or Windows 10+
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 1GB free space minimum
- **CPU**: x86_64 processor

### Recommended Requirements
- **RAM**: 8GB for better ML performance
- **Storage**: 5GB for logs and models
- **CPU**: Multi-core processor for better monitoring

## 🐧 Linux Installation

### Ubuntu/Debian Installation

#### Method 1: Automated Installation Script
```bash
# Download and run the automated installer
cd /opt
sudo git clone https://github.com/yashab-cyber/sentinair.git
cd sentinair
sudo chmod +x install/install_ubuntu.sh
sudo ./install/install_ubuntu.sh
```

#### Method 2: Manual Installation
```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Install system dependencies
sudo apt install -y python3 python3-pip python3-venv git sqlite3 \
    libqt5gui5 libqt5widgets5 libqt5core5a python3-pyqt5 \
    build-essential python3-dev libssl-dev

# 3. Clone Sentinair repository
cd /opt
sudo git clone https://github.com/yashab-cyber/sentinair.git
cd sentinair

# 4. Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 5. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Set up permissions
sudo chown -R $USER:$USER /opt/sentinair
chmod +x main.py

# 7. Create systemd service (optional)
sudo cp install/sentinair.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sentinair
```

### Kali Linux Installation
```bash
# Use the Kali-specific installer
cd /opt
sudo git clone https://github.com/yashab-cyber/sentinair.git
cd sentinair
sudo chmod +x install/install_kali.sh
sudo ./install/install_kali.sh
```

### CentOS/RHEL Installation
```bash
# Use the CentOS-specific installer
cd /opt
sudo git clone https://github.com/yashab-cyber/sentinair.git
cd sentinair
sudo chmod +x install/install_centos.sh
sudo ./install/install_centos.sh
```

## 🪟 Windows Installation

### Method 1: Automated PowerShell Script
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Download and run installer
git clone https://github.com/yashab-cyber/sentinair.git
cd sentinair
.\install\install_windows.ps1
```

### Method 2: Manual Windows Installation
```powershell
# 1. Install Python 3.8+ from python.org
# Download from: https://www.python.org/downloads/

# 2. Install Git for Windows
# Download from: https://git-scm.com/download/win

# 3. Clone repository
git clone https://github.com/yashab-cyber/sentinair.git
cd sentinair

# 4. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 5. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 6. Install as Windows service (optional)
.\install\install_windows.bat
```

## 🛠️ Post-Installation Setup

### 1. Initial Configuration
```bash
# Navigate to Sentinair directory
cd /opt/sentinair  # Linux
# or
cd C:\sentinair   # Windows

# Copy default configuration
cp config/default.yaml config/sentinair.yaml

# Edit configuration (optional)
nano config/sentinair.yaml  # Linux
notepad config\sentinair.yaml  # Windows
```

### 2. Generate Initial Training Data
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux
.venv\Scripts\activate     # Windows

# Generate training data
python generate_training_data.py
```

### 3. Test Installation
```bash
# Test core functionality
python main.py --help

# Start in CLI mode for testing
python main.py --mode cli
```

### 4. Set Up System Service (Linux)
```bash
# Enable systemd service
sudo systemctl enable sentinair
sudo systemctl start sentinair
sudo systemctl status sentinair
```

### 5. Set Up Windows Service
```powershell
# Run as Administrator
sc create Sentinair binPath= "C:\sentinair\.venv\Scripts\python.exe C:\sentinair\main.py --mode stealth"
sc config Sentinair start= auto
sc start Sentinair
```

## 🔧 Installation Verification

### Basic Functionality Test
```bash
# Test imports and basic functionality
python -c "
from core.engine import SentinairEngine
from utils.config import Config
config = Config()
engine = SentinairEngine(config)
print('✅ Sentinair installation successful!')
"
```

### Full System Test
```bash
# Run comprehensive test
python main.py --mode cli --log-level INFO
# In CLI: type 'status' and 'help' to verify functionality
```

## 🚨 Troubleshooting Installation

### Common Issues

#### Permission Denied Errors (Linux)
```bash
# Fix ownership
sudo chown -R $USER:$USER /opt/sentinair

# Fix permissions
chmod +x main.py
chmod +x install/*.sh
```

#### Python Module Import Errors
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt --no-cache-dir
```

#### Qt/GUI Issues (Linux)
```bash
# Install additional Qt dependencies
sudo apt install -y python3-pyqt5.qtsql python3-pyqt5.qtwidgets
```

#### Windows Path Issues
```powershell
# Add Python to PATH
$env:PATH += ";C:\Python39;C:\Python39\Scripts"
```

### Getting Help
- Check the [Troubleshooting Guide](13-troubleshooting.md)
- Review system logs: `data/logs/sentinair.log`
- Verify Python version: `python --version`
- Check dependencies: `pip list`

## 📦 Package Managers

### Debian/Ubuntu APT Package (Future)
```bash
# Coming soon - APT repository
sudo apt install sentinair
```

### Python PyPI Package (Future)
```bash
# Coming soon - PyPI package
pip install sentinair
```

### Docker Container (Future)
```bash
# Coming soon - Docker image
docker run -d --name sentinair sentinair/sentinair:latest
```

## 🔄 Updating Sentinair

### Git Update
```bash
cd /opt/sentinair
git pull origin main
pip install -r requirements.txt --upgrade
```

### Service Restart
```bash
# Linux
sudo systemctl restart sentinair

# Windows
sc stop Sentinair
sc start Sentinair
```

---

**Next**: [Quick Start Guide](02-quickstart.md)
