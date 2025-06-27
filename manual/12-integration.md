# Integration Guide

This comprehensive guide covers integrating Sentinair with external systems, APIs, and third-party security tools, while maintaining air-gap security requirements.

## 🔗 Integration Architecture

### Integration Patterns for Air-Gapped Environments

```
┌─────────────────────────────────────────────────────────┐
│                Air-Gapped Network                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ Sentinair   │────│ Local SIEM  │────│ Dashboard   │ │
│  │ Instance 1  │    │             │    │ Server      │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ Sentinair   │────│ File Share  │────│ Backup      │ │
│  │ Instance 2  │    │ (Logs)      │    │ System      │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Integration Methods
1. **File-Based Integration**: JSON/CSV/XML file exchange
2. **Database Integration**: Shared database access
3. **API Integration**: RESTful APIs for local systems
4. **Message Queue**: Local message broker integration
5. **Log Integration**: Syslog and log file sharing

## 🔌 API Integration

### Sentinair REST API

#### API Configuration
```yaml
# config/api.yaml
api:
  enabled: true
  host: "127.0.0.1"  # Local only for security
  port: 8888
  ssl: true
  authentication:
    method: "api_key"
    require_auth: true
    
  endpoints:
    alerts: "/api/v1/alerts"
    events: "/api/v1/events"
    status: "/api/v1/status"
    config: "/api/v1/config"
    reports: "/api/v1/reports"
    
  rate_limiting:
    enabled: true
    requests_per_minute: 100
    
  cors:
    enabled: false  # Disabled for security
```

#### API Authentication
```python
# api/auth.py
class APIAuthentication:
    def __init__(self):
        self.api_keys = self.load_api_keys()
        
    def generate_api_key(self, client_name, permissions):
        api_key = secrets.token_urlsafe(32)
        key_data = {
            'key': api_key,
            'client': client_name,
            'permissions': permissions,
            'created': time.time(),
            'expires': time.time() + (365 * 24 * 3600)  # 1 year
        }
        self.store_api_key(key_data)
        return api_key
        
    def validate_api_key(self, api_key):
        key_data = self.api_keys.get(api_key)
        if not key_data:
            return False
            
        if time.time() > key_data['expires']:
            return False
            
        return key_data

# Usage
auth = APIAuthentication()
api_key = auth.generate_api_key("SIEM_System", ["read_alerts", "read_events"])
```

### API Endpoints

#### Alert Management API
```python
# api/endpoints/alerts.py
from flask import Flask, request, jsonify
from flask_httpauth import HTTPTokenAuth

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    return APIAuthentication().validate_api_key(token)

@app.route('/api/v1/alerts', methods=['GET'])
@auth.login_required
def get_alerts():
    """Get alerts with optional filtering"""
    # Query parameters
    severity = request.args.get('severity')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    limit = int(request.args.get('limit', 100))
    
    # Build query
    query = AlertQuery()
    if severity:
        query.filter_by_severity(severity)
    if start_time:
        query.filter_by_start_time(start_time)
    if end_time:
        query.filter_by_end_time(end_time)
        
    alerts = query.limit(limit).execute()
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts],
        'count': len(alerts),
        'total': query.count()
    })

