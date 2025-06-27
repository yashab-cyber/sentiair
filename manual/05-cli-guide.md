# CLI User Guide

Complete reference for using Sentinair's command-line interface for server management and advanced operations.

## 🖥️ Starting CLI Mode

### Basic Usage
```bash
cd /opt/sentinair
python main.py --mode cli
```

### Advanced Startup Options
```bash
# Start with specific log level
python main.py --mode cli --log-level DEBUG

# Start with custom config
python main.py --mode cli --config /path/to/config.yaml

# Start with stealth mode access
python main.py --mode cli --stealth-key "your-secret-key"
```

## 💻 CLI Interface Overview

### Welcome Screen
```
╔══════════════════════════════════════════════════════════════╗
║                         SENTINAIR                            ║
║            Offline AI-Powered Threat Detection              ║
║                    Command Line Interface                    ║
╚══════════════════════════════════════════════════════════════╝

Available Commands:
  help     - Show this help message
  status   - Show system status
  start    - Start monitoring
  stop     - Stop monitoring
  alerts   - Show recent alerts
  stats    - Show detection statistics
  config   - Show/modify configuration
  report   - Generate reports
  train    - Manually trigger model training
  clear    - Clear screen
  exit     - Exit application

sentinair> 
```

### Command Prompt
- `sentinair>` - Normal operation mode
- `sentinair[TRAINING]>` - During model training
- `sentinair[STEALTH]>` - Stealth mode active
- `sentinair[OFFLINE]>` - Database connection issues

## 📋 Core Commands

### System Control

#### `start` - Start Monitoring
```bash
sentinair> start
Starting Sentinair monitoring...
✅ File monitoring started
✅ Process monitoring started  
✅ USB monitoring started
✅ Behavior monitoring started
🎯 Monitoring active - 4/4 modules running
```

#### `stop` - Stop Monitoring
```bash
sentinair> stop
Stopping Sentinair monitoring...
⏹️ File monitoring stopped
⏹️ Process monitoring stopped
⏹️ USB monitoring stopped
⏹️ Behavior monitoring stopped
⚫ Monitoring stopped - all modules offline
```

#### `status` - System Status
```bash
sentinair> status
📊 SENTINAIR SYSTEM STATUS
════════════════════════════════════════
🟢 Engine Status:         Running
🟢 Monitoring Active:     Yes (4/4 modules)
🟢 Database Connected:    Yes
🟢 ML Model Status:       Trained (94.2% accuracy)
📅 Last Training:         2025-06-27 08:00:00
📊 Events Today:          1,247
🚨 Active Alerts:         3 (1 critical, 2 medium)
💾 Database Size:         45.2 MB
🧠 Memory Usage:          156 MB
⚡ CPU Usage:            2.3%
```

### Alert Management

#### `alerts` - View Alerts
```bash
# Show recent alerts
sentinair> alerts
🚨 RECENT ALERTS (Last 24 hours)
════════════════════════════════════════
ID    | TIME     | SEVERITY | TYPE           | DESCRIPTION
------|----------|----------|----------------|---------------------------
1001  | 10:15:30 | CRITICAL | Process        | Suspicious executable detected
1002  | 09:45:15 | MEDIUM   | File Access    | Unauthorized /etc access
1003  | 08:30:22 | MEDIUM   | USB Device     | Unknown device connected
1004  | 07:15:10 | LOW      | Behavior       | Unusual login pattern

Total: 4 alerts (1 critical, 2 medium, 1 low)
```

