# Quick Start Guide

Get Sentinair up and running in minutes with this quick start guide.

## 🚀 5-Minute Quick Start

### Step 1: Verify Installation
```bash
cd /opt/sentinair
python main.py --help
```
You should see the Sentinair help message with available options.

### Step 2: Start CLI Mode
```bash
python main.py --mode cli
```

### Step 3: Basic Commands
In the CLI interface, try these commands:
```
sentinair> help      # Show all commands
sentinair> status    # Check system status
sentinair> start     # Start monitoring
sentinair> stats     # View statistics
```

### Step 4: Generate Training Data (First Time)
```bash
# In another terminal
python generate_training_data.py
```

### Step 5: Train the AI Model
```
sentinair> train     # In CLI interface
sentinair> status    # Verify model is trained
```

That's it! Sentinair is now monitoring your system.

## 🖥️ Interface Options

### GUI Mode (Recommended for Desktop)
```bash
python main.py --mode gui
```
- Full graphical interface
- Real-time dashboards
- Interactive alert management
- Easy configuration

### CLI Mode (Recommended for Servers)
```bash
python main.py --mode cli
```
- Command-line interface
- Perfect for SSH sessions
- Scriptable operations
- Low resource usage

### Stealth Mode (Background Operation)
```bash
python main.py --mode stealth --stealth-key "your-secret-key"
```
- Hidden background operation
- No visible interface
- Requires unlock key to access
- Minimal system footprint

## 📊 First-Time Setup Wizard

### 1. Configuration Check
```bash
# Check current configuration
python main.py --mode cli
sentinair> config show
```

### 2. Basic Settings
Common settings to adjust:
```yaml
# config/default.yaml
monitoring:
  file_monitoring: true      # Monitor file access
  process_monitoring: true   # Monitor processes
  usb_monitoring: true       # Monitor USB devices
  
detection:
  sensitivity: medium        # low, medium, high
  auto_train: true          # Automatic model retraining
  
alerts:
  gui_notifications: true   # Desktop notifications
  log_alerts: true         # Log to file
  email_alerts: false      # Email notifications (configure SMTP)
```

### 3. Training Data Generation
```bash
# Generate diverse training data
python generate_training_data.py

# Check data quality
python main.py --mode cli
sentinair> stats
```

### 4. Model Training
```bash
# CLI mode
sentinair> train
sentinair> status  # Check if model is ready
```

## 🎯 Common Use Cases

### Home Security Monitoring
```bash
# Start with GUI for easy monitoring
python main.py --mode gui

# Enable all monitoring modules
# Check dashboard for activity
# Review alerts in real-time
```

### Server Security (Headless)
```bash
# Start as system service
sudo systemctl start sentinair

# Monitor via CLI
python main.py --mode cli
sentinair> start
sentinair> status
```

### Air-Gapped System
```bash
# Stealth mode for sensitive environments
python main.py --mode stealth --stealth-key "air-gap-key-2025"

# Check status (requires key)
python main.py --mode cli --stealth-key "air-gap-key-2025"
```

## 📋 Daily Operations

### Morning Checklist
```bash
# Check system status
sentinair> status

# Review overnight alerts
sentinair> alerts

# Check statistics
sentinair> stats
```

### Weekly Maintenance
```bash
# Retrain model with new data
sentinair> train

# Generate reports
sentinair> report --days 7

# Clear old logs (optional)
sentinair> clear logs --older-than 30
```

## 🚨 Immediate Response Actions

### When You See an Alert
1. **Don't Panic** - Review the alert details
2. **Assess Severity** - Check the risk score and type
3. **Investigate** - Look at the event details
4. **Take Action** - Block, allow, or investigate further
5. **Document** - Acknowledge the alert with notes

### High-Priority Alerts
```bash
# View critical alerts only
sentinair> alerts --severity critical

# Get detailed information
sentinair> alerts --details <alert-id>

# Acknowledge after investigation
sentinair> alerts acknowledge <alert-id>
```

## 🔧 Quick Troubleshooting

### Sentinair Won't Start
```bash
# Check logs
tail -f data/logs/sentinair.log

# Verify configuration
python -c "from utils.config import Config; Config()"

# Test database
python -c "from utils.database import DatabaseManager; from utils.config import Config; DatabaseManager(Config())"
```

### No Alerts Being Generated
```bash
# Check if monitoring is active
sentinair> status

# Start monitoring if stopped
sentinair> start

# Check sensitivity settings
sentinair> config show detection.sensitivity
```

### Performance Issues
```bash
# Check resource usage
sentinair> stats system

# Reduce monitoring frequency
sentinair> config set monitoring.check_interval 10
```

## 📱 Remote Monitoring Setup

### SSH Access
```bash
# Connect via SSH
ssh user@your-server

# Attach to Sentinair CLI
cd /opt/sentinair
python main.py --mode cli
```

### Web Dashboard (Future Feature)
```bash
# Enable web interface (coming soon)
sentinair> config set web.enabled true
sentinair> config set web.port 8080
```

## 🎓 Learning Resources

### Essential Commands
- `help` - Show all available commands
- `status` - System status and health
- `start/stop` - Control monitoring
- `alerts` - View and manage alerts
- `stats` - System statistics
- `config` - Configuration management
- `train` - Retrain AI model

### Configuration Files
- `config/default.yaml` - Main configuration
- `data/logs/` - Log files
- `data/models/` - AI models
- `signatures/` - YARA rules

### Next Steps
1. Read the [GUI User Guide](04-gui-guide.md) for desktop use
2. Check [CLI User Guide](05-cli-guide.md) for server management
3. Review [Security Best Practices](08-security.md)
4. Explore [Machine Learning](10-machine-learning.md) features

## 🆘 Getting Help

### Built-in Help
```bash
sentinair> help           # All commands
sentinair> help status    # Specific command help
python main.py --help     # Startup options
```

### Documentation
- This manual: `/opt/sentinair/manual/`
- Configuration reference: [Config Reference](17-config-reference.md)
- Troubleshooting: [Troubleshooting Guide](13-troubleshooting.md)

### Community Resources
- GitHub Issues: Report bugs and feature requests
- Documentation: Latest updates and examples
- Security Advisories: Important security updates

---

**Previous**: [Installation Guide](01-installation.md) | **Next**: [Configuration](03-configuration.md)
