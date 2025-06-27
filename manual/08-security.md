# Security Best Practices

This comprehensive guide covers security best practices for deploying and operating Sentinair in production environments, with special focus on air-gapped and high-security environments.

## 🛡️ Security Architecture

### Defense in Depth Strategy

```
┌─────────────────────────────────────────────────────────┐
│                    Physical Security                    │
├─────────────────────────────────────────────────────────┤
│                   Network Security                      │
├─────────────────────────────────────────────────────────┤
│                   System Security                       │
├─────────────────────────────────────────────────────────┤
│                 Application Security                    │
├─────────────────────────────────────────────────────────┤
│                    Data Security                        │
└─────────────────────────────────────────────────────────┘
```

### Security Principles
1. **Least Privilege**: Minimum necessary permissions
2. **Zero Trust**: Verify everything, trust nothing
3. **Defense in Depth**: Multiple security layers
4. **Fail Secure**: Default to secure state on failure
5. **Audit Everything**: Comprehensive logging and monitoring

## 🔐 Authentication & Authorization

### Strong Authentication

#### Multi-Factor Authentication Setup
```bash
# Enable MFA for admin access
python main.py --setup-mfa --admin

# Configure MFA methods
python main.py --config-mfa --methods "password,totp,key"

# Test MFA setup
python main.py --test-mfa
```

#### Password Policy Configuration
```yaml
# config/security.yaml
authentication:
  password_policy:
    min_length: 12
    require_uppercase: true
    require_lowercase: true
    require_numbers: true
    require_special: true
    max_age_days: 90
    history_count: 12
    lockout_attempts: 3
    lockout_duration: 30m
  
  session_management:
    timeout: 30m
    max_concurrent: 1
    secure_cookies: true
    
  mfa:
    required_for_admin: true
    required_for_config: true
    totp_window: 30
    backup_codes: 10
```

### Role-Based Access Control (RBAC)

#### Security Roles
```yaml
# config/security_roles.yaml
roles:
  security_admin:
    description: "Full security administration"
    permissions:
      - "system.*"
      - "security.*"
      - "audit.*"
      - "config.*"
      
  security_analyst:
    description: "Security monitoring and analysis"
    permissions:
      - "alerts.view"
      - "alerts.acknowledge"
      - "reports.generate"
      - "dashboard.access"
      - "logs.view"
      
  system_admin:
    description: "System administration without security config"
    permissions:
      - "system.status"
      - "system.restart"
      - "config.view"
      - "logs.view"
      
  readonly_user:
    description: "Read-only access to dashboards"
    permissions:
      - "dashboard.view"
      - "alerts.view"
      - "reports.view"
```

#### Permission Management
```bash
# Create security-focused user
python admin/user_admin.py --create-user security_analyst \
  --role security_analyst \
  --require-mfa \
  --password-policy strict

# Audit user permissions
python admin/security_audit.py --check-permissions

# Review access logs
python admin/access_review.py --period 30days
```

## 🔒 Data Protection

### Encryption Standards

#### Data at Rest
```yaml
# config/encryption.yaml
encryption:
  data_at_rest:
    algorithm: "AES-256-GCM"
    key_derivation: "PBKDF2"
    key_iterations: 100000
    
    # Database encryption
    database:
      enabled: true
      table_level: true
      
    # Log file encryption
    logs:
      enabled: true
      rotate_keys: true
      key_rotation_days: 30
      
    # Configuration encryption
    config:
      sensitive_only: true
      password_encryption: true
```

#### Encryption Key Management
```bash
# Generate new encryption keys
python security/key_manager.py --generate-keys --strength 256

# Rotate encryption keys
python security/key_manager.py --rotate-keys --backup-old

# Key backup (to secure offline storage)
python security/key_manager.py --export-keys --secure-backup /secure/location/
```

### Secure Storage

#### File System Security
```bash
# Set secure permissions
chmod 700 /opt/sentinair/data/
chmod 600 /opt/sentinair/config/*.yaml
chmod 600 /opt/sentinair/data/sentinair.db

# Set file ownership
chown -R sentinair:sentinair /opt/sentinair/
```

#### Database Security
```sql
-- Create database with encryption
CREATE DATABASE sentinair_secure 
  ENCRYPTION_KEY = 'your-encryption-key'
  COMPRESSION = ON;

-- Set secure database permissions
GRANT SELECT, INSERT, UPDATE ON sentinair_secure.* TO 'sentinair'@'localhost';
REVOKE ALL PRIVILEGES ON sentinair_secure.* FROM 'public';
```

## 🌐 Network Security

### Air-Gapped Environment Configuration

