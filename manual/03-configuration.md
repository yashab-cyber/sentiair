# Configuration Guide

Complete guide to configuring Sentinair for your environment and security requirements.

## 📁 Configuration Files

### Main Configuration
- **Location**: `config/default.yaml`
- **Custom Config**: `config/sentinair.yaml` (overrides default)
- **Environment**: Environment variables (highest priority)

### Configuration Priority
1. Environment variables (highest)
2. Custom config file (`config/sentinair.yaml`)
3. Default config file (`config/default.yaml`)
4. Built-in defaults (lowest)

## 🔧 Basic Configuration

### Database Settings
```yaml
database:
  path: "data/sentinair.db"
  backup_enabled: true
  backup_interval: 24  # hours
  max_events: 100000   # maximum events to store
  cleanup_days: 90     # days to keep old events
```

### Logging Configuration
```yaml
logging:
  level: "INFO"                    # DEBUG, INFO, WARNING, ERROR
  file: "data/logs/sentinair.log"
  max_size: 10                     # MB
  backup_count: 5
  console_output: true
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Monitoring Modules
```yaml
monitoring:
  enabled: true
  check_interval: 5              # seconds between checks
  
  file_monitoring:
    enabled: true
    paths:
      - "/home"
      - "/etc"
      - "/var/log"
    exclude_patterns:
      - "*.tmp"
      - "*.swp"
      - "__pycache__"
    max_file_size: 1000          # MB, files larger are skipped
  
  process_monitoring:
    enabled: true
    check_new_processes: true
    check_process_changes: true
    whitelist_processes:
      - "systemd"
      - "kernel"
      - "ssh"
  
  usb_monitoring:
    enabled: true
    auto_block_unknown: false
    whitelist_devices: []
    
  behavior_monitoring:
    enabled: true
    track_user_patterns: true
    track_application_usage: true
    suspicious_activity_threshold: 0.7
```

## 🤖 Machine Learning Configuration

### Anomaly Detection
```yaml
ml:
  enabled: true
  model_type: "isolation_forest"   # isolation_forest, autoencoder, ensemble
  
  # Model parameters
  contamination: 0.1               # expected anomaly ratio
  n_estimators: 100                # for isolation forest
  max_samples: 256                 # training sample size
  
  # Training settings
  auto_train: true
  retrain_interval: 168            # hours (weekly)
  min_training_samples: 1000
  
  # Feature engineering
  features:
    time_based: true               # hour, day of week, etc.
    process_based: true            # process names, PIDs
    file_based: true               # file paths, sizes, extensions
    user_based: true               # user behavior patterns
    network_based: false           # network activity (future)
  
  # Model persistence
  save_models: true
  model_path: "data/models/"
  backup_models: true
```

### Advanced ML Settings
```yaml
ml_advanced:
  # Ensemble methods
  ensemble:
    enabled: false
    models:
      - "isolation_forest"
      - "one_class_svm"
      - "local_outlier_factor"
    voting_method: "soft"          # soft, hard
    
  # Deep learning (experimental)
  deep_learning:
    enabled: false
    architecture: "autoencoder"
    hidden_layers: [64, 32, 16, 32, 64]
    epochs: 100
    batch_size: 32
    
  # Feature selection
  feature_selection:
    enabled: true
    method: "variance_threshold"   # variance_threshold, mutual_info
    threshold: 0.01
```

## 🚨 Alert Configuration

### Alert Settings
```yaml
alerts:
  enabled: true
  
  # Severity thresholds
  thresholds:
    low: 0.3
    medium: 0.6
    high: 0.8
    critical: 0.9
  
  # Notification methods
  notifications:
    gui: true                      # desktop notifications
    email: false                   # email alerts
    syslog: true                   # system log
    webhook: false                 # HTTP webhooks
    file: true                     # log to file
  
  # Rate limiting
  rate_limiting:
    enabled: true
    max_alerts_per_minute: 10
    cooldown_period: 300           # seconds
  
  # Auto-acknowledgment
  auto_acknowledge:
    enabled: false
    low_severity_timeout: 3600     # auto-ack low alerts after 1 hour
    duplicate_threshold: 5         # auto-ack after 5 duplicates
```

### Email Notifications
```yaml
alerts:
  notifications:
    email: true
    email_config:
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      use_tls: true
      username: "your-email@gmail.com"
      password: "your-app-password"  # Use app passwords, not account password
      from_address: "sentinair@yourcompany.com"
      to_addresses:
        - "admin@yourcompany.com"
        - "security@yourcompany.com"
      subject_prefix: "[SENTINAIR ALERT]"
```

### Webhook Notifications
```yaml
alerts:
  notifications:
    webhook: true
    webhook_config:
      url: "https://your-webhook-endpoint.com/alerts"
      method: "POST"
      headers:
        "Authorization": "Bearer your-token"
        "Content-Type": "application/json"
      timeout: 30                  # seconds
      retry_attempts: 3