@app.route('/api/v1/alerts/<alert_id>', methods=['GET'])
@auth.login_required
def get_alert(alert_id):
    """Get specific alert details"""
    alert = AlertManager().get_alert(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
        
    return jsonify(alert.to_dict())

@app.route('/api/v1/alerts/<alert_id>/acknowledge', methods=['POST'])
@auth.login_required
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    data = request.get_json()
    user = data.get('user', 'API')
    comment = data.get('comment', '')
    
    result = AlertManager().acknowledge_alert(alert_id, user, comment)
    if result:
        return jsonify({'status': 'acknowledged'})
    else:
        return jsonify({'error': 'Failed to acknowledge alert'}), 400
```

#### System Status API
```python
# api/endpoints/status.py
@app.route('/api/v1/status', methods=['GET'])
@auth.login_required
def get_system_status():
    """Get system status and health"""
    status = {
        'system': {
            'running': SystemMonitor().is_running(),
            'uptime': SystemMonitor().get_uptime(),
            'version': get_version(),
            'mode': get_current_mode()
        },
        'monitoring': {
            'file_monitor': FileMonitor().is_active(),
            'usb_monitor': USBMonitor().is_active(),
            'process_monitor': ProcessMonitor().is_active(),
            'behavior_monitor': BehaviorMonitor().is_active()
        },
        'performance': {
            'cpu_usage': get_cpu_usage(),
            'memory_usage': get_memory_usage(),
            'disk_usage': get_disk_usage()
        },
        'alerts': {
            'total_today': AlertManager().count_today(),
            'critical_open': AlertManager().count_critical_open(),
            'last_alert': AlertManager().get_last_alert_time()
        }
    }
    
    return jsonify(status)
```

#### Configuration API
```python
# api/endpoints/config.py
@app.route('/api/v1/config', methods=['GET'])
@auth.login_required
def get_config():
    """Get current configuration"""
    config = ConfigManager().get_all_config()
    # Remove sensitive information
    config = sanitize_config(config)
    return jsonify(config)

@app.route('/api/v1/config', methods=['PUT'])
@auth.login_required
def update_config():
    """Update configuration"""
    data = request.get_json()
    
    # Validate configuration
    validator = ConfigValidator()
    if not validator.validate(data):
        return jsonify({'error': 'Invalid configuration', 
                       'details': validator.get_errors()}), 400
    
    # Update configuration
    config_manager = ConfigManager()
    result = config_manager.update_config(data)
    
    if result:
        return jsonify({'status': 'updated'})
    else:
        return jsonify({'error': 'Failed to update configuration'}), 500
```

### API Client Examples

#### Python Client
```python
# clients/python_client.py
import requests
import json

class SentinairAPIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
    def get_alerts(self, severity=None, limit=100):
        """Get alerts from Sentinair"""
        params = {'limit': limit}
        if severity:
            params['severity'] = severity
            
        response = requests.get(
            f'{self.base_url}/api/v1/alerts',
            headers=self.headers,
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'API Error: {response.status_code}')
            
    def acknowledge_alert(self, alert_id, user, comment=""):
        """Acknowledge an alert"""
        data = {
            'user': user,
            'comment': comment
        }
        
        response = requests.post(
            f'{self.base_url}/api/v1/alerts/{alert_id}/acknowledge',
            headers=self.headers,
            json=data
        )
        
        return response.status_code == 200
        
    def get_system_status(self):
        """Get system status"""
        response = requests.get(
            f'{self.base_url}/api/v1/status',
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'API Error: {response.status_code}')

# Usage example
client = SentinairAPIClient('https://localhost:8888', 'your_api_key')
alerts = client.get_alerts(severity='critical')
status = client.get_system_status()
```

#### PowerShell Client
```powershell
# clients/powershell_client.ps1
class SentinairAPI {
    [string]$BaseUrl
    [hashtable]$Headers
    
    SentinairAPI([string]$baseUrl, [string]$apiKey) {
        $this.BaseUrl = $baseUrl
        $this.Headers = @{
            'Authorization' = "Bearer $apiKey"
            'Content-Type' = 'application/json'
        }
    }
    
    [object] GetAlerts([string]$severity, [int]$limit) {
        $uri = "$($this.BaseUrl)/api/v1/alerts?limit=$limit"
        if ($severity) {
            $uri += "&severity=$severity"
        }
        
        try {
            $response = Invoke-RestMethod -Uri $uri -Headers $this.Headers -Method GET
            return $response
        }
        catch {
            throw "API Error: $($_.Exception.Message)"
        }
    }
    
    [bool] AcknowledgeAlert([string]$alertId, [string]$user, [string]$comment) {
        $uri = "$($this.BaseUrl)/api/v1/alerts/$alertId/acknowledge"
        $body = @{
            user = $user
            comment = $comment
        } | ConvertTo-Json
        
        try {
            Invoke-RestMethod -Uri $uri -Headers $this.Headers -Method POST -Body $body
            return $true
        }
        catch {
            return $false
        }
    }
}

# Usage
$api = [SentinairAPI]::new('https://localhost:8888', 'your_api_key')
$alerts = $api.GetAlerts('critical', 50)
```

## 📊 SIEM Integration

### Log Format Standardization

#### CEF (Common Event Format)
```python
# integration/cef_formatter.py
class CEFFormatter:
    def __init__(self):
        self.vendor = "ZehraSec"
        self.product = "Sentinair"
        self.version = "1.0"
        
    def format_alert(self, alert):
        """Format alert as CEF"""
        # CEF Header
        device_vendor = self.vendor
        device_product = self.product
        device_version = self.version
        signature_id = alert.get('rule_id', 'unknown')
        name = alert.get('title', 'Sentinair Alert')
        severity = self.map_severity(alert.get('severity', 'medium'))
        
        # CEF Extensions
        extensions = {
            'src': alert.get('source_ip', ''),
            'dst': alert.get('dest_ip', ''),
            'suser': alert.get('user', ''),
            'fname': alert.get('filename', ''),
            'msg': alert.get('description', ''),
            'cs1': alert.get('category', ''),
            'cs1Label': 'Category',
            'cn1': alert.get('confidence', 0),
            'cn1Label': 'Confidence'
        }
        
        # Build CEF string
        cef_header = f"CEF:0|{device_vendor}|{device_product}|{device_version}|{signature_id}|{name}|{severity}"
        cef_extensions = "|".join([f"{k}={v}" for k, v in extensions.items() if v])
        
        return f"{cef_header}|{cef_extensions}"
        
    def map_severity(self, severity):
        """Map Sentinair severity to CEF severity"""
        mapping = {
            'low': 3,
            'medium': 5,
            'high': 8,
            'critical': 10
        }
        return mapping.get(severity.lower(), 5)
```

#### LEEF (Log Event Extended Format)
```python
# integration/leef_formatter.py
class LEEFFormatter:
    def format_alert(self, alert):
        """Format alert as LEEF"""
        # LEEF Header
        version = "2.0"
        vendor = "ZehraSec"
        product = "Sentinair"
        product_version = "1.0"
        event_id = alert.get('rule_id', 'unknown')
        delimiter = "|"
        
        # LEEF Attributes
        attributes = {
            'devTime': alert.get('timestamp'),
            'severity': alert.get('severity'),
            'eventId': event_id,
            'srcIP': alert.get('source_ip', ''),
            'usrName': alert.get('user', ''),
            'fileName': alert.get('filename', ''),
            'msg': alert.get('description', ''),
            'cat': alert.get('category', '')
        }
        
        # Build LEEF string
        leef_header = f"LEEF:{version}{delimiter}{vendor}{delimiter}{product}{delimiter}{product_version}{delimiter}{event_id}{delimiter}"
        leef_attributes = "\t".join([f"{k}={v}" for k, v in attributes.items() if v])
        
        return f"{leef_header}{leef_attributes}"
```

### Syslog Integration

#### Syslog Configuration
```python
# integration/syslog_integration.py
import logging
import logging.handlers

class SyslogIntegration:
    def __init__(self, syslog_server="localhost", port=514, facility="local0"):
        self.logger = logging.getLogger('sentinair_syslog')
        self.logger.setLevel(logging.INFO)
        
        # Create syslog handler
        handler = logging.handlers.SysLogHandler(
            address=(syslog_server, port),
            facility=facility
        )
        
        # Set format
        formatter = logging.Formatter(
            'Sentinair[%(process)d]: %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        
    def send_alert(self, alert):
        """Send alert to syslog"""
        severity_map = {
            'low': logging.INFO,
            'medium': logging.WARNING,
            'high': logging.ERROR,
            'critical': logging.CRITICAL
        }
        
        level = severity_map.get(alert.get('severity', 'medium'), logging.WARNING)
        message = f"ALERT: {alert.get('title', 'Unknown')} - {alert.get('description', '')}"
        
        self.logger.log(level, message)
```

## 📁 File-Based Integration

### JSON Export Format
```python
# integration/json_exporter.py
class JSONExporter:
    def __init__(self, export_path="/data/exports/"):
        self.export_path = export_path
        
    def export_alerts(self, alerts, filename=None):
        """Export alerts to JSON file"""
        if not filename:
            filename = f"sentinair_alerts_{int(time.time())}.json"
            
        filepath = os.path.join(self.export_path, filename)
        
        export_data = {
            'export_time': time.time(),
            'export_source': 'Sentinair',
            'version': '1.0',
            'alert_count': len(alerts),
            'alerts': [self.format_alert(alert) for alert in alerts]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
            
        return filepath
        
    def format_alert(self, alert):
        """Format alert for JSON export"""
        return {
            'id': alert.id,
            'timestamp': alert.timestamp,
            'severity': alert.severity,
            'category': alert.category,
            'title': alert.title,
            'description': alert.description,
            'source': alert.source,
            'details': alert.details,
            'status': alert.status,
            'acknowledged_by': alert.acknowledged_by,
            'acknowledged_at': alert.acknowledged_at
        }
```

### CSV Export Format
```python
# integration/csv_exporter.py
import csv

class CSVExporter:
    def export_alerts(self, alerts, filename=None):
        """Export alerts to CSV file"""
        if not filename:
            filename = f"sentinair_alerts_{int(time.time())}.csv"
            
        filepath = os.path.join(self.export_path, filename)
        
        fieldnames = [
            'id', 'timestamp', 'severity', 'category', 'title', 
            'description', 'source', 'status', 'acknowledged_by'
        ]
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for alert in alerts:
                writer.writerow({
                    'id': alert.id,
                    'timestamp': alert.timestamp,
                    'severity': alert.severity,
                    'category': alert.category,
                    'title': alert.title,
                    'description': alert.description,
                    'source': alert.source,
                    'status': alert.status,
                    'acknowledged_by': alert.acknowledged_by or ''
                })
                
        return filepath
```

## 🗄️ Database Integration

### Shared Database Setup
```python
# integration/database_integration.py
import sqlite3
import threading

class SharedDatabaseIntegration:
    def __init__(self, db_path="/shared/sentinair_integration.db"):
        self.db_path = db_path
        self.init_database()
        self.lock = threading.Lock()
        
    def init_database(self):
        """Initialize shared database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_alerts (
                id TEXT PRIMARY KEY,
                timestamp REAL,
                severity TEXT,
                category TEXT,
                title TEXT,
                description TEXT,
                source TEXT,
                details TEXT,
                status TEXT,
                created_at REAL,
                updated_at REAL
            )
        ''')
        
        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_events (
                id TEXT PRIMARY KEY,
                timestamp REAL,
                event_type TEXT,
                source TEXT,
                data TEXT,
                processed BOOLEAN DEFAULT FALSE,
                created_at REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def insert_alert(self, alert):
        """Insert alert into shared database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO shared_alerts 
                (id, timestamp, severity, category, title, description, 
                 source, details, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.id, alert.timestamp, alert.severity, alert.category,
                alert.title, alert.description, alert.source, 
                json.dumps(alert.details), alert.status,
                time.time(), time.time()
            ))
            
            conn.commit()
            conn.close()
```

## 🔄 Message Queue Integration

### Local Message Broker
```python
# integration/message_queue.py
import queue
import threading
import json

class LocalMessageQueue:
    def __init__(self):
        self.queues = {}
        self.lock = threading.Lock()
        
    def create_queue(self, queue_name, maxsize=0):
        """Create a new message queue"""
        with self.lock:
            if queue_name not in self.queues:
                self.queues[queue_name] = queue.Queue(maxsize=maxsize)
                
    def publish(self, queue_name, message):
        """Publish message to queue"""
        if queue_name not in self.queues:
            self.create_queue(queue_name)
            
        try:
            self.queues[queue_name].put_nowait({
                'timestamp': time.time(),
                'data': message
            })
            return True
        except queue.Full:
            return False
            
    def subscribe(self, queue_name, timeout=None):
        """Subscribe to queue and get messages"""
        if queue_name not in self.queues:
            return None
            
        try:
            return self.queues[queue_name].get(timeout=timeout)
        except queue.Empty:
            return None

# Alert publisher
class AlertPublisher:
    def __init__(self):
        self.mq = LocalMessageQueue()
        self.mq.create_queue('alerts')
        
    def publish_alert(self, alert):
        """Publish alert to message queue"""
        message = {
            'type': 'alert',
            'alert_id': alert.id,
            'severity': alert.severity,
            'title': alert.title,
            'description': alert.description,
            'timestamp': alert.timestamp
        }
        
        return self.mq.publish('alerts', message)
```

## 🖥️ Dashboard Integration

### Grafana Integration (for environments with Grafana)
```python
# integration/grafana_integration.py
class GrafanaIntegration:
    def __init__(self, grafana_url, api_key):
        self.grafana_url = grafana_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
    def create_sentinair_dashboard(self):
        """Create Sentinair dashboard in Grafana"""
        dashboard_config = {
            "dashboard": {
                "title": "Sentinair Security Dashboard",
                "panels": [
                    {
                        "title": "Alert Severity Distribution",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "sentinair_alerts_by_severity",
                                "legendFormat": "{{severity}}"
                            }
                        ]
                    },
                    {
                        "title": "Alerts Over Time",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(sentinair_alerts_total[5m])",
                                "legendFormat": "Alert Rate"
                            }
                        ]
                    }
                ]
            }
        }
        
        response = requests.post(
            f"{self.grafana_url}/api/dashboards/db",
            headers=self.headers,
            json=dashboard_config
        )
        
        return response.status_code == 200