#### Network Isolation Verification
```bash
# Verify no internet connectivity
python security/network_check.py --verify-airgap

# Check for unexpected network connections
python security/network_monitor.py --detect-anomalies

# Block all external connections
python security/firewall_config.py --block-external --allow-local
```

#### Internal Network Security
```yaml
# config/network_security.yaml
network:
  airgap_mode: true
  
  allowed_connections:
    - "127.0.0.1"      # Localhost only
    - "192.168.1.0/24" # Internal network (if needed)
    
  blocked_ports:
    - "80"   # HTTP
    - "443"  # HTTPS
    - "53"   # DNS
    - "123"  # NTP
    
  monitoring:
    detect_outbound: true
    alert_external: true
    log_connections: true
```

### Secure Communication

#### Internal API Security
```yaml
# config/api_security.yaml
api:
  authentication:
    method: "bearer_token"
    token_lifetime: "1h"
    refresh_enabled: false
    
  encryption:
    tls_version: "1.3"
    cipher_suites:
      - "TLS_AES_256_GCM_SHA384"
      - "TLS_CHACHA20_POLY1305_SHA256"
      
  rate_limiting:
    requests_per_minute: 100
    burst_size: 10
    
  cors:
    enabled: false  # Disable for security
    
  headers:
    hsts: true
    csp: "default-src 'self'"
    x_frame_options: "DENY"
```

## 🔍 Security Monitoring

### Security Event Detection

#### Security-Focused YARA Rules
```yara
// signatures/security.yar
rule Suspicious_File_Access {
    meta:
        description = "Detects suspicious file access patterns"
        severity = "high"
        
    strings:
        $sensitive1 = "/etc/passwd"
        $sensitive2 = "/etc/shadow"
        $sensitive3 = "C:\\Windows\\System32\\config\\"
        
    condition:
        any of ($sensitive*)
}

rule Data_Exfiltration_Pattern {
    meta:
        description = "Detects potential data exfiltration"
        severity = "critical"
        
    strings:
        $usb = "USB"
        $large_file = { 00 00 ?? ?? }  // Large file header
        
    condition:
        $usb and $large_file
}
```

#### Advanced Threat Detection
```python
# security/threat_detector.py
class SecurityThreatDetector:
    def __init__(self):
        self.threat_patterns = {
            'privilege_escalation': {
                'process_patterns': ['sudo', 'runas', 'net user'],
                'file_patterns': ['/etc/sudoers', 'SAM'],
                'threshold': 3
            },
            'lateral_movement': {
                'network_patterns': ['psexec', 'wmic', 'ssh'],
                'threshold': 2
            },
            'data_staging': {
                'file_patterns': ['*.zip', '*.rar', '*.tar'],
                'size_threshold': '100MB',
                'location_patterns': ['/tmp/', 'C:\\Temp\\']
            }
        }
```

### Security Alerting

#### Critical Security Alerts
```yaml
# config/security_alerts.yaml
security_alerts:
  immediate_response:
    - "privilege_escalation_detected"
    - "data_exfiltration_detected"
    - "unauthorized_access_attempt"
    - "malware_signature_match"
    - "system_file_modification"
    
  escalation_chain:
    level_1: "security_analyst"
    level_2: "security_admin"
    level_3: "ciso"
    
  response_times:
    critical: "5m"
    high: "15m"
    medium: "1h"
    low: "24h"
```

## 🔧 Hardening Guidelines

### System Hardening

#### Operating System Hardening
```bash
# Linux hardening script
#!/bin/bash
# security/harden_linux.sh

# Disable unnecessary services
systemctl disable avahi-daemon
systemctl disable bluetooth
systemctl disable cups

# Configure firewall
ufw enable
ufw default deny incoming
ufw default deny outgoing
ufw allow from 127.0.0.1

# Secure kernel parameters
echo "net.ipv4.ip_forward = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.send_redirects = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.accept_redirects = 0" >> /etc/sysctl.conf

# Set file permissions
chmod 700 /root
chmod 755 /etc/passwd
chmod 600 /etc/shadow

# Configure audit logging
auditctl -w /etc/passwd -p wa -k user_modification
auditctl -w /etc/shadow -p wa -k user_modification
```

#### Windows Hardening
```powershell
# security/harden_windows.ps1

# Disable unnecessary services
Set-Service -Name "RemoteRegistry" -StartupType Disabled
Set-Service -Name "Fax" -StartupType Disabled
Set-Service -Name "TelnetServer" -StartupType Disabled

# Configure Windows Firewall
New-NetFirewallRule -DisplayName "Block Outbound" -Direction Outbound -Action Block
New-NetFirewallRule -DisplayName "Allow Localhost" -Direction Outbound -RemoteAddress 127.0.0.1 -Action Allow

# Enable audit policies
auditpol /set /category:"Logon/Logoff" /success:enable /failure:enable
auditpol /set /category:"Account Management" /success:enable /failure:enable

# Disable PowerShell v2
Disable-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2Root
```

