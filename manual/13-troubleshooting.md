# Troubleshooting Guide

Comprehensive troubleshooting guide for common Sentinair issues and their solutions.

## 🚨 Quick Problem Resolution

### Most Common Issues
1. **Sentinair won't start** → [Startup Issues](#startup-issues)
2. **No alerts being generated** → [Alert Problems](#alert-problems)
3. **High CPU/Memory usage** → [Performance Issues](#performance-issues)
4. **Database errors** → [Database Problems](#database-problems)
5. **Permission denied errors** → [Permission Issues](#permission-issues)

## 🔧 Startup Issues

### Problem: Sentinair Won't Start
```bash
# Error: "Module not found" or "Import Error"
```

**Solutions:**
```bash
# 1. Verify Python environment
python --version          # Should be 3.8+
which python              # Check Python location

# 2. Check virtual environment
source .venv/bin/activate  # Linux
.venv\Scripts\activate     # Windows

# 3. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 4. Check for conflicting packages
pip list | grep -i sentinair
pip uninstall conflicting-package
```

### Problem: Configuration File Not Found
```bash
# Error: "Configuration file not found: config/default.yaml"
```

**Solutions:**
```bash
# 1. Check file existence
ls -la config/
ls -la config/default.yaml

# 2. Verify working directory
pwd                        # Should be in Sentinair root
cd /opt/sentinair          # Navigate to correct directory

# 3. Create missing config
cp config/default.yaml.example config/default.yaml  # If exists
# Or reinstall Sentinair
```

### Problem: Permission Denied on Startup
```bash
# Error: "Permission denied: '/opt/sentinair/data/sentinair.db'"
```

**Solutions:**
```bash
# 1. Fix file permissions
sudo chown -R $USER:$USER /opt/sentinair
chmod -R 755 /opt/sentinair
chmod 644 /opt/sentinair/data/sentinair.db

# 2. Check directory permissions
ls -la /opt/sentinair/data/

# 3. Create missing directories
mkdir -p /opt/sentinair/data/logs
mkdir -p /opt/sentinair/data/models
mkdir -p /opt/sentinair/data/reports
```

## 🔍 Database Problems

### Problem: Database Connection Failed
```bash
# Error: "Database connection failed" or "database is locked"
```

**Solutions:**
```bash
# 1. Check database file
ls -la data/sentinair.db
file data/sentinair.db     # Should show "SQLite 3.x database"

# 2. Test database manually
sqlite3 data/sentinair.db ".tables"
sqlite3 data/sentinair.db "SELECT COUNT(*) FROM system_events;"

# 3. Kill processes using database
lsof data/sentinair.db     # Show processes using file
kill <pid>                 # Kill if needed

# 4. Backup and recreate database
cp data/sentinair.db data/sentinair.db.backup
rm data/sentinair.db
python main.py --mode cli  # Will recreate database
```

### Problem: Database Corruption
```bash
# Error: "database disk image is malformed"
```

**Solutions:**
```bash
# 1. Attempt repair
sqlite3 data/sentinair.db "PRAGMA integrity_check;"
sqlite3 data/sentinair.db ".recover" | sqlite3 data/sentinair_recovered.db

# 2. Export and recreate
sqlite3 data/sentinair.db ".dump" > backup.sql
rm data/sentinair.db
sqlite3 data/sentinair.db < backup.sql

# 3. Start fresh (last resort)
mv data/sentinair.db data/sentinair.db.corrupted
python main.py --mode cli  # Creates new database
```

### Problem: Database Growing Too Large
```bash
# Warning: Database size > 1GB
```

**Solutions:**
```bash
# 1. Check database size
du -h data/sentinair.db

# 2. Clean old data via CLI
python main.py --mode cli
sentinair> db cleanup --days 30
sentinair> db vacuum

# 3. Configure automatic cleanup
# Edit config/default.yaml:
database:
  cleanup_days: 30         # Keep 30 days of data
  max_events: 50000        # Maximum events to store
```

## 🚨 Alert Problems

### Problem: No Alerts Generated
```bash
# Issue: System running but no alerts appear
```

**Solutions:**
```bash
# 1. Check if monitoring is active
python main.py --mode cli
sentinair> status          # Should show "Monitoring Active: Yes"

# 2. Start monitoring if stopped
sentinair> start

# 3. Check alert thresholds
sentinair> config show alerts.thresholds
# Lower thresholds if too high:
sentinair> config set alerts.thresholds.low 0.2
sentinair> config set alerts.thresholds.medium 0.4

# 4. Verify ML model is trained
sentinair> model info
# Train if needed:
sentinair> train

# 5. Test with known suspicious activity
# Create test file in /tmp with suspicious name
echo "test" > /tmp/malware_test.exe
```

### Problem: Too Many False Positive Alerts
```bash
# Issue: Excessive alerts for normal activity
```

**Solutions:**
```bash
# 1. Increase alert thresholds
sentinair> config set alerts.thresholds.low 0.4
sentinair> config set alerts.thresholds.medium 0.6
sentinair> config set alerts.thresholds.high 0.8

# 2. Retrain model with more data
sentinair> train --days 30  # Use more training data

# 3. Whitelist known good processes
sentinair> config show monitoring.process_monitoring.whitelist_processes
# Add to whitelist in config file:
monitoring:
  process_monitoring:
    whitelist_processes:
      - "your_application"
      - "legitimate_tool"

# 4. Adjust monitoring sensitivity
sentinair> config set detection.sensitivity "low"
```

### Problem: Alerts Not Displayed in GUI
```bash
# Issue: Alerts generated but not shown in interface
```

**Solutions:**
```bash
# 1. Check alert database table
sqlite3 data/sentinair.db "SELECT COUNT(*) FROM alerts;"

# 2. Verify GUI notifications enabled
sentinair> config show alerts.notifications.gui
sentinair> config set alerts.notifications.gui true

# 3. Check for GUI dependency issues (Linux)
sudo apt install python3-pyqt5
pip install plyer

# 4. Test notification system
python -c "from plyer import notification; notification.notify(title='Test', message='GUI working')"
```

## ⚡ Performance Issues

### Problem: High CPU Usage
```bash
# Issue: Sentinair using > 20% CPU constantly
```

**Solutions:**
```bash
# 1. Check current resource usage
sentinair> stats system
top -p $(pgrep -f sentinair)

# 2. Reduce monitoring frequency
sentinair> config set monitoring.check_interval 10  # Increase from 5 to 10 seconds

# 3. Disable unnecessary monitoring
sentinair> config set monitoring.usb_monitoring.enabled false
sentinair> config set monitoring.behavior_monitoring.enabled false

# 4. Optimize file monitoring paths
# Edit config to monitor fewer paths:
monitoring:
  file_monitoring:
    paths:
      - "/home/user"          # Instead of entire /home
      - "/etc/important"      # Instead of entire /etc

# 5. Reduce ML model complexity
sentinair> config set ml.n_estimators 50  # Reduce from 100
```

### Problem: High Memory Usage
```bash
# Issue: Sentinair using > 500MB RAM
```

**Solutions:**
```bash
# 1. Check memory usage breakdown
sentinair> stats system
ps aux | grep sentinair

# 2. Reduce cache size
sentinair> config set performance.memory.max_cache_size 64  # Reduce cache

# 3. Enable garbage collection
sentinair> config set performance.memory.gc_threshold 500

# 4. Limit training data size
sentinair> config set ml.max_samples 1000  # Reduce training samples

# 5. Restart periodically (workaround)
# Add to crontab for daily restart:
0 2 * * * systemctl restart sentinair
```

### Problem: Slow Database Queries
```bash
# Issue: Database operations taking > 5 seconds
```

**Solutions:**
```bash
# 1. Vacuum database
sentinair> db vacuum

# 2. Check database size and cleanup
sentinair> db info
sentinair> db cleanup --days 30

# 3. Optimize database settings
# Edit config/default.yaml:
database:
  connection_pool_size: 5
  batch_insert_size: 500

# 4. Add database indexes (advanced)
sqlite3 data/sentinair.db "CREATE INDEX IF NOT EXISTS idx_timestamp ON system_events(timestamp);"
sqlite3 data/sentinair.db "CREATE INDEX IF NOT EXISTS idx_event_type ON system_events(event_type);"
```

## 🔒 Permission Issues

### Problem: Permission Denied Accessing Files
```bash
# Error: "Permission denied: '/etc/passwd'"
```

**Solutions:**
```bash
# 1. Run with appropriate privileges
sudo python main.py --mode cli  # If monitoring system files

# 2. Add user to required groups
sudo usermod -a -G adm $USER    # For log file access
sudo usermod -a -G disk $USER   # For disk monitoring

# 3. Configure specific permissions
# For monitoring /etc without root:
sudo setfacl -R -m u:$USER:r /etc/important_directory

# 4. Adjust monitoring paths
# Edit config to monitor accessible paths only:
monitoring:
  file_monitoring:
    paths:
      - "/home/$USER"
      - "/var/log"  # Usually readable by adm group
```

### Problem: Cannot Create Files in Data Directory
```bash
# Error: "Permission denied: 'data/sentinair.db'"
```

**Solutions:**
```bash
# 1. Fix ownership
sudo chown -R $USER:$USER /opt/sentinair/data/

# 2. Fix permissions
chmod -R 755 /opt/sentinair/data/
chmod 755 /opt/sentinair/data/logs/
chmod 755 /opt/sentinair/data/models/

# 3. Create directories if missing
mkdir -p /opt/sentinair/data/{logs,models,reports}

# 4. Check disk space
df -h /opt/sentinair/data/
```

## 🌐 Network and Connectivity Issues

### Problem: Email Notifications Not Working
```bash
# Issue: Email alerts not being sent
```

**Solutions:**
```bash
# 1. Test email configuration
sentinair> config show alerts.notifications.email_config

# 2. Test SMTP connection manually
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print('SMTP connection successful')
"

# 3. Check for authentication issues
# Use app passwords for Gmail, not account password
# Enable "Less secure app access" if required

# 4. Test with different SMTP settings
# Try different ports: 25, 465, 587
# Try different servers: smtp.outlook.com, etc.
```

### Problem: Webhook Notifications Failing
```bash
# Issue: HTTP webhook calls failing
```

**Solutions:**
```bash
# 1. Test webhook URL manually
curl -X POST https://your-webhook-url.com/alerts \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'

# 2. Check network connectivity
ping your-webhook-domain.com
nslookup your-webhook-domain.com

# 3. Verify webhook configuration
sentinair> config show alerts.notifications.webhook_config

# 4. Check for proxy/firewall issues
export http_proxy=http://proxy:8080
export https_proxy=http://proxy:8080
```

## 🐧 Linux-Specific Issues

### Problem: Systemd Service Won't Start
```bash
# Error: "Failed to start sentinair.service"
```

**Solutions:**
```bash
# 1. Check service status
sudo systemctl status sentinair
sudo journalctl -u sentinair -f

# 2. Fix service file
sudo nano /etc/systemd/system/sentinair.service
# Verify paths and user in service file

# 3. Reload systemd
sudo systemctl daemon-reload
sudo systemctl enable sentinair
sudo systemctl start sentinair

# 4. Check service file template
[Unit]
Description=Sentinair Security Monitor
After=network.target

[Service]
Type=simple
User=sentinair
WorkingDirectory=/opt/sentinair
ExecStart=/opt/sentinair/.venv/bin/python main.py --mode stealth
Restart=always

[Install]
WantedBy=multi-user.target
```

### Problem: PyQt5 Installation Issues
```bash
# Error: "No module named 'PyQt5'"
```

**Solutions:**
```bash
# 1. Install system PyQt5 packages
sudo apt install python3-pyqt5 python3-pyqt5.qtwidgets

# 2. Install via pip (if system packages don't work)
pip install PyQt5

# 3. For older systems
sudo apt install python3-pyqt5-dev python3-pyqt5.qtsql

# 4. Alternative: Use system Python
sudo apt install python3-pip
sudo pip3 install -r requirements.txt
```

## 🪟 Windows-Specific Issues

### Problem: Windows Service Installation Failed
```powershell
# Error: Service installation failed
```

**Solutions:**
```powershell
# 1. Run PowerShell as Administrator
# Right-click PowerShell → "Run as Administrator"

# 2. Check execution policy
Get-ExecutionPolicy
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Install service manually
sc create Sentinair binPath= "C:\sentinair\.venv\Scripts\python.exe C:\sentinair\main.py --mode stealth"
sc config Sentinair start= auto

# 4. Use alternative service installer
pip install pywin32
python Scripts/pywin32_postinstall.py -install
```

### Problem: Python Not Found on Windows
```powershell
# Error: "'python' is not recognized"
```

**Solutions:**
```powershell
# 1. Add Python to PATH
$env:PATH += ";C:\Python39;C:\Python39\Scripts"

# 2. Use full Python path
C:\Python39\python.exe main.py --mode cli

# 3. Reinstall Python with "Add to PATH" option
# Download from python.org and check "Add Python to PATH"

# 4. Use Python Launcher
py main.py --mode cli
py -3.9 main.py --mode cli
```

## 🔍 Diagnostic Tools

### Built-in Diagnostics
```bash
# Run comprehensive diagnostics
sentinair> test all

# Test specific components
sentinair> test database
sentinair> test ml-model
sentinair> test alerts
sentinair> test performance

# System information
sentinair> system info
sentinair> system diagnostics
```

### Log Analysis
```bash
# Check for common error patterns
grep -i error data/logs/sentinair.log
grep -i "permission denied" data/logs/sentinair.log
grep -i "failed" data/logs/sentinair.log

# Monitor logs in real-time
tail -f data/logs/sentinair.log

# Analyze log patterns
sentinair> logs --level ERROR --hours 24
sentinair> logs --search "database"
```

### Performance Monitoring
```bash
# Monitor system resources
top -p $(pgrep -f sentinair)
htop                           # If available
iotop                          # Disk I/O
nethogs                        # Network usage

# Check file descriptors
lsof -p $(pgrep -f sentinair)

# Memory analysis
pmap $(pgrep -f sentinair)
```

## 🆘 Getting Help

### Community Support
- **GitHub Issues**: Report bugs and get help
- **Documentation**: Check latest manual updates
- **Examples**: Review example configurations

### Professional Support
- **Commercial Support**: Available for enterprise users
- **Custom Development**: Feature requests and customizations
- **Training**: Professional training available

### Emergency Procedures
```bash
# Emergency stop
sentinair> emergency-stop

# Kill all Sentinair processes
pkill -f sentinair

# Reset to factory defaults
mv config/default.yaml config/default.yaml.backup
cp config/default.yaml.original config/default.yaml
rm data/sentinair.db
```

---

**Previous**: [Stealth Mode](06-stealth-mode.md) | **Next**: [Performance Tuning](14-performance.md)
