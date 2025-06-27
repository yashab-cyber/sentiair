# System Administration Guide

This guide covers the administration and management of Sentinair in production environments, including deployment, monitoring, maintenance, and scaling considerations.

## 🏢 Production Deployment

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores, 2.0GHz+
- **RAM**: 4GB (8GB recommended)
- **Storage**: 10GB available space
- **OS**: Windows 10+ or Linux (Ubuntu 18.04+, CentOS 7+)
- **Python**: 3.8+ with pip
- **Permissions**: Administrator/root access for full functionality

#### Recommended Production Setup
- **CPU**: 4 cores, 3.0GHz+
- **RAM**: 16GB+
- **Storage**: 50GB+ SSD
- **Network**: Isolated/air-gapped environment
- **Backup**: Automated backup solution
- **Monitoring**: System monitoring tools

### Multi-System Deployment

#### Central Management Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Endpoint 1    │    │   Endpoint 2    │    │   Endpoint N    │
│   Sentinair     │    │   Sentinair     │    │   Sentinair     │
│   Agent         │    │   Agent         │    │   Agent         │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴───────────┐
                    │   Central Management    │
                    │   Console               │
                    │   - Log Aggregation     │
                    │   - Alert Management    │
                    │   - Configuration       │
                    │   - Reporting           │
                    └─────────────────────────┘
```

#### Deployment Methods

##### 1. Manual Deployment
```bash
# Copy Sentinair to each system
scp -r sentinair/ admin@target-system:/opt/

# Install on each system
ssh admin@target-system
cd /opt/sentinair
sudo python setup.py --production
```

##### 2. Automated Deployment
```bash
# Using deployment script
python examples/deploy.py --targets targets.txt --config production.yaml

# Using Ansible (if available)
ansible-playbook -i inventory sentinair-deploy.yml
```

##### 3. Docker Deployment (if Docker available)
```dockerfile
# Dockerfile for Sentinair
FROM python:3.9-slim

COPY . /app/sentinair
WORKDIR /app/sentinair

RUN pip install -r requirements.txt
RUN python setup.py --docker

EXPOSE 8888
CMD ["python", "main.py", "--docker"]
```

## 🔧 Configuration Management

### Centralized Configuration

#### Configuration Templates
```yaml
# templates/production.yaml
production:
  deployment_type: "enterprise"
  monitoring:
    enabled_monitors: ["file", "usb", "process", "behavior"]
    sensitivity: "high"
    
  security:
    encryption: true
    admin_auth: true
    log_encryption: true
    
  performance:
    max_cpu_usage: 25
    max_memory_mb: 512
    log_rotation_size: "50MB"
    
  alerts:
    immediate_critical: true
    batch_warnings: true
    email_alerts: false  # Air-gapped
    
  ml:
    training_interval: "24h"
    model_retention: 30
    anomaly_threshold: 0.8
```

#### Configuration Distribution
```bash
# Distribute configuration
python admin/distribute_config.py --template production.yaml --targets all

# Validate configuration on all systems
python admin/validate_config.py --check-all

# Update specific setting across all systems
python admin/update_setting.py --key "alerts.sensitivity" --value "high"
```

### Environment-Specific Configurations

#### Development Environment
```yaml
# config/dev.yaml
environment: "development"
logging:
  level: "DEBUG"
  console_output: true
  
monitoring:
  reduced_checks: true
  test_mode: true
  
alerts:
  suppress_non_critical: true
```

#### Staging Environment
```yaml
# config/staging.yaml
environment: "staging"
logging:
  level: "INFO"
  
monitoring:
  full_monitoring: true
  test_alerts: true
  
ml:
  training_interval: "6h"  # More frequent for testing
```

#### Production Environment
```yaml
# config/production.yaml
environment: "production"
logging:
  level: "WARNING"
  console_output: false
  
monitoring:
  full_monitoring: true
  performance_optimized: true
  
security:
  maximum_security: true
  audit_logging: true
```

## 📊 Monitoring & Health Checks

### System Health Monitoring

#### Health Check Script
```bash
#!/bin/bash
# admin/health_check.sh

echo "Sentinair Health Check - $(date)"
echo "================================"

# Check if Sentinair is running
if pgrep -f "main.py" > /dev/null; then
    echo "✅ Sentinair process running"
