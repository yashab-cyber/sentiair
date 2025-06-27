# Configuration Reference

This comprehensive reference guide covers all configuration options available in Sentinair. Configuration files use YAML format and are located in the `config/` directory.

## Table of Contents

1. [Configuration Files Overview](#configuration-files-overview)
2. [Main Configuration (default.yaml)](#main-configuration-defaultyaml)
3. [Logging Configuration](#logging-configuration)
4. [Database Configuration](#database-configuration)
5. [Monitoring Configuration](#monitoring-configuration)
6. [Machine Learning Configuration](#machine-learning-configuration)
7. [Alert Configuration](#alert-configuration)
8. [Security Configuration](#security-configuration)
9. [Performance Configuration](#performance-configuration)
10. [Environment Variables](#environment-variables)
11. [Configuration Validation](#configuration-validation)

## Configuration Files Overview

### Primary Configuration Files

| File | Purpose | Required |
|------|---------|----------|
| `config/default.yaml` | Main configuration file | Yes |
| `config/encryption.key` | Encryption key for sensitive data | Yes |
| `config/logging.yaml` | Logging configuration (optional) | No |
| `config/custom_rules.yaml` | Custom detection rules | No |

### Configuration Priority

Sentinair loads configuration in the following order (later overrides earlier):

1. Default built-in settings
2. `config/default.yaml`
3. Environment variables (prefixed with `SENTINAIR_`)
4. Command-line arguments

## Main Configuration (default.yaml)

### Complete Configuration Template

```yaml
# Sentinair Configuration File
# Version: 1.0

# System Settings
system:
  # Application name and version
  name: "Sentinair"
  version: "1.0.0"
  
  # System identification
  instance_id: "sentinair-001"
  deployment_type: "production"  # development, testing, production
  
  # Data directories
  data_dir: "data/"
  logs_dir: "data/logs/"
  models_dir: "data/models/"
  reports_dir: "data/reports/"
  
  # Temporary files
  temp_dir: "/tmp/sentinair"
  cleanup_temp: true
  
  # Process management
  max_workers: 4
  worker_timeout: 300
  
  # System limits
  max_memory_usage: "2GB"
  max_disk_usage: "10GB"

# Database Configuration
database:
  # Database type and connection
  type: "sqlite"  # sqlite, postgresql, mysql
  path: "data/sentinair.db"
  
  # Connection settings (for external databases)
  host: "localhost"
  port: 5432
  username: ""
  password: ""
  database_name: "sentinair"
  
  # Connection pool
  max_connections: 10
  connection_timeout: 30
  
  # Maintenance
  auto_vacuum: true
  backup_enabled: true
  backup_interval: 24  # hours
  max_backups: 7

# Logging Configuration
logging:
  # Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
  level: "INFO"
  
  # Log formats
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
  
  # Log files
  main_log: "data/logs/sentinair.log"
  error_log: "data/logs/sentinair_errors.log"
  audit_log: "data/logs/audit.log"
  security_log: "data/logs/security_events.log"
  
  # Log rotation
  max_file_size: "10MB"
  max_files: 5
  
  # Log retention
  retention_days: 30
  
  # Console logging
  console_enabled: true
  console_level: "INFO"

# Monitoring Configuration
monitoring:
  # Global monitoring settings
  enabled: true
  interval: 1  # seconds
  
  # File system monitoring
  file_monitor:
    enabled: true
    watch_paths:
      - "/home"
      - "/etc"
      - "/var/log"
      - "/tmp"
    exclude_paths:
      - "/proc"
      - "/sys"
      - "/dev"
    file_types:
      - ".exe"
      - ".dll"
      - ".bat"
      - ".sh"
      - ".py"
    max_file_size: "100MB"
    checksum_enabled: true
  
  # Process monitoring
  process_monitor:
    enabled: true
    scan_interval: 5  # seconds
    track_children: true
    monitor_network: true
    suspicious_processes:
      - "nc"
      - "netcat"
      - "nmap"
      - "tcpdump"
  
  # USB monitoring
  usb_monitor:
    enabled: true
    block_unknown: false
    whitelist_enabled: true
    whitelist:
      - "vendor:product"  # Format: vendorID:productID
    log_all_events: true
  
  # Behavior monitoring
  behavior_monitor:
    enabled: true
    track_logins: true
    track_file_access: true
    track_network: true
    track_registry: true  # Windows only
    suspicious_patterns:
      - "rapid_file_creation"
      - "unusual_network_activity"
      - "privilege_escalation"

# Machine Learning Configuration
machine_learning:
  # ML engine settings
  enabled: true
  model_type: "isolation_forest"  # isolation_forest, one_class_svm, local_outlier_factor
  
  # Training settings
  training_enabled: true
  auto_retrain: true
  retrain_interval: 168  # hours (1 week)
  min_training_samples: 1000
  
  # Model parameters
  contamination: 0.1  # Expected outlier fraction
  random_state: 42
  n_estimators: 100  # For Isolation Forest
  
  # Feature engineering
  features:
    - "file_access_patterns"
    - "process_behavior"
    - "network_activity"
    - "time_patterns"
    - "user_behavior"
  
  # Anomaly detection
  detection_threshold: 0.7
  min_confidence: 0.6
  
  # Model persistence
  save_models: true
  model_format: "pickle"  # pickle, joblib, onnx
  
  # Performance
  batch_size: 100
  prediction_cache: true
  cache_size: 1000

# Alert Configuration
alerts:
  # Global alert settings
  enabled: true
  
  # Alert levels and thresholds
  levels:
    low: 0.3
    medium: 0.6
    high: 0.8
    critical: 0.9
  
  # Alert channels
  channels:
    file:
      enabled: true
      path: "data/logs/alerts.log"
    
    email:
      enabled: false
      smtp_server: "smtp.example.com"
      smtp_port: 587
      username: "alerts@example.com"
      password: ""
      recipients:
        - "admin@example.com"
    
    syslog:
      enabled: false
      server: "localhost"
      port: 514
      facility: "local0"
    
    webhook:
      enabled: false
      url: "https://hooks.example.com/alerts"
      headers:
        Content-Type: "application/json"
      timeout: 30
  
  # Alert rules
  rules:
    - name: "high_risk_process"
      condition: "process_risk > 0.8"
      level: "critical"
      cooldown: 300  # seconds
    
    - name: "suspicious_file_access"
      condition: "file_access_anomaly > 0.7"
      level: "high"
      cooldown: 60
    
    - name: "usb_device_inserted"
      condition: "usb_event == 'insert'"
      level: "medium"
      cooldown: 0

# Security Configuration
security:
  # Encryption settings
  encryption:
    enabled: true
    algorithm: "AES-256-GCM"
    key_file: "config/encryption.key"
    rotate_keys: true
    rotation_interval: 2160  # hours (90 days)
  
  # Access control
  access_control:
    enabled: true
    require_auth: true
    session_timeout: 3600  # seconds
    max_failed_attempts: 5
    lockout_duration: 900  # seconds
  
  # Audit settings
  audit:
    enabled: true
    log_all_access: true
    log_config_changes: true
    log_admin_actions: true
    retention_days: 365
  
  # Secure communication
  tls:
    enabled: true
    version: "TLSv1.3"
    cert_file: "certs/server.crt"
    key_file: "certs/server.key"
    ca_file: "certs/ca.crt"

# Performance Configuration
performance:
  # CPU usage limits
  cpu:
    max_usage: 80  # percentage
    throttle_threshold: 90
    nice_level: 10
  
  # Memory management
  memory:
    max_usage: "1GB"
    gc_threshold: 0.8
    cache_size: "256MB"
  
  # I/O optimization
  io:
    buffer_size: "64KB"
    max_concurrent_reads: 10
    use_sendfile: true
  
  # Database performance
  database_tuning:
    cache_size: "100MB"
    page_size: 4096
    checkpoint_interval: 1000
    wal_mode: true

# GUI Configuration
gui:
  # Window settings
  window:
    title: "Sentinair Security Monitor"
    width: 1200
    height: 800
    resizable: true
    
  # Theme settings
  theme:
    name: "dark"  # dark, light, system
    primary_color: "#2196F3"
    accent_color: "#FF9800"
  
  # Update intervals
  refresh_rates:
    dashboard: 5  # seconds
    alerts: 2
    logs: 10
    system_stats: 5
  
  # Charts and graphs
  charts:
    animation: true
    max_data_points: 100
    auto_scale: true

# CLI Configuration
cli:
  # Output formatting
  output:
    format: "table"  # table, json, yaml, csv
    colors: true
    timestamps: true
  
  # Command defaults
  defaults:
    max_results: 100
    timeout: 30
    verbose: false
  
  # History
  history:
    enabled: true
    max_entries: 1000
    file: "data/cli_history.txt"

# Integration Configuration
integrations:
  # API settings
  api:
    enabled: true
    host: "0.0.0.0"
    port: 8080
    cors_enabled: true
    rate_limiting:
      enabled: true
      requests_per_minute: 100
  
  # SIEM integration
  siem:
    enabled: false
    type: "splunk"  # splunk, elk, qradar
    endpoint: "https://siem.example.com/api"
    api_key: ""
  
  # External tools
  external_tools:
    yara:
      enabled: true
      rules_path: "signatures/"
    
    clamav:
      enabled: false
      database_path: "/var/lib/clamav/"

# Development Configuration
development:
  # Debug settings
  debug:
    enabled: false
    log_sql: false
    profile_performance: false
  
  # Testing
  testing:
    mock_data: false
    test_mode: false
    bypass_auth: false
```

## Configuration Sections Reference

### System Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `system.name` | string | "Sentinair" | Application name |
| `system.version` | string | "1.0.0" | Version identifier |
| `system.instance_id` | string | "sentinair-001" | Unique instance identifier |
| `system.deployment_type` | string | "production" | Deployment environment |
| `system.data_dir` | string | "data/" | Data directory path |
| `system.max_workers` | integer | 4 | Maximum worker processes |

### Database Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `database.type` | string | "sqlite" | Database type |
| `database.path` | string | "data/sentinair.db" | SQLite database path |
| `database.max_connections` | integer | 10 | Maximum database connections |
| `database.backup_enabled` | boolean | true | Enable automatic backups |

### Monitoring Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `monitoring.enabled` | boolean | true | Enable monitoring |
| `monitoring.interval` | integer | 1 | Monitoring interval (seconds) |
| `monitoring.file_monitor.enabled` | boolean | true | Enable file monitoring |
| `monitoring.process_monitor.enabled` | boolean | true | Enable process monitoring |

### Machine Learning Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `machine_learning.enabled` | boolean | true | Enable ML detection |
| `machine_learning.model_type` | string | "isolation_forest" | ML model type |
| `machine_learning.contamination` | float | 0.1 | Expected outlier fraction |
| `machine_learning.detection_threshold` | float | 0.7 | Detection threshold |

## Environment Variables

Sentinair supports configuration via environment variables. All variables are prefixed with `SENTINAIR_`:

### Database Variables

```bash
export SENTINAIR_DATABASE_TYPE="postgresql"
export SENTINAIR_DATABASE_HOST="localhost"
export SENTINAIR_DATABASE_PORT="5432"
export SENTINAIR_DATABASE_USERNAME="sentinair"
export SENTINAIR_DATABASE_PASSWORD="secure_password"
```

### Security Variables

```bash
export SENTINAIR_ENCRYPTION_KEY_FILE="/secure/path/encryption.key"
export SENTINAIR_TLS_CERT_FILE="/certs/server.crt"
export SENTINAIR_TLS_KEY_FILE="/certs/server.key"
```

### Performance Variables

```bash
export SENTINAIR_MAX_WORKERS="8"
export SENTINAIR_MAX_MEMORY_USAGE="4GB"
export SENTINAIR_CPU_MAX_USAGE="90"
```

### Monitoring Variables

```bash
export SENTINAIR_MONITORING_INTERVAL="2"
export SENTINAIR_FILE_MONITOR_ENABLED="true"
export SENTINAIR_USB_MONITOR_ENABLED="false"
```

## Configuration Validation

### Validation Rules

Sentinair validates configuration on startup:

1. **Required fields**: Must be present
2. **Type checking**: Values must match expected types
3. **Range validation**: Numeric values within acceptable ranges
4. **Path validation**: File and directory paths must be accessible
5. **Format validation**: Email addresses, URLs, etc.

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid log level` | Unsupported log level | Use: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `Database connection failed` | Invalid database settings | Check host, port, credentials |
| `Invalid monitoring interval` | Interval too low or high | Use 1-3600 seconds |
| `Missing encryption key` | Key file not found | Generate or copy encryption key |

### Validation Command

```bash
# Validate configuration
sentinair config validate

# Validate specific config file
sentinair config validate --file config/custom.yaml

# Show current configuration
sentinair config show

# Test configuration
sentinair config test
```

## Configuration Best Practices

### Security Recommendations

1. **Protect sensitive files**: Set proper permissions on config files
   ```bash
   chmod 600 config/default.yaml
   chmod 400 config/encryption.key
   ```

2. **Use environment variables**: For sensitive data like passwords
   ```bash
   export SENTINAIR_DATABASE_PASSWORD="$(cat /secure/db_password)"
   ```

3. **Regular key rotation**: Enable automatic key rotation
   ```yaml
   security:
     encryption:
       rotate_keys: true
       rotation_interval: 2160  # 90 days
   ```

### Performance Tuning

1. **Adjust worker count**: Based on CPU cores
   ```yaml
   system:
     max_workers: 8  # For 8-core system
   ```

2. **Optimize database**: Use appropriate cache sizes
   ```yaml
   database:
     max_connections: 20
   performance:
     database_tuning:
       cache_size: "500MB"
   ```

3. **Monitor resource usage**: Set appropriate limits
   ```yaml
   performance:
     cpu:
       max_usage: 80
     memory:
       max_usage: "2GB"
   ```

### Monitoring Optimization

1. **Selective monitoring**: Only monitor necessary paths
   ```yaml
   monitoring:
     file_monitor:
       watch_paths:
         - "/critical/path"
       exclude_paths:
         - "/tmp"
         - "/var/cache"
   ```

2. **Appropriate intervals**: Balance security and performance
   ```yaml
   monitoring:
     interval: 2  # For high-security environments
     process_monitor:
       scan_interval: 10  # For normal environments
   ```

## Troubleshooting Configuration

### Common Issues

1. **Configuration not loading**
   - Check file permissions
   - Validate YAML syntax
   - Check file paths

2. **Database connection errors**
   - Verify database credentials
   - Check network connectivity
   - Ensure database server is running

3. **High resource usage**
   - Reduce monitoring intervals
   - Limit monitored paths
   - Adjust worker count

### Debug Configuration

Enable debug mode for troubleshooting:

```yaml
development:
  debug:
    enabled: true
    log_sql: true
    profile_performance: true

logging:
  level: "DEBUG"
  console_level: "DEBUG"
```

### Configuration Templates

#### Minimal Configuration

```yaml
system:
  name: "Sentinair"
  data_dir: "data/"

database:
  type: "sqlite"
  path: "data/sentinair.db"

logging:
  level: "INFO"

monitoring:
  enabled: true
  interval: 5

machine_learning:
  enabled: true
```

#### High-Security Configuration

```yaml
system:
  deployment_type: "production"
  max_workers: 2

monitoring:
  interval: 1
  file_monitor:
    enabled: true
    checksum_enabled: true
  usb_monitor:
    enabled: true
    block_unknown: true

security:
  encryption:
    enabled: true
    rotate_keys: true
  access_control:
    require_auth: true
    max_failed_attempts: 3

alerts:
  enabled: true
  levels:
    critical: 0.8
```

#### Development Configuration

```yaml
system:
  deployment_type: "development"

logging:
  level: "DEBUG"
  console_enabled: true

development:
  debug:
    enabled: true
    log_sql: true

monitoring:
  interval: 10  # Slower for development
```

## Configuration Migration

### Version Compatibility

When upgrading Sentinair, configuration files may need migration:

```bash
# Backup current configuration
cp config/default.yaml config/default.yaml.backup

# Migrate configuration
sentinair config migrate --from-version 0.9 --to-version 1.0

# Validate migrated configuration
sentinair config validate
```

### Configuration Schema

Sentinair uses JSON Schema for configuration validation. Schema files are located in `schemas/config.json`.

---

*This reference covers all configuration options available in Sentinair v1.0. For the most up-to-date information, consult the official documentation.*