```

## 🔒 Security Configuration

### Encryption Settings
```yaml
security:
  encryption:
    enabled: true
    algorithm: "AES-256-GCM"
    key_file: "config/encryption.key"
    auto_rotate_keys: true
    rotation_interval: 2160        # hours (90 days)
  
  access_control:
    require_authentication: true
    session_timeout: 3600          # seconds
    max_failed_attempts: 5
    lockout_duration: 900          # seconds (15 minutes)
  
  stealth_mode:
    enabled: false
    unlock_key: "change-this-secret-key"
    hide_process: true
    fake_process_name: "system_update"
```

### YARA Rules
```yaml
detection:
  yara:
    enabled: true
    rules_path: "signatures/"
    auto_update: false             # auto-download new rules
    custom_rules: true             # load custom rules
    
    rule_categories:
      malware: true
      suspicious: true
      pua: false                   # potentially unwanted applications
      testing: false               # test rules only
```

## 🌐 Network Configuration (Future)

### Network Monitoring
```yaml
network:
  enabled: false                   # Coming in future version
  interfaces:
    - "eth0"
    - "wlan0"
  
  monitoring:
    connections: true
    traffic_analysis: true
    dns_monitoring: true
    
  detection:
    suspicious_connections: true
    data_exfiltration: true
    c2_communication: true
```

## 🎯 Environment-Specific Configurations

### Air-Gapped Environment
```yaml
# config/airgap.yaml
monitoring:
  network_monitoring:
    enabled: false               # No network in air-gapped
  usb_monitoring:
    enabled: true
    auto_block_unknown: true     # Block all unknown USB devices
    strict_mode: true

alerts:
  notifications:
    email: false                 # No email in air-gapped
    webhook: false               # No webhooks
    file: true                   # Log to files only
    gui: true                    # Local notifications only

ml:
  auto_update_models: false      # No model updates from internet
  offline_mode: true
```

### High-Security Environment
```yaml
# config/high-security.yaml
monitoring:
  check_interval: 1              # More frequent monitoring
  
detection:
  sensitivity: "high"
  strict_mode: true
  
alerts:
  thresholds:
    low: 0.2                     # Lower thresholds
    medium: 0.4
    high: 0.6
    critical: 0.8
  
  rate_limiting:
    enabled: false               # Don't limit alerts in high-security

security:
  access_control:
    require_authentication: true
    session_timeout: 1800        # 30 minutes
    max_failed_attempts: 3
```

### Development Environment
```yaml
# config/development.yaml
logging:
  level: "DEBUG"
  console_output: true

monitoring:
  check_interval: 10             # Less frequent for development
  
alerts:
  notifications:
    gui: true
    email: false                 # No email spam during development
    
ml:
  auto_train: false              # Manual training for testing
```

## 🔄 Dynamic Configuration

### Runtime Configuration Changes
```bash
# Via CLI
sentinair> config set monitoring.check_interval 10
sentinair> config set alerts.thresholds.high 0.9
sentinair> config reload

# Via API (future)
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{"monitoring.check_interval": 10}'
```

### Environment Variables
```bash
# Override any config setting
export SENTINAIR_MONITORING_CHECK_INTERVAL=5
export SENTINAIR_ALERTS_NOTIFICATIONS_EMAIL=true
export SENTINAIR_ML_CONTAMINATION=0.05
```

## 📊 Performance Tuning

### High-Performance Settings
```yaml
performance:
  # Database optimization
  database:
    connection_pool_size: 10
    batch_insert_size: 1000
    vacuum_interval: 168         # hours
  
  # Memory management
  memory:
    max_cache_size: 512          # MB
    gc_threshold: 1000           # objects
  
  # Processing optimization
  processing:
    max_workers: 4               # parallel processing threads
    queue_size: 10000            # event queue size
    batch_processing: true
```

### Resource-Constrained Settings
```yaml
performance:
  # Minimal resource usage
  database:
    connection_pool_size: 2
    batch_insert_size: 100
  
  memory:
    max_cache_size: 64           # MB
    gc_threshold: 500
  
  processing:
    max_workers: 1
    queue_size: 1000
    batch_processing: false
  
  monitoring:
    check_interval: 30           # Less frequent checks
```

## 🔍 Validation and Testing

### Configuration Validation
```bash
# Test configuration
python main.py --validate-config

# Test specific settings
python -c "
from utils.config import Config
config = Config('config/your-config.yaml')
print('✅ Configuration valid')
"
```

### Configuration Templates
```bash
# Generate template for specific environment
python main.py --generate-config --environment production
python main.py --generate-config --environment development
python main.py --generate-config --environment airgap
```

---

**Previous**: [Quick Start Guide](02-quickstart.md) | **Next**: [GUI User Guide](04-gui-guide.md)