else
    echo "❌ Sentinair process not running"
    exit 1
fi

# Check CPU usage
CPU_USAGE=$(ps -p $(pgrep -f "main.py") -o %cpu= | awk '{print int($1)}')
if [ $CPU_USAGE -lt 50 ]; then
    echo "✅ CPU usage: ${CPU_USAGE}%"
else
    echo "⚠️  High CPU usage: ${CPU_USAGE}%"
fi

# Check memory usage
MEM_USAGE=$(ps -p $(pgrep -f "main.py") -o %mem= | awk '{print int($1)}')
if [ $MEM_USAGE -lt 20 ]; then
    echo "✅ Memory usage: ${MEM_USAGE}%"
else
    echo "⚠️  High memory usage: ${MEM_USAGE}%"
fi

# Check disk space
DISK_USAGE=$(df /opt/sentinair | awk 'NR==2 {print int($5)}')
if [ $DISK_USAGE -lt 80 ]; then
    echo "✅ Disk usage: ${DISK_USAGE}%"
else
    echo "⚠️  High disk usage: ${DISK_USAGE}%"
fi

# Check log file sizes
LOG_SIZE=$(du -sh /opt/sentinair/data/logs/ | cut -f1)
echo "📊 Log directory size: $LOG_SIZE"

# Check database size
DB_SIZE=$(du -sh /opt/sentinair/data/sentinair.db | cut -f1)
echo "📊 Database size: $DB_SIZE"

echo "Health check completed"
```

#### Automated Health Monitoring
```bash
# Add to crontab for regular health checks
# */15 * * * * /opt/sentinair/admin/health_check.sh >> /var/log/sentinair_health.log

# Setup monitoring with alerts
python admin/setup_monitoring.py --interval 15m --alert-email admin@company.com
```

### Performance Monitoring

#### Performance Metrics Collection
```python
# admin/performance_monitor.py
import psutil
import time
import json

def collect_metrics():
    # Get Sentinair process
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'main.py' in proc.info['cmdline']:
            sentinair_proc = psutil.Process(proc.info['pid'])
            break
    
    metrics = {
        'timestamp': time.time(),
        'cpu_percent': sentinair_proc.cpu_percent(),
        'memory_mb': sentinair_proc.memory_info().rss / 1024 / 1024,
        'threads': sentinair_proc.num_threads(),
        'open_files': len(sentinair_proc.open_files()),
        'connections': len(sentinair_proc.connections()),
    }
    
    return metrics

# Run performance monitoring
python admin/performance_monitor.py --duration 24h --output metrics.json
```

## 🔒 Security Administration

### Access Control

#### User Management
```bash
# Create admin user
python admin/user_admin.py --create-admin --username security_admin

# Create read-only user
python admin/user_admin.py --create-user --username analyst --role readonly

# List users
python admin/user_admin.py --list-users

# Change user permissions
python admin/user_admin.py --modify-user analyst --add-permission view_alerts
```

#### Role-Based Access Control
```yaml
# config/rbac.yaml
roles:
  admin:
    permissions:
      - "system.manage"
      - "config.modify"
      - "users.manage"
      - "alerts.manage"
      - "reports.generate"
      - "logs.access"
      
  analyst:
    permissions:
      - "alerts.view"
      - "reports.view"
      - "dashboards.access"
      
  readonly:
    permissions:
      - "dashboard.view"
      - "status.check"
```

### Audit Logging

#### Security Event Auditing
```python
# Enable comprehensive audit logging
python main.py --enable-audit-logging

# Audit log configuration
audit:
  enabled: true
  log_level: "INFO"
  events:
    - "user_login"
    - "config_change"
    - "alert_acknowledgment"
    - "report_generation"
    - "system_shutdown"
    - "file_access"
  
  retention: 90  # days
  encryption: true
  tamper_protection: true
```

## 🔄 Backup & Recovery

### Backup Strategy

#### What to Backup
1. **Configuration Files**
   - `config/default.yaml`
   - Custom configuration files
   - RBAC settings

2. **Database**
   - `data/sentinair.db`
   - Model files in `data/models/`

3. **Logs** (if required for compliance)
   - `data/logs/`

4. **Custom Rules**
   - `signatures/` directory
   - Custom YARA rules

#### Backup Script
```bash
#!/bin/bash
# admin/backup.sh

