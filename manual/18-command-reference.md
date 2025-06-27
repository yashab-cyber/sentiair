# Command Reference

Complete reference for all Sentinair commands, parameters, and options.

## 📋 Command Categories

### System Control
- [`start`](#start) - Start monitoring
- [`stop`](#stop) - Stop monitoring  
- [`status`](#status) - Show system status
- [`restart`](#restart) - Restart monitoring

### Alert Management
- [`alerts`](#alerts) - View and manage alerts
- [`acknowledge`](#acknowledge) - Acknowledge alerts

### Statistics and Monitoring
- [`stats`](#stats) - Show system statistics
- [`monitor`](#monitor) - Real-time monitoring
- [`logs`](#logs) - View and manage logs

### Machine Learning
- [`train`](#train) - Train ML models
- [`model`](#model) - Model management
- [`predict`](#predict) - Test predictions

### Configuration
- [`config`](#config) - Configuration management
- [`set`](#set) - Set configuration values
- [`get`](#get) - Get configuration values

### Reporting
- [`report`](#report) - Generate reports
- [`export`](#export) - Export data

### Database Management
- [`db`](#db) - Database operations
- [`backup`](#backup) - Create backups
- [`restore`](#restore) - Restore backups

### System Tools
- [`test`](#test) - Run diagnostic tests
- [`search`](#search) - Search events and alerts
- [`clear`](#clear) - Clear screen/data

### Help and Information
- [`help`](#help) - Show help information
- [`version`](#version) - Show version info
- [`exit`](#exit) - Exit application

---

## 🚀 System Control Commands

### `start`
Start Sentinair monitoring system.

**Syntax:**
```bash
start [options]
```

**Options:**
- `--modules <list>` - Start specific modules only
- `--force` - Force start even if already running
- `--background` - Start in background mode

**Examples:**
```bash
sentinair> start
sentinair> start --modules file,process
sentinair> start --force --background
```

**Output:**
```
Starting Sentinair monitoring...
✅ File monitoring started
✅ Process monitoring started  
✅ USB monitoring started
✅ Behavior monitoring started
🎯 Monitoring active - 4/4 modules running
```

---

### `stop`
Stop Sentinair monitoring system.

**Syntax:**
```bash
stop [options]
```

**Options:**
- `--modules <list>` - Stop specific modules only
- `--force` - Force stop immediately
- `--graceful` - Graceful shutdown (default)

**Examples:**
```bash
sentinair> stop
sentinair> stop --modules usb
sentinair> stop --force
```

---

### `status`
Display comprehensive system status.

**Syntax:**
```bash
status [options]
```

**Options:**
- `--detailed` - Show detailed status information
- `--modules` - Show module-specific status
- `--format <type>` - Output format (text, json, table)

**Examples:**
```bash
sentinair> status
sentinair> status --detailed
sentinair> status --format json
```

---

### `restart`
Restart monitoring system.

**Syntax:**
```bash
restart [options]
```

**Options:**
- `--modules <list>` - Restart specific modules
- `--wait <seconds>` - Wait time between stop/start

**Examples:**
```bash
sentinair> restart
sentinair> restart --modules file,process
sentinair> restart --wait 5
```

---

## 🚨 Alert Management Commands

### `alerts`
View and manage security alerts.

**Syntax:**
```bash
alerts [subcommand] [options]
```

**Subcommands:**
- `list` - List alerts (default)
- `show <id>` - Show specific alert details
- `acknowledge <id>` - Acknowledge alert
- `delete <id>` - Delete alert
- `clear` - Clear all alerts

**Options:**
- `--severity <level>` - Filter by severity (critical, high, medium, low)
- `--type <type>` - Filter by event type
- `--hours <n>` - Show alerts from last N hours
- `--days <n>` - Show alerts from last N days
- `--since <datetime>` - Show alerts since specific time
- `--status <status>` - Filter by status (new, acknowledged, resolved)
- `--details` - Show detailed information
- `--format <type>` - Output format (table, json, csv)
- `--export <file>` - Export to file

**Examples:**
```bash
# List recent alerts
sentinair> alerts
sentinair> alerts --hours 6
sentinair> alerts --severity critical high

# Show specific alert
sentinair> alerts show 1001
sentinair> alerts --details 1001

# Filter alerts
sentinair> alerts --type process --days 7
sentinair> alerts --status new --severity critical

# Export alerts
sentinair> alerts --export alerts.csv --format csv
sentinair> alerts --since "2025-06-26 00:00:00" --format json
```

---

### `acknowledge`
Acknowledge one or more alerts.

**Syntax:**
```bash
acknowledge <alert_ids> [options]
```

**Options:**
- `--message <text>` - Add acknowledgment message
- `--user <username>` - Specify acknowledging user
- `--all` - Acknowledge all alerts (with filters)

**Examples:**
```bash
sentinair> acknowledge 1001
sentinair> acknowledge 1001 1002 1003
sentinair> acknowledge 1001 --message "False positive - authorized tool"
sentinair> acknowledge --all --severity low
```

---

## 📊 Statistics and Monitoring Commands

### `stats`
Display system statistics and metrics.

**Syntax:**
```bash
stats [category] [options]
```

**Categories:**
- `system` - System performance metrics
- `events` - Event statistics
- `alerts` - Alert statistics
- `ml` - Machine learning metrics
- `database` - Database statistics

**Options:**
- `--hours <n>` - Statistics for last N hours
- `--days <n>` - Statistics for last N days
- `--today` - Today's statistics only
- `--week` - This week's statistics
- `--month` - This month's statistics
- `--format <type>` - Output format (text, json, table)
- `--export <file>` - Export to file

**Examples:**
```bash
sentinair> stats
sentinair> stats events --days 7
sentinair> stats ml --format json
sentinair> stats system --export system_stats.json
```

---

### `monitor`
Real-time monitoring of events and system activity.

**Syntax:**
```bash
monitor [type] [options]
```

**Types:**
- `events` - All events (default)
- `alerts` - Alert stream
- `process` - Process events only
- `file` - File access events only
- `usb` - USB events only

**Options:**
- `--filter <pattern>` - Filter events by pattern
- `--severity <level>` - Filter by severity
- `--user <username>` - Filter by user
- `--path <pattern>` - Filter by file path pattern

**Examples:**
```bash
sentinair> monitor
sentinair> monitor alerts
sentinair> monitor file --path "/etc/*"
sentinair> monitor process --user root
```

**Control:**
- `Ctrl+C` - Stop monitoring
- `Ctrl+Z` - Pause monitoring

---

### `logs`
View and manage system logs.

**Syntax:**
```bash
logs [options]
```

**Options:**
- `--tail <n>` - Show last N lines
- `--follow` - Follow log in real-time
- `--level <level>` - Filter by log level (DEBUG, INFO, WARNING, ERROR)
- `--module <name>` - Filter by module name
- `--since <datetime>` - Show logs since specific time
- `--search <pattern>` - Search log content
- `--grep <pattern>` - Grep-style pattern matching
- `--export <file>` - Export logs to file
- `--archive` - Create compressed log archive

**Examples:**
```bash
sentinair> logs --tail 50
sentinair> logs --follow
sentinair> logs --level ERROR --since "10:00:00"
sentinair> logs --search "anomaly detected"
sentinair> logs --module core.engine --export engine.log
```

---

## 🤖 Machine Learning Commands

### `train`
Train or retrain machine learning models.

**Syntax:**
```bash
train [options]
```

**Options:**
- `--model <type>` - Model type (isolation_forest, svm, lof, autoencoder, ensemble)
- `--data-file <file>` - Use custom training data file
- `--days <n>` - Use data from last N days
- `--contamination <float>` - Set contamination parameter
- `--estimators <n>` - Number of estimators (for ensemble methods)
- `--max-samples <n>` - Maximum samples per estimator
- `--validation-split <float>` - Validation data percentage
- `--cross-validation <n>` - K-fold cross validation
- `--save-model` - Save trained model
- `--force` - Force retrain even if model exists

**Examples:**
```bash
sentinair> train
sentinair> train --model ensemble --validation-split 0.2
sentinair> train --contamination 0.05 --estimators 200
sentinair> train --data-file custom_data.json --force
```

---

### `model`
Manage machine learning models.

**Syntax:**
```bash
model <subcommand> [options]
```

**Subcommands:**
- `info` - Show model information
- `list` - List available models
- `load <model>` - Load specific model
- `save <name>` - Save current model
- `delete <model>` - Delete model
- `export <file>` - Export model to file
- `import <file>` - Import model from file
- `evaluate` - Evaluate model performance
- `cross-validate` - Run cross-validation
- `feature-importance` - Analyze feature importance
- `optimize` - Optimize hyperparameters
- `compare <model1> <model2>` - Compare models

**Examples:**
```bash
sentinair> model info
sentinair> model list
sentinair> model load isolation_forest_v2.pkl
sentinair> model evaluate --cross-validation 5
sentinair> model feature-importance
sentinair> model compare v1.2 v1.3
```

---

### `predict`
Test model predictions on specific data.

**Syntax:**
```bash
predict [options]
```

**Options:**
- `--event-id <id>` - Predict on specific event
- `--file <path>` - Predict on file path
- `--process <name>` - Predict on process name
- `--features <values>` - Predict on raw feature values
- `--explain` - Explain prediction reasoning

**Examples:**
```bash
sentinair> predict --event-id 12345
sentinair> predict --file "/tmp/suspicious.exe"
sentinair> predict --process "unknown_binary" --explain
```

---

## ⚙️ Configuration Commands

### `config`
Manage system configuration.

**Syntax:**
```bash
config <subcommand> [options]
```

**Subcommands:**
- `show [path]` - Show configuration
- `set <path> <value>` - Set configuration value
- `get <path>` - Get configuration value
- `reload` - Reload configuration from file
- `reset` - Reset to default configuration
- `backup` - Backup current configuration
- `restore <file>` - Restore configuration from backup
- `validate` - Validate configuration
- `export <file>` - Export configuration
- `import <file>` - Import configuration

**Examples:**
```bash
sentinair> config show
sentinair> config show monitoring.check_interval
sentinair> config set alerts.thresholds.high 0.9
sentinair> config backup
sentinair> config export production_config.yaml
```

---

### `set`
Quick configuration setter.

**Syntax:**
```bash
set <config_path> <value>
```

**Examples:**
```bash
sentinair> set monitoring.check_interval 10
sentinair> set ml.contamination 0.05
sentinair> set alerts.notifications.email true
```

---

### `get`
Quick configuration getter.

**Syntax:**
```bash
get <config_path>
```

**Examples:**
```bash
sentinair> get monitoring.enabled
sentinair> get ml.model_type
sentinair> get alerts.thresholds
```

---

## 📊 Reporting Commands

### `report`
Generate comprehensive reports.

**Syntax:**
```bash
report [options]
```

**Options:**
- `--type <type>` - Report type (security, threat-analysis, compliance, activity)
- `--format <format>` - Output format (pdf, html, csv, json)
- `--output <file>` - Output file path
- `--days <n>` - Include data from last N days
- `--hours <n>` - Include data from last N hours
- `--date-range <start> <end>` - Custom date range
- `--include <sections>` - Include specific sections
- `--exclude <sections>` - Exclude specific sections
- `--template <file>` - Use custom report template
- `--email <address>` - Email report to address
- `--schedule <frequency>` - Schedule recurring report

**Examples:**
```bash
sentinair> report --type security --days 7 --format pdf
sentinair> report --format csv --output weekly_report.csv
sentinair> report --email admin@company.com --schedule weekly
```

---

### `export`
Export data in various formats.

**Syntax:**
```bash
export <data_type> [options]
```

**Data Types:**
- `events` - Export event data
- `alerts` - Export alert data
- `stats` - Export statistics
- `config` - Export configuration
- `logs` - Export log data
- `models` - Export ML models

**Options:**
- `--format <format>` - Export format (csv, json, xml)
- `--output <file>` - Output file path
- `--filter <criteria>` - Filter criteria
- `--compress` - Compress output file

**Examples:**
```bash
sentinair> export events --format csv --days 30
sentinair> export alerts --format json --severity critical
sentinair> export stats --output stats.json --compress
```

---

## 💾 Database Commands

### `db`
Database management operations.

**Syntax:**
```bash
db <subcommand> [options]
```

**Subcommands:**
- `info` - Show database information
- `backup [file]` - Create database backup
- `restore <file>` - Restore from backup
- `cleanup` - Clean old data
- `vacuum` - Optimize database
- `repair` - Repair database corruption
- `migrate` - Migrate database schema
- `export <table>` - Export table data
- `import <table> <file>` - Import table data

**Examples:**
```bash
sentinair> db info
sentinair> db backup
sentinair> db cleanup --days 90
sentinair> db vacuum
sentinair> db export events events_backup.sql
```

---

### `backup`
Create system backups.

**Syntax:**
```bash
backup [type] [options]
```

**Types:**
- `database` - Database backup (default)
- `config` - Configuration backup
- `models` - ML models backup
- `logs` - Log files backup
- `full` - Complete system backup

**Options:**
- `--output <file>` - Backup file path
- `--compress` - Compress backup
- `--encrypt` - Encrypt backup

**Examples:**
```bash
sentinair> backup
sentinair> backup full --compress --encrypt
sentinair> backup config --output config_backup.yaml
```

---

### `restore`
Restore from backups.

**Syntax:**
```bash
restore <backup_file> [options]
```

**Options:**
- `--type <type>` - Backup type (auto-detect if not specified)
- `--force` - Force restore without confirmation
- `--decrypt` - Decrypt backup file

**Examples:**
```bash
sentinair> restore backup_20250627.db
sentinair> restore full_backup.tar.gz --decrypt
```

---

## 🔧 System Tools

### `test`
Run diagnostic tests.

**Syntax:**
```bash
test [component] [options]
```

**Components:**
- `all` - Run all tests
- `database` - Test database connectivity
- `ml-model` - Test ML model
- `alerts` - Test alert system
- `config` - Test configuration
- `performance` - Performance tests
- `network` - Network connectivity tests

**Options:**
- `--verbose` - Verbose output
- `--report` - Generate test report

**Examples:**
```bash
sentinair> test all
sentinair> test database --verbose
sentinair> test performance --report
```

---

### `search`
Search events, alerts, and logs.

**Syntax:**
```bash
search <data_type> <query> [options]
```

**Data Types:**
- `events` - Search event data
- `alerts` - Search alerts
- `logs` - Search log files

**Options:**
- `--regex` - Use regular expressions
- `--case-sensitive` - Case-sensitive search
- `--field <field>` - Search specific field only
- `--limit <n>` - Limit number of results
- `--export <file>` - Export search results

**Examples:**
```bash
sentinair> search events "suspicious.exe"
sentinair> search alerts "malware" --field message
sentinair> search logs "ERROR" --regex --limit 50
```

---

### `clear`
Clear screen or data.

**Syntax:**
```bash
clear [target]
```

**Targets:**
- (no target) - Clear screen
- `logs` - Clear log files
- `alerts` - Clear alerts
- `cache` - Clear system cache

**Examples:**
```bash
sentinair> clear
sentinair> clear logs --older-than 30
sentinair> clear cache
```

---

## ℹ️ Help and Information Commands

### `help`
Show help information.

**Syntax:**
```bash
help [command] [subcommand]
```

**Examples:**
```bash
sentinair> help
sentinair> help alerts
sentinair> help config set
sentinair> help model evaluate
```

---

### `version`
Show version information.

**Syntax:**
```bash
version [options]
```

**Options:**
- `--detailed` - Show detailed version info
- `--dependencies` - Show dependency versions

**Examples:**
```bash
sentinair> version
sentinair> version --detailed
sentinair> version --dependencies
```

---

### `exit`
Exit Sentinair CLI.

**Syntax:**
```bash
exit
quit
q
```

**Aliases:** `quit`, `q`

---

## 🔧 Global Options

These options can be used with most commands:

- `--help` - Show command help
- `--verbose` - Verbose output
- `--quiet` - Suppress non-essential output
- `--format <type>` - Output format (text, json, csv, table)
- `--no-color` - Disable colored output
- `--config <file>` - Use specific configuration file
- `--log-level <level>` - Set logging level for command

## 📝 Examples and Use Cases

### Daily Operations
```bash
# Morning security check
sentinair> start
sentinair> status
sentinair> alerts --hours 24
sentinair> stats events --today

# Weekly maintenance
sentinair> train --validation-split 0.2
sentinair> db cleanup --days 30
sentinair> report --type security --days 7 --email admin@company.com
```

### Incident Response
```bash
# Investigate critical alerts
sentinair> alerts --severity critical --details
sentinair> search events "suspicious_process" --hours 6
sentinair> monitor alerts --severity high critical

# Export incident data
sentinair> export events --filter "severity:critical" --format json
sentinair> backup database --encrypt
```

### Performance Monitoring
```bash
# Check system performance
sentinair> stats system
sentinair> test performance
sentinair> logs --level WARNING ERROR --hours 24

# Optimize if needed
sentinair> db vacuum
sentinair> model optimize
sentinair> config set monitoring.check_interval 10
```

---

**Previous**: [Configuration Reference](17-config-reference.md) | **Next**: [Manual Index](index.md)