#### `alerts` Advanced Options
```bash
# Filter by severity
sentinair> alerts --severity critical
sentinair> alerts --severity high medium

# Filter by type
sentinair> alerts --type process
sentinair> alerts --type file usb

# Filter by time range
sentinair> alerts --hours 6
sentinair> alerts --days 7
sentinair> alerts --since "2025-06-26 00:00:00"

# Show detailed information
sentinair> alerts --details 1001
🚨 ALERT DETAILS - ID: 1001
════════════════════════════════════════
Timestamp:     2025-06-27 10:15:30
Severity:      CRITICAL
Type:          Process
Risk Score:    0.92

Event Details:
  Process:     /tmp/suspicious.exe
  PID:         7823
  User:        root
  Command:     /tmp/suspicious.exe --silent --persist
  
Risk Factors:
  ⚠️ Unknown process location
  ⚠️ Elevated privileges
  ⚠️ Persistence indicators
  ⚠️ ML confidence: 92.3%

Actions Available:
  [A] Acknowledge   [B] Block Process   [W] Whitelist   [I] Investigate
```

#### `alerts acknowledge` - Acknowledge Alerts
```bash
# Acknowledge specific alert
sentinair> alerts acknowledge 1001
✅ Alert 1001 acknowledged by cli-user

# Acknowledge with note
sentinair> alerts acknowledge 1001 "False positive - authorized admin tool"

# Acknowledge multiple alerts
sentinair> alerts acknowledge 1001 1002 1003

# Acknowledge all low severity alerts
sentinair> alerts acknowledge --severity low --all
```

### Statistics and Monitoring

#### `stats` - System Statistics
```bash
sentinair> stats
📈 SENTINAIR STATISTICS
════════════════════════════════════════
📊 Event Statistics (Last 24 hours):
   Total Events:           1,247
   File Access Events:       892
   Process Events:           234
   USB Events:                 8
   Behavior Events:          113

🚨 Alert Statistics:
   Total Alerts:              12
   Critical:                   1 (8.3%)
   High:                       2 (16.7%)
   Medium:                     5 (41.7%)
   Low:                        4 (33.3%)

🤖 ML Performance:
   Model Accuracy:         94.2%
   False Positive Rate:     2.1%
   Detection Rate:         96.8%
   Last Training:          2025-06-27 08:00:00
   Training Data Size:     15,847 events

💻 System Performance:
   CPU Usage:               2.3%
   Memory Usage:           156 MB
   Disk Usage:            45.2 MB
   Database Queries/sec:     127
```

#### `stats` Advanced Options
```bash
# Show specific timeframes
sentinair> stats --hours 6
sentinair> stats --days 30
sentinair> stats --today
sentinair> stats --week

# Show specific categories
sentinair> stats system        # System performance only
sentinair> stats events        # Event statistics only
sentinair> stats ml            # ML performance only
sentinair> stats alerts        # Alert statistics only

# Export statistics
sentinair> stats --export csv
sentinair> stats --export json --file /tmp/stats.json
```

## 🤖 Machine Learning Commands

#### `train` - Model Training
```bash
# Start model training
sentinair> train
🧠 Starting ML model training...
📊 Loading training data: 15,847 events
🔄 Training Isolation Forest model...
⏳ Training in progress... [████████░░] 80%
✅ Training completed in 2m 34s
📈 Model accuracy: 94.2%
💾 Model saved to data/models/isolation_forest_20250627.pkl
```

#### `train` Advanced Options
```bash
# Train with specific parameters
sentinair> train --contamination 0.05
sentinair> train --estimators 200
sentinair> train --max-samples 512

# Train with custom data
sentinair> train --data-file /path/to/training_data.json
sentinair> train --days 30        # Use last 30 days of data

# Force retrain
sentinair> train --force
sentinair> train --reset          # Reset and retrain from scratch
```

#### `model` - Model Management
```bash
# Show model information
sentinair> model info
🧠 ML MODEL INFORMATION
════════════════════════════════════════
Model Type:           Isolation Forest
Status:               Trained
Accuracy:             94.2%
Training Date:        2025-06-27 08:00:00
Training Data Size:   15,847 events
Model Size:           2.3 MB
Features Used:        23
False Positive Rate:  2.1%

# List available models
sentinair> model list
📋 AVAILABLE MODELS
════════════════════════════════════════
* isolation_forest_20250627.pkl (active)  - 94.2% accuracy
  isolation_forest_20250626.pkl           - 92.1% accuracy
  autoencoder_20250625.pkl                - 89.3% accuracy

# Switch models
sentinair> model load isolation_forest_20250626.pkl
sentinair> model set-active autoencoder_20250625.pkl

# Export/import models
sentinair> model export /path/to/model_backup.pkl
sentinair> model import /path/to/model_backup.pkl
```