BACKUP_DIR="/backup/sentinair/$(date +%Y%m%d_%H%M%S)"
SENTINAIR_DIR="/opt/sentinair"

mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r "$SENTINAIR_DIR/config" "$BACKUP_DIR/"

# Backup database
cp "$SENTINAIR_DIR/data/sentinair.db" "$BACKUP_DIR/"

# Backup models
cp -r "$SENTINAIR_DIR/data/models" "$BACKUP_DIR/"

# Backup signatures
cp -r "$SENTINAIR_DIR/signatures" "$BACKUP_DIR/"

# Backup logs (last 7 days)
find "$SENTINAIR_DIR/data/logs" -mtime -7 -type f -exec cp {} "$BACKUP_DIR/logs/" \;

# Create backup manifest
echo "Backup created: $(date)" > "$BACKUP_DIR/manifest.txt"
echo "Sentinair version: $(python $SENTINAIR_DIR/main.py --version)" >> "$BACKUP_DIR/manifest.txt"

# Compress backup
tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname $BACKUP_DIR)" "$(basename $BACKUP_DIR)"
rm -rf "$BACKUP_DIR"

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

#### Automated Backup
```bash
# Daily backup cron job
0 2 * * * /opt/sentinair/admin/backup.sh

# Weekly full backup with retention
0 3 * * 0 /opt/sentinair/admin/full_backup.sh --retain 4
```

### Recovery Procedures

#### System Recovery
```bash
# 1. Stop Sentinair
python main.py --shutdown

# 2. Restore from backup
tar -xzf backup_20250627_020000.tar.gz
cp -r backup_20250627_020000/config/* /opt/sentinair/config/
cp backup_20250627_020000/sentinair.db /opt/sentinair/data/

# 3. Verify restore
python admin/verify_restore.py

# 4. Restart Sentinair
python main.py --start
```

## 📈 Scaling Considerations

### Vertical Scaling
- **CPU**: Add more cores for ML processing
- **Memory**: Increase RAM for larger datasets
- **Storage**: Add fast SSD for better I/O performance

### Horizontal Scaling
- **Load Balancing**: Distribute monitoring across multiple systems
- **Data Aggregation**: Central log collection and analysis
- **Redundancy**: Multiple monitoring nodes for high availability

### Performance Optimization
```yaml
# config/performance.yaml
performance:
  cpu_optimization:
    worker_threads: 4
    ml_threads: 2
    io_threads: 2
    
  memory_optimization:
    cache_size_mb: 256
    buffer_size_mb: 64
    gc_threshold: 1000
    
  storage_optimization:
    log_compression: true
    db_optimization: true
    file_cache_size: 100
```

## 🚨 Troubleshooting Administration Issues

### Common Admin Issues

#### High Resource Usage
```bash
# Check resource usage
python admin/resource_check.py

# Optimize configuration
python admin/optimize_config.py --reduce-memory --reduce-cpu

# Restart with optimized settings
python main.py --restart --config optimized.yaml
```

#### Service Won't Start
```bash
# Check dependencies
python admin/check_dependencies.py

# Verify configuration
python admin/validate_config.py

# Check permissions
python admin/check_permissions.py

# Start in debug mode
python main.py --debug --verbose
```

## 📋 Administration Checklist

### Daily Tasks
- [ ] Check system health status
- [ ] Review critical alerts
- [ ] Monitor resource usage
- [ ] Verify backup completion

### Weekly Tasks
- [ ] Review performance metrics
- [ ] Analyze alert patterns
- [ ] Check log file sizes
- [ ] Test emergency procedures

### Monthly Tasks
- [ ] Update configuration as needed
- [ ] Review user access permissions
- [ ] Analyze security events
- [ ] Plan capacity upgrades

### Quarterly Tasks
- [ ] Full system audit
- [ ] Documentation updates
- [ ] Security assessment
- [ ] Disaster recovery testing

---

**Next Steps:**
- [Security Best Practices](08-security.md) - Comprehensive security guide
- [Monitoring & Alerts](09-monitoring.md) - Advanced monitoring setup
- [Performance Tuning](14-performance.md) - Optimization techniques