```

## 📋 Integration Checklist

### Pre-Integration Planning
- [ ] Define integration requirements
- [ ] Assess security implications
- [ ] Plan data flow and formats
- [ ] Design authentication mechanism
- [ ] Test in isolated environment

### API Integration
- [ ] Configure API endpoints
- [ ] Set up authentication
- [ ] Test API connectivity
- [ ] Implement rate limiting
- [ ] Document API usage

### File-Based Integration
- [ ] Define export formats
- [ ] Set up file locations
- [ ] Configure permissions
- [ ] Test file generation
- [ ] Implement error handling

### Database Integration
- [ ] Design database schema
- [ ] Set up access permissions
- [ ] Test database connectivity
- [ ] Implement data validation
- [ ] Plan data retention

### Monitoring Integration
- [ ] Configure log forwarding
- [ ] Set up monitoring dashboards
- [ ] Test alert delivery
- [ ] Validate data accuracy
- [ ] Monitor performance impact

## ⚠️ Security Considerations

### Air-Gap Compliance
- **No Internet Access**: Ensure no external connectivity
- **Local Authentication**: Use local authentication only
- **Data Validation**: Validate all external data
- **Access Control**: Implement strict access controls
- **Audit Logging**: Log all integration activities

### Integration Security
- **Encrypted Communication**: Use TLS for all API calls
- **API Key Management**: Secure API key storage and rotation
- **Input Validation**: Validate all incoming data
- **Output Sanitization**: Sanitize all outgoing data
- **Error Handling**: Secure error handling and logging

---

**Next Steps:**
- [Troubleshooting](13-troubleshooting.md) - Integration troubleshooting
- [API Reference](16-api-reference.md) - Complete API documentation
- [Security Best Practices](08-security.md) - Integration security guidelines