## ⚙️ Configuration Management

#### `config` - Configuration Commands
```bash
# Show all configuration
sentinair> config show
📋 CURRENT CONFIGURATION
════════════════════════════════════════
monitoring:
  enabled: true
  check_interval: 5
  file_monitoring:
    enabled: true
    paths: ['/home', '/etc', '/var/log']
  process_monitoring:
    enabled: true
...

# Show specific sections
sentinair> config show monitoring
sentinair> config show alerts.thresholds
sentinair> config show ml.contamination

# Set configuration values
sentinair> config set monitoring.check_interval 10
sentinair> config set alerts.thresholds.high 0.9
sentinair> config set ml.auto_train false

# Reload configuration
sentinair> config reload
🔄 Configuration reloaded from file
✅ New settings applied
```

#### `config` Advanced Operations
```bash
# Backup current config
sentinair> config backup
💾 Configuration backed up to config/backup_20250627_101530.yaml

# Restore from backup
sentinair> config restore config/backup_20250627_101530.yaml

# Reset to defaults
sentinair> config reset
⚠️ This will reset all settings to defaults. Continue? [y/N]: y
🔄 Configuration reset to defaults

# Validate configuration
sentinair> config validate
✅ Configuration is valid

# Export configuration
sentinair> config export /path/to/sentinair_config.yaml
sentinair> config export --format json /path/to/config.json
```

## 📊 Reporting Commands

#### `report` - Generate Reports
```bash
# Generate basic security report
sentinair> report
📊 Generating security report...
✅ Report generated: data/reports/security_report_20250627.pdf

# Specify report type and timeframe
sentinair> report --type security --days 7
sentinair> report --type threat-analysis --hours 24
sentinair> report --type compliance --month

# Custom output format and location
sentinair> report --format pdf --output /tmp/security_report.pdf
sentinair> report --format csv --output /tmp/events.csv
sentinair> report --format json --output /tmp/alerts.json

# Include specific sections
sentinair> report --include alerts,events,stats
sentinair> report --exclude charts,details
```

#### `report` Advanced Options
```bash
# Email report
sentinair> report --email admin@company.com
sentinair> report --email-subject "Weekly Security Report"

# Scheduled reports
sentinair> report --schedule daily --time 08:00
sentinair> report --schedule weekly --day monday --time 09:00

# Custom filters
sentinair> report --severity critical high
sentinair> report --event-types process file
sentinair> report --date-range "2025-06-20 to 2025-06-27"
```

## 🔧 System Management

#### `logs` - Log Management
```bash
# View recent logs
sentinair> logs
sentinair> logs --tail 50
sentinair> logs --follow        # Real-time log streaming

# Filter logs
sentinair> logs --level ERROR
sentinair> logs --module core.engine
sentinair> logs --since "10:00:00"

# Search logs
sentinair> logs --search "error"
sentinair> logs --grep "anomaly detected"

# Export logs
sentinair> logs --export /tmp/sentinair.log
sentinair> logs --archive        # Create compressed archive
```

#### `db` - Database Management
```bash
# Database information
sentinair> db info
💾 DATABASE INFORMATION
════════════════════════════════════════
Database Path:     /opt/sentinair/data/sentinair.db
Database Size:     45.2 MB
Total Events:      15,847
Total Alerts:      234
Oldest Event:      2025-06-20 08:00:00
Newest Event:      2025-06-27 10:15:30

# Database maintenance
sentinair> db vacuum           # Optimize database
sentinair> db backup           # Create backup
sentinair> db restore backup_20250627.db
sentinair> db repair           # Repair corruption

# Data cleanup
sentinair> db cleanup --days 90     # Remove data older than 90 days
sentinair> db cleanup --events 10000 # Keep only last 10,000 events
```

