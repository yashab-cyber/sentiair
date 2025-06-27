# Sentinair User Guide

> **📚 NEW: Comprehensive Manual Available**  
> For the most up-to-date and detailed documentation, please see the new structured manual in the `/manual` directory:
> - **[Manual Overview](manual/README.md)** - Complete documentation index
> - **[Installation Guide](manual/01-installation.md)** - Detailed setup instructions
> - **[Quick Start Guide](manual/02-quickstart.md)** - Get started quickly
> - **[Configuration Guide](manual/03-configuration.md)** - System configuration
> - **[GUI Guide](manual/04-gui-guide.md)** & **[CLI Guide](manual/05-cli-guide.md)** - Interface guides
> - **[Troubleshooting](manual/13-troubleshooting.md)** - Problem solving
>
> This document remains available for reference but may not be as current as the manual.

---

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Features](#features)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)

## Overview

Sentinair is an advanced offline AI-based Intrusion Detection System tailored for isolated environments such as air-gapped military, industrial, or banking systems. It monitors system behavior patterns and flags anomalies using machine learning - all without needing internet connectivity.

### Key Features
- **Offline Operation**: No internet connection required
- **AI-Powered Detection**: Uses machine learning for behavioral analysis
- **Real-time Monitoring**: Continuous system monitoring
- **Multiple Interfaces**: GUI, CLI, and stealth modes
- **Comprehensive Reporting**: PDF and CSV reports
- **Cross-Platform**: Supports Windows and Linux

## Installation

### Prerequisites
- Python 3.8 or higher
- 2GB+ RAM recommended
- 1GB+ available disk space
- Administrator privileges (for some monitoring features)

### Quick Installation
```bash
# Clone or extract Sentinair files
cd sentinair

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py

# Start the application
python main.py
```

### Detailed Installation Steps

1. **Download Sentinair**
   ```bash
   # Extract the Sentinair package to your desired location
   cd /path/to/sentinair
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt --user
   ```

3. **Run Initial Setup**
   ```bash
   python setup.py
   ```
   This will:
   - Create necessary directories
   - Initialize the database
   - Generate encryption keys
   - Set up configuration files
   - Configure admin password for stealth mode

4. **Verify Installation**
   ```bash
   python main.py --mode cli
   ```

## Configuration

### Configuration File
The main configuration is stored in `config/default.yaml`. Key settings include:

```yaml
# Detection Settings
detection:
  anomaly_threshold: 0.7        # Sensitivity (0.0-1.0)
  training_interval_hours: 24   # How often to retrain
  min_training_samples: 1000    # Minimum data for training

# Machine Learning
ml:
  model_type: "isolation_forest"  # or "autoencoder"
  contamination_rate: 0.1         # Expected percentage of anomalies

# Security
security:
  encrypt_logs: true              # Encrypt stored data
  stealth_mode: false            # Enable stealth operation
```

### Monitor Configuration
Enable/disable specific monitoring components:

```yaml
detection:
  track_file_access: true      # Monitor file system access
  track_usb_events: true       # Monitor USB device events
  track_app_launches: true     # Monitor process launches
  track_user_behavior: true    # Monitor user interaction patterns
```

## Usage

### GUI Mode (Recommended for new users)
```bash
python main.py --mode gui
```

Features:
- Real-time dashboard with system status
- Alert management interface
- Configuration editor
- Report generation
- System statistics

### CLI Mode (For advanced users)
```bash
python main.py --mode cli
```

Available commands:
- `status` - Show system status
- `start` - Begin monitoring
- `stop` - Stop monitoring
- `alerts` - Show recent alerts
- `config` - View/modify configuration
- `report` - Generate reports

### Stealth Mode (For covert operation)
```bash
python main.py --mode stealth --stealth-key YOUR_PASSWORD
```

Stealth mode features:
- Runs in background without visible interface
- Minimal system footprint
- Requires password authentication
- Suitable for long-term deployment

## Features

### Behavioral Monitoring

**File Access Monitoring**
- Tracks file system access patterns
- Detects unusual file operations
- Monitors sensitive directories
- Flags suspicious file extensions

**USB Device Monitoring**
- Detects USB device insertion/removal
- Identifies unknown devices
- Monitors data transfer patterns
- Flags suspicious device characteristics

**Process Monitoring**
- Tracks application launches
- Monitors process behavior
- Detects suspicious executables
- Analyzes command line arguments

**User Behavior Analysis**
- Monitors typing patterns (privacy-preserving)
- Tracks application usage
- Detects unusual activity times
- Analyzes idle/active periods

### Machine Learning Models

**Isolation Forest (Default)**
- Unsupervised anomaly detection
- Fast training and prediction
- Good for general anomaly detection
- Requires minimal configuration

**Autoencoder (Advanced)**
- Deep learning based detection
- More sensitive to subtle anomalies
- Requires more computational resources
- Better for complex behavior patterns

### Alert System

**Severity Levels**
- **Critical**: Immediate attention required
- **High**: Potentially serious threat
- **Medium**: Unusual but not immediately dangerous
- **Low**: Minor deviation from normal

**Alert Actions**
- Desktop notifications
- Log file entries
- Email export (manual)
- Report generation

### Reporting

**Daily Reports**
- System status summary
- Alert statistics
- Behavioral analysis
- Recommendations

**Weekly Reports**
- Trend analysis
- Performance metrics
- Historical comparisons
- Executive summary

**Incident Reports**
- Detailed alert analysis
- Timeline reconstruction
- Impact assessment
- Response recommendations

## API Reference

### Basic Usage
```python
from utils.config import Config
from core.engine import SentinairEngine

# Initialize
config = Config("config/default.yaml")
engine = SentinairEngine(config)

# Start monitoring
engine.start()

# Get status
status = engine.get_status()
print(f"Running: {status['running']}")

# Get alerts
alerts = engine.get_recent_alerts(hours=24)

# Stop monitoring
engine.stop()
```

### Configuration Management
```python
from utils.config import Config

config = Config("config/default.yaml")

# Get configuration value
threshold = config.get('detection.anomaly_threshold')

# Set configuration value
config.set('detection.anomaly_threshold', 0.8)
config.save_config()
```

### Custom Alert Handling
```python
from alerts.alert_manager import AlertManager

alert_manager = AlertManager(config)

# Create custom alert
alert_data = {
    'timestamp': datetime.now(),
    'severity': 'medium',
    'description': 'Custom alert',
    'confidence': 0.8
}

alert_id = alert_manager.create_alert(alert_data)
```

## Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt --user

# Check Python path
python -c "import sys; print(sys.path)"
```

**Permission denied errors**
```bash
# Run with appropriate privileges
# On Linux: sudo python main.py
# On Windows: Run as Administrator
```

**Database errors**
```bash
# Re-initialize database
python setup.py
```

**High CPU usage**
- Reduce monitoring scope in configuration
- Increase training interval
- Use Isolation Forest instead of Autoencoder

**False positives**
- Increase anomaly threshold
- Increase training data collection period
- Fine-tune model parameters

### Log Files
- Application logs: `logs/sentinair.log`
- Error logs: `logs/error.log`
- Database: `data/sentinair.db`

### Performance Optimization

**For Low-Resource Systems**
```yaml
detection:
  training_interval_hours: 48  # Train less frequently
ml:
  model_type: "isolation_forest"  # Use simpler model
  n_estimators: 50  # Reduce complexity
```

**For High-Security Environments**
```yaml
detection:
  anomaly_threshold: 0.5  # More sensitive
  training_interval_hours: 12  # Train more frequently
security:
  encrypt_logs: true
  tamper_detection: true
```

### Getting Help

1. Check the logs for error messages
2. Review configuration settings
3. Try running in CLI mode for detailed output
4. Use the example scripts for testing

### System Requirements by Mode

**GUI Mode**
- 4GB RAM recommended
- Graphics support required
- 500MB+ available storage

**CLI Mode**
- 2GB RAM minimum
- No graphics required
- 200MB+ available storage

**Stealth Mode**
- 1GB RAM minimum
- Minimal system resources
- 100MB+ available storage

## Security Considerations

### Data Protection
- All logs can be encrypted
- Secure deletion of old data
- No network communication
- Local-only operation

### Access Control
- Admin password protection
- File permission management
- Process isolation
- Tamper detection

### Deployment Best Practices
1. Run initial setup with administrator privileges
2. Configure appropriate monitoring scope
3. Set up regular maintenance schedules
4. Monitor system performance impact
5. Regularly review and update YARA rules

---

*For additional support or questions, refer to the example scripts in the `examples/` directory.*