### Application Hardening

#### Sentinair Security Configuration
```yaml
# config/hardened.yaml
security:
  hardening:
    disable_debug: true
    disable_test_modes: true
    secure_defaults: true
    
  runtime_protection:
    memory_protection: true
    code_signing: true
    tamper_detection: true
    
  logging:
    security_events: true
    access_logging: true
    failure_logging: true
    
  limits:
    max_file_size: "100MB"
    max_log_size: "1GB"
    max_memory_usage: "512MB"
    max_cpu_usage: 50
```

## 🕵️ Security Auditing

### Regular Security Audits

#### Automated Security Scan
```bash
# security/security_scan.sh
#!/bin/bash

echo "Sentinair Security Audit - $(date)"
echo "=================================="

# Check file permissions
echo "Checking file permissions..."
python security/check_permissions.py

# Verify encryption status
echo "Checking encryption status..."
python security/verify_encryption.py

# Audit user accounts
echo "Auditing user accounts..."
python security/audit_users.py

# Check for security updates
echo "Checking for security issues..."
python security/vulnerability_scan.py

# Verify configuration security
echo "Checking configuration security..."
python security/config_audit.py

echo "Security audit completed"
```

#### Compliance Checking
```python
# security/compliance_check.py
def check_compliance():
    checks = {
        'password_policy': check_password_policy(),
        'encryption_enabled': check_encryption(),
        'audit_logging': check_audit_logs(),
        'access_controls': check_rbac(),
        'network_security': check_network_isolation(),
        'data_protection': check_data_encryption(),
        'backup_security': check_backup_encryption()
    }
    
    return compliance_report(checks)
```

## 🚨 Incident Response

### Security Incident Procedures

#### Incident Detection
```yaml
# config/incident_response.yaml
incident_response:
  detection:
    automated_triggers:
      - "multiple_failed_logins"
      - "privilege_escalation"
      - "data_exfiltration"
      - "malware_detection"
      - "unauthorized_config_change"
      
  response_levels:
    level_1: "monitor_and_log"
    level_2: "alert_admin"
    level_3: "isolate_system"
    level_4: "emergency_shutdown"
```

#### Automated Response Actions
```python
# security/incident_response.py
class IncidentResponse:
    def handle_security_incident(self, incident_type, severity):
        if severity == 'critical':
            self.isolate_system()
            self.alert_security_team()
            self.preserve_evidence()
            
        elif severity == 'high':
            self.enhance_monitoring()
            self.alert_admin()
            self.collect_evidence()
            
        self.log_incident(incident_type, severity)
```

## 📋 Security Checklist

### Pre-Deployment Security Review
- [ ] All default passwords changed
- [ ] Encryption enabled for all sensitive data
- [ ] Network isolation verified
- [ ] Access controls configured
- [ ] Audit logging enabled
- [ ] Security monitoring active
- [ ] Incident response procedures in place
- [ ] Backup security verified

### Ongoing Security Tasks

#### Daily
- [ ] Review security alerts
- [ ] Check authentication logs
- [ ] Monitor network connections
- [ ] Verify system integrity

#### Weekly
- [ ] Review user access permissions
- [ ] Audit configuration changes
- [ ] Check encryption key status
- [ ] Test backup restoration

#### Monthly
- [ ] Full security audit
- [ ] Update security policies
- [ ] Review incident response procedures
- [ ] Security awareness training

#### Quarterly
- [ ] Penetration testing
- [ ] Security policy review
- [ ] Compliance assessment
- [ ] Security architecture review

## ⚠️ Security Warnings

### Critical Security Considerations
1. **Never disable encryption** in production environments
2. **Regularly rotate encryption keys** and passwords
3. **Monitor all system changes** and access attempts
4. **Maintain air-gap integrity** in isolated environments
5. **Test incident response procedures** regularly
6. **Keep security documentation** up to date
7. **Limit administrative access** to essential personnel only

### Emergency Security Procedures
```bash
# Emergency system lockdown
python security/emergency_lockdown.py --immediate

# Isolate from network
python security/network_isolate.py --complete

# Preserve evidence
python security/evidence_preservation.py --all

# Emergency contact procedures
python security/emergency_contact.py --alert-all
```

---

**Next Steps:**
- [Monitoring & Alerts](09-monitoring.md) - Advanced monitoring setup
- [Custom Rules](11-custom-rules.md) - Security rule customization
- [Troubleshooting](13-troubleshooting.md) - Security troubleshooting