#### `system` - System Commands
```bash
# System information
sentinair> system info
💻 SYSTEM INFORMATION
════════════════════════════════════════
OS:                Linux Ubuntu 22.04
Python Version:    3.12.3
Sentinair Version: 1.0.0
Uptime:           2 days, 14:32:15
CPU Usage:        2.3%
Memory Usage:     156 MB / 8 GB
Disk Usage:       45.2 MB / 100 GB

# Process management
sentinair> system processes       # Show Sentinair processes
sentinair> system performance     # Performance metrics
sentinair> system diagnostics     # Run system diagnostics

# Service control (Linux)
sentinair> system service status
sentinair> system service restart
sentinair> system service enable
```

## 🔍 Advanced Features

#### `search` - Search Events and Alerts
```bash
# Search events
sentinair> search events "suspicious.exe"
sentinair> search events --type process --user root
sentinair> search events --file-path "/etc/*"

# Search alerts
sentinair> search alerts "malware"
sentinair> search alerts --severity critical --days 7

# Complex searches
sentinair> search events --query "type:process AND user:root AND path:/tmp/*"
sentinair> search --regex ".*\.exe$" --field process_name
```

#### `monitor` - Real-time Monitoring
```bash
# Real-time event stream
sentinair> monitor events
[10:15:30] FILE_ACCESS | /home/user/document.txt | READ | user
[10:15:31] PROCESS_START | /usr/bin/firefox | PID:1234 | user
[10:15:32] USB_CONNECT | Kingston USB Drive | /dev/sdb1

# Monitor specific types
sentinair> monitor alerts        # Only show alerts
sentinair> monitor process       # Only process events
sentinair> monitor file --path "/etc/*"

# Stop monitoring
Press Ctrl+C to stop real-time monitoring
```

#### `test` - Testing and Diagnostics
```bash
# Test system components
sentinair> test database         # Test database connectivity
sentinair> test ml-model         # Test ML model
sentinair> test alerts          # Test alert system
sentinair> test all             # Comprehensive test

# Performance testing
sentinair> test performance      # Performance benchmarks
sentinair> test load            # Load testing

# Network testing (if enabled)
sentinair> test network         # Network connectivity
sentinair> test firewall        # Firewall rules
```

## 🎯 Scripting and Automation

### Batch Commands
```bash
# Execute multiple commands
sentinair> start; status; alerts --hours 1

# Command files
echo "start" > commands.txt
echo "status" >> commands.txt
echo "alerts" >> commands.txt
python main.py --mode cli --batch commands.txt
```

### Non-interactive Mode
```bash
# Single command execution
python main.py --mode cli --command "status"
python main.py --mode cli --command "alerts --severity critical"

# Output formatting for scripts
python main.py --mode cli --command "status" --format json
python main.py --mode cli --command "alerts" --format csv
```

### Environment Variables
```bash
# Configure via environment
export SENTINAIR_CLI_FORMAT=json
export SENTINAIR_CLI_OUTPUT=/tmp/sentinair_output.json
export SENTINAIR_CLI_QUIET=true

python main.py --mode cli --command "status"
```

## 🆘 Help and Troubleshooting

### Built-in Help
```bash
# General help
sentinair> help

# Command-specific help
sentinair> help alerts
sentinair> help config set
sentinair> help report --type

# Command examples
sentinair> examples alerts
sentinair> examples config
```

### Debugging Commands
```bash
# Debug mode
sentinair> debug on
sentinair> debug off
sentinair> debug level DEBUG

# Verbose output
sentinair> verbose on
sentinair> trace on             # Enable function tracing

# Error analysis
sentinair> errors show          # Show recent errors
sentinair> errors clear         # Clear error log
```

### Exit Commands
```bash
# Normal exit
sentinair> exit
sentinair> quit
sentinair> q

# Emergency stop
sentinair> emergency-stop       # Immediate shutdown
Ctrl+C                         # Interrupt signal
```

---

**Previous**: [GUI User Guide](04-gui-guide.md) | **Next**: [Stealth Mode](06-stealth-mode.md)
