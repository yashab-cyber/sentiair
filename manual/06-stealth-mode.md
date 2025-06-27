# Stealth Mode - Hidden Operation

Stealth Mode allows Sentinair to run completely hidden in the background, providing security monitoring without user visibility. This mode is ideal for security teams who need covert monitoring capabilities.

## 🔒 Overview

Stealth Mode provides:
- **Invisible Operation**: No GUI windows or obvious system presence
- **Background Monitoring**: Continuous security monitoring without user awareness
- **Admin Authentication**: Secure access control for authorized personnel
- **Hidden Logs**: Encrypted log storage in secure locations
- **Emergency Access**: Special key combinations for emergency access

## 🚀 Starting Stealth Mode

### Command Line
```bash
# Start in stealth mode
python main.py --stealth

# Start with custom config
python main.py --stealth --config /path/to/stealth.yaml

# Start with specific password
python main.py --stealth --auth-key your_secret_key
```

### Windows Service
```powershell
# Install as Windows service (stealth)
python main.py --install-service --stealth

# Start service
net start sentinair

# Stop service
net stop sentinair
```

### Linux Daemon
```bash
# Install as system daemon
sudo python main.py --install-daemon --stealth

# Start daemon
sudo systemctl start sentinair

# Enable auto-start
sudo systemctl enable sentinair
```

## 🔐 Authentication & Access

### Setting Up Stealth Authentication
```bash
# Set stealth password during setup
python setup.py --stealth-auth

# Change stealth password
python main.py --change-stealth-auth
```

### Emergency Access Methods

#### Method 1: Key Combination
- **Windows**: `Ctrl + Alt + Shift + S`
- **Linux**: `Ctrl + Alt + Shift + S`

#### Method 2: Command Line
```bash
# Reveal stealth instance
python main.py --reveal-stealth

# Stop stealth mode
python main.py --stop-stealth
```

#### Method 3: Special File
Create a file named `.sentinair_reveal` in the home directory:
```bash
# Linux/Mac
touch ~/.sentinair_reveal

# Windows
echo. > %USERPROFILE%\.sentinair_reveal
```

## ⚙️ Stealth Configuration

### Stealth-Specific Settings
```yaml
# config/stealth.yaml
stealth:
  mode: true
  auth_required: true
  auth_timeout: 300  # 5 minutes
  
  # Hiding options
  hide_process_name: true
  hide_logs: true
  hide_alerts: false  # Emergency alerts still show
  
  # Emergency settings
  emergency_reveal: true
  emergency_key: "Ctrl+Alt+Shift+S"
  emergency_file: ".sentinair_reveal"
  
  # Monitoring in stealth
  reduced_monitoring: false
  silent_alerts: true
  log_rotation: true
```

### Process Hiding
```yaml
process:
  hide_name: true
  fake_name: "svchost.exe"  # Windows
  fake_name_linux: "systemd-resolve"  # Linux
  cpu_throttle: true  # Reduce CPU usage
  memory_limit: 256MB  # Limit memory usage
```

## 📊 Monitoring in Stealth Mode

### What Gets Monitored
- ✅ File system changes
- ✅ USB device events
- ✅ Process launches
- ✅ Network connections (if enabled)
- ✅ User behavior patterns
- ✅ Security events

### Stealth Logging
```yaml
logging:
  stealth_logs: true
  log_location: "/var/log/.sentinair"  # Hidden location
  encryption: true
  rotate_size: "10MB"
  max_files: 5
  
  # Log levels in stealth
  console_level: "NONE"
  file_level: "INFO"
  alert_level: "WARNING"
```

## 🚨 Alerts in Stealth Mode

### Alert Behavior
- **Critical Alerts**: Always shown (security threats)
- **Warning Alerts**: Logged only, no popup
- **Info Alerts**: Logged only
- **Emergency Alerts**: Force reveal and show

### Emergency Alert Configuration
```yaml
alerts:
  stealth_mode:
    critical_show: true
    warning_show: false
    info_show: false
    
    # Emergency conditions that force reveal
    emergency_conditions:
      - "multiple_usb_insertions"
      - "suspicious_process_execution"
      - "data_exfiltration_detected"
      - "encryption_anomaly"
```

## 🔧 Stealth Administration

### Remote Management
```bash
# Connect to stealth instance remotely
python main.py --stealth-admin --host localhost --port 8888

# View stealth status
python main.py --stealth-status

# Retrieve stealth logs
python main.py --stealth-logs --export /path/to/export
```

### Stealth Health Monitoring
```bash
# Check if stealth is running
python main.py --stealth-check

# Stealth performance metrics
python main.py --stealth-metrics

# Restart stealth monitoring
python main.py --stealth-restart
```

## 🛡️ Security Considerations

### Stealth Security Features
- **Encrypted Storage**: All stealth data encrypted with AES-256
- **Secure Authentication**: Multi-factor authentication support
- **Process Protection**: Anti-tampering measures
- **Log Integrity**: Cryptographic log signing
- **Memory Protection**: Sensitive data cleared from memory

### Best Practices
1. **Change Default Passwords**: Always set custom authentication
2. **Limit Access**: Only authorized personnel should know stealth is running
3. **Regular Checks**: Monitor stealth health regularly
4. **Secure Logs**: Protect log files with appropriate permissions
5. **Network Isolation**: Consider network monitoring restrictions

## 🚫 Uninstalling Stealth Mode

### Graceful Shutdown
```bash
# Stop stealth mode gracefully
python main.py --stop-stealth --auth your_password

# Remove stealth service/daemon
python main.py --remove-stealth-service
```

### Emergency Stop
```bash
# Force stop (if normal methods fail)
python main.py --force-stop-stealth

# Clean stealth artifacts
python main.py --clean-stealth
```

## 📋 Stealth Mode Checklist

### Pre-Deployment
- [ ] Set strong stealth authentication password
- [ ] Configure emergency access methods
- [ ] Test reveal mechanisms
- [ ] Set appropriate log locations
- [ ] Configure alert thresholds

### During Operation
- [ ] Monitor stealth health regularly
- [ ] Check log rotation and storage
- [ ] Verify alert delivery for critical events
- [ ] Test emergency access periodically

### Maintenance
- [ ] Regular password changes
- [ ] Log cleanup and archival
- [ ] Performance monitoring
- [ ] Security audit of stealth components

## ⚠️ Important Warnings

- **Legal Compliance**: Ensure stealth monitoring complies with local laws
- **User Privacy**: Be transparent about monitoring where required
- **System Impact**: Monitor system performance in stealth mode
- **Detection Risk**: Some security tools may detect stealth operation
- **Emergency Access**: Always have multiple ways to access/stop stealth mode

---

**Next Steps:**
- [System Administration](07-administration.md) - Managing production deployments
- [Security Best Practices](08-security.md) - Comprehensive security guide
- [Troubleshooting](13-troubleshooting.md) - Solving stealth mode issues
