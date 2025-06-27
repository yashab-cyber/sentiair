# Sentinair - Offline AI-Powered Behavioral Threat Detection System

*Created by Yashab Alam, Founder of ZehraSec*

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![AI Powered](https://img.shields.io/badge/AI-Powered-orange.svg)
![Offline](https://img.shields.io/badge/offline-capable-brightgreen.svg)
![Security](https://img.shields.io/badge/security-threat%20detection-red.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)
![GitHub Issues](https://img.shields.io/github/issues/yashab-cyber/sentinair)
![GitHub Stars](https://img.shields.io/github/stars/yashab-cyber/sentinair)
![GitHub Forks](https://img.shields.io/github/forks/yashab-cyber/sentinair)
![GitHub Last Commit](https://img.shields.io/github/last-commit/yashab-cyber/sentinair)

## Overview
Sentinair is an advanced offline AI-based Intrusion Detection System tailored for isolated environments such as air-gapped military, industrial, or banking systems. It monitors system behavior patterns and flags anomalies using machine learning - all without needing internet connectivity.

## Features
- **Behavioral Tracking Engine**: Monitors file access patterns, USB device events, application launches, system activity, and user interaction patterns
- **Local ML Anomaly Detection**: Uses unsupervised machine learning (Isolation Forest/Autoencoders) to detect behavioral deviations
- **Offline Alerting System**: GUI alerts, CLI support, and manual export capabilities
- **Report Generation**: Detailed logs in PDF/CSV format with optional YARA rule integration
- **Stealth Mode**: Hidden background operation with admin authentication
- **Cross-Platform**: Supports Linux (Debian/Kali/Ubuntu) and Windows 10+

## 💰 Support This Project

Sentinair is an open-source project that relies on community support. If you find this tool valuable, please consider supporting its development:

- 🌟 **Star this repository** to show your support
- 💵 **Make a donation** to fund development - see [DONATE.md](DONATE.md) for details
- 🤝 **Contribute code** by submitting pull requests
- 📝 **Report issues** to help improve the project
- 📢 **Share** with others who might benefit from this tool

**Your support helps us:**
- Improve AI detection models
- Add new features and capabilities
- Maintain cross-platform compatibility
- Provide better documentation and support

👉 **[View Donation Options](DONATE.md)**

## Installation

### Automated Installation Scripts

For production deployment, use the automated installation scripts in the `install/` directory:

#### Linux
```bash
# Ubuntu/Debian
chmod +x install/install_ubuntu.sh
sudo ./install/install_ubuntu.sh

# CentOS/RHEL/Fedora  
chmod +x install/install_centos.sh
sudo ./install/install_centos.sh

# Kali Linux
chmod +x install/install_kali.sh
sudo ./install/install_kali.sh
```

#### Windows
```powershell
# PowerShell (Recommended - includes service installation)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install\install_windows.ps1

# Or use the batch script
.\install\install_windows.bat
```

### Manual Installation

#### Prerequisites
- Python 3.8+
- SQLite3
- Required Python packages (see requirements.txt)

#### Setup
```bash
# Clone or extract the project
cd sentinair

# Install dependencies
pip install -r requirements.txt

# Initialize the system
python setup.py

# Run the application
python main.py
```

## 🚀 Quick Start

```bash
# 1. Extract/clone the project
cd sentinair

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run initial setup
python setup.py

# 4. Start the application
python main.py --gui    # GUI mode
python main.py --cli    # CLI mode
python main.py --stealth # Background mode
```

## 📚 Documentation

### Complete User Manual
The `/manual` directory contains comprehensive documentation:

- **[Installation Guide](manual/01-installation.md)** - Detailed setup instructions for all platforms
- **[Quick Start Guide](manual/02-quickstart.md)** - Get up and running in minutes
- **[Configuration Guide](manual/03-configuration.md)** - Customize system settings
- **[GUI User Guide](manual/04-gui-guide.md)** - Navigate the graphical interface
- **[CLI User Guide](manual/05-cli-guide.md)** - Master the command line
- **[Machine Learning Guide](manual/10-machine-learning.md)** - Understanding AI detection
- **[Troubleshooting](manual/13-troubleshooting.md)** - Solve common issues
- **[Command Reference](manual/18-command-reference.md)** - Complete command guide

👉 **Start with the [Manual Overview](manual/README.md)**

### Additional Documentation
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment checklist
- **[User Guide](USER_GUIDE.md)** - Legacy user documentation
- **[Contributing](CONTRIBUTING.md)** - Development and contribution guidelines
- **[Security Policy](SECURITY.md)** - Security practices and reporting

## Architecture

### Core Components

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **core/** | Main detection engine and monitors | `engine.py`, `monitors/` |
| **ml/** | Machine learning anomaly detection | `anomaly_detector.py` |
| **gui/** | Graphical user interface | `main_window.py`, dashboard/alerts widgets |
| **cli/** | Command-line interface | `cli_interface.py` |
| **alerts/** | Alert management system | `alert_manager.py` |
| **reports/** | Report generation | `report_generator.py` |
| **utils/** | Core utilities | `config.py`, `database.py`, `logger.py` |
| **config/** | Configuration files | `default.yaml` |
| **signatures/** | YARA detection rules | `default.yar` |
| **install/** | Installation scripts | Platform-specific installers |
| **manual/** | User documentation | Comprehensive guides |

### Monitoring Capabilities
- **File System**: Track file access, creation, deletion, and modifications
- **USB Devices**: Monitor device insertion/removal and suspicious devices  
- **Processes**: Application launches and executable analysis
- **User Behavior**: Privacy-preserving activity pattern analysis

## Security Features
- **Offline Operation**: No internet connectivity required
- **Encrypted Storage**: AES-encrypted local data storage
- **Self-Contained**: Complete standalone operation
- **Admin Authentication**: Secure access for sensitive operations
- **Stealth Mode**: Hidden background operation

## License
MIT License - See [LICENSE](LICENSE) file for details

## Production Ready
This project has been cleaned and prepared for deployment:
- ✅ All test and debug files removed
- ✅ Comprehensive documentation in `/manual` directory  
- ✅ Production installation scripts ready
- ✅ Security hardened and validated
- ✅ See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment checklist

## 🏢 About ZehraSec

**Sentinair** is developed by **[ZehraSec](https://www.zehrasec.com)**, a cybersecurity company founded by **Yashab Alam**.

**Connect with ZehraSec:**
- 🌐 **Website:** [www.zehrasec.com](https://www.zehrasec.com)
- 📸 **Instagram:** [@_zehrasec](https://www.instagram.com/_zehrasec?igsh=bXM0cWl1ejdoNHM4)
- 🐦 **X (Twitter):** [@zehrasec](https://x.com/zehrasec?t=Tp9LOesZw2d2yTZLVo0_GA&s=08)
- 💼 **LinkedIn:** [ZehraSec Company](https://www.linkedin.com/company/zehrasec)

**Connect with Yashab Alam:**
- 💻 **GitHub:** [@yashab-cyber](https://github.com/yashab-cyber)
- 📸 **Instagram:** [@yashab.alam](https://www.instagram.com/yashab.alam)
- 💼 **LinkedIn:** [Yashab Alam](https://www.linkedin.com/in/yashabalam)

---

**🛡️ Made with ❤️ by Yashab Alam (Founder of ZehraSec)**

*© 2025 ZehraSec. Released under MIT License.*
