# API Reference Guide

This comprehensive reference covers the complete Sentinair API, including REST endpoints, Python SDK, authentication, and integration examples.

## 🌐 API Overview

### API Architecture
Sentinair provides a comprehensive REST API for programmatic access to all system functions. The API is designed for air-gapped environments and supports local-only access.

### Base URL
```
https://localhost:8888/api/v1
```

### Authentication
All API endpoints require authentication via API keys:
```http
Authorization: Bearer YOUR_API_KEY
```

### Response Format
All responses are in JSON format:
```json
{
  "status": "success|error",
  "data": {...},
  "message": "Optional message",
  "timestamp": 1640995200
}
```

## 🔐 Authentication

### API Key Management

#### Generate API Key
```bash
# Generate new API key
python main.py --generate-api-key --name "SIEM_Integration" --permissions "read_alerts,read_events"

# Generate admin API key
python main.py --generate-api-key --name "Admin_Console" --permissions "all" --admin
```

#### API Key Permissions
```yaml
# Available permissions
permissions:
  read_only:
    - "read_alerts"
    - "read_events" 
    - "read_status"
    - "read_config"
    
  standard:
    - "read_alerts"
    - "read_events"
    - "acknowledge_alerts"
    - "generate_reports"
    
  admin:
    - "all"  # Full access to all endpoints
```

### Authentication Examples

#### Python
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

response = requests.get('https://localhost:8888/api/v1/status', headers=headers)
```

#### cURL
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://localhost:8888/api/v1/status
```

#### PowerShell
```powershell
$headers = @{
    'Authorization' = 'Bearer YOUR_API_KEY'
    'Content-Type' = 'application/json'
}

Invoke-RestMethod -Uri 'https://localhost:8888/api/v1/status' -Headers $headers
```

## 📊 Alert Management API

### Get Alerts

#### Endpoint
```http
GET /api/v1/alerts
```

#### Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `severity` | string | Filter by severity | `critical`, `high`, `medium`, `low` |
| `status` | string | Filter by status | `open`, `acknowledged`, `closed` |
| `category` | string | Filter by category | `malware`, `persistence`, `exfiltration` |
| `start_time` | timestamp | Start time filter | `1640995200` |
| `end_time` | timestamp | End time filter | `1641081600` |
| `limit` | integer | Limit results | `100` (max: 1000) |
| `offset` | integer | Pagination offset | `0` |
| `sort_by` | string | Sort field | `timestamp`, `severity`, `title` |
| `sort_order` | string | Sort direction | `asc`, `desc` |

#### Example Request
```http
GET /api/v1/alerts?severity=critical&status=open&limit=50&sort_by=timestamp&sort_order=desc
```

#### Example Response
```json
{
  "status": "success",
  "data": {
    "alerts": [
      {
        "id": "alert_001",
        "timestamp": 1640995200,
        "severity": "critical",
        "category": "malware",
        "title": "Malicious file detected",
        "description": "Suspicious executable found in Downloads folder",
        "source": "file_monitor",
        "details": {
          "file_path": "/home/user/Downloads/suspicious.exe",
          "file_hash": "abc123...",
          "rule_matched": "malware_detection"
        },
        "status": "open",
        "created_at": 1640995200,
        "updated_at": 1640995200,
        "acknowledged_by": null,
        "acknowledged_at": null
      }
    ],
    "total_count": 1,
    "page_count": 1,
    "current_page": 1
  },
  "timestamp": 1640995800
}
```

### Get Single Alert

#### Endpoint
```http
GET /api/v1/alerts/{alert_id}
```

#### Example Response
```json
{
  "status": "success",
  "data": {
    "id": "alert_001",
    "timestamp": 1640995200,
    "severity": "critical",
    "category": "malware",
    "title": "Malicious file detected",
    "description": "Suspicious executable found in Downloads folder",
    "source": "file_monitor",
    "details": {
      "file_path": "/home/user/Downloads/suspicious.exe",
      "file_hash": "abc123def456",
      "file_size": 1024000,
      "rule_matched": "malware_detection",
      "confidence": 0.95
    },
    "status": "open",
    "created_at": 1640995200,
    "updated_at": 1640995200,
    "acknowledged_by": null,
    "acknowledged_at": null,
    "related_events": ["event_001", "event_002"]
  }
}
```

### Acknowledge Alert

#### Endpoint
```http
POST /api/v1/alerts/{alert_id}/acknowledge
```

#### Request Body
```json
{
  "user": "security_analyst",
  "comment": "False positive - approved software installation"
}
```

#### Example Response
```json
{
  "status": "success",
  "data": {
    "alert_id": "alert_001",
    "acknowledged": true,
    "acknowledged_by": "security_analyst",
    "acknowledged_at": 1640995800,
    "comment": "False positive - approved software installation"
  }
}
```

### Bulk Alert Operations

#### Bulk Acknowledge
```http
POST /api/v1/alerts/bulk/acknowledge
```

#### Request Body
```json
{
  "alert_ids": ["alert_001", "alert_002", "alert_003"],
  "user": "security_analyst",
  "comment": "Bulk acknowledgment - approved maintenance"
}
```

#### Bulk Update Status
```http
POST /api/v1/alerts/bulk/update_status
```

#### Request Body
```json
{
  "alert_ids": ["alert_001", "alert_002"],
  "status": "closed",
  "user": "security_analyst",
  "comment": "Investigation complete"
}
```

## 📈 Events API

### Get Events

#### Endpoint
```http
GET /api/v1/events
```

#### Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `event_type` | string | Filter by event type |
| `source` | string | Filter by source |
| `start_time` | timestamp | Start time filter |
| `end_time` | timestamp | End time filter |
| `limit` | integer | Limit results |
| `offset` | integer | Pagination offset |

#### Example Response
```json
{
  "status": "success",
  "data": {
    "events": [
      {
        "id": "event_001",
        "timestamp": 1640995200,
        "type": "file_created",
        "source": "file_monitor",
        "data": {
          "path": "/home/user/document.txt",
          "size": 1024,
          "permissions": "644"
        },
        "processed": true,
        "alerts_generated": 0
      }
    ],
    "total_count": 1000,
    "page_count": 10,
    "current_page": 1
  }
}
```

### Create Event

#### Endpoint
```http
POST /api/v1/events
```

#### Request Body
```json
{
  "type": "custom_event",
  "source": "external_system",
  "data": {
    "custom_field": "custom_value",
    "severity": "medium"
  }
}
```

## 🖥️ System Status API

### Get System Status

#### Endpoint
```http
GET /api/v1/status
```

#### Example Response
```json
{
  "status": "success",
  "data": {
    "system": {
      "running": true,
      "uptime": 86400,
      "version": "1.0.0",
      "mode": "production"
    },
    "monitoring": {
      "file_monitor": {
        "active": true,
        "events_processed": 10000,
        "last_activity": 1640995200
      },
      "usb_monitor": {
        "active": true,
        "events_processed": 50,
        "last_activity": 1640995100
      },
      "process_monitor": {
        "active": true,
        "events_processed": 5000,
        "last_activity": 1640995200
      },
      "behavior_monitor": {
        "active": true,
        "events_processed": 2000,
        "last_activity": 1640995150
      }
    },
    "performance": {
      "cpu_usage": 15.5,
      "memory_usage": 25.3,
      "disk_usage": 45.2
    },
    "alerts": {
      "total_today": 5,
      "critical_open": 1,
      "high_open": 2,
      "last_alert": 1640995000
    },
    "ml_model": {
      "last_training": 1640908800,
      "accuracy": 0.95,
      "predictions_today": 1000
    }
  }
}
```

### Get Health Status

#### Endpoint
```http
GET /api/v1/health
```

#### Example Response
```json
{
  "status": "success",
  "data": {
    "overall_health": "healthy",
    "checks": {
      "database": {
        "status": "ok",
        "response_time": 50,
        "last_check": 1640995200
      },
      "file_system": {
        "status": "ok",
        "disk_space": "55% used",
        "last_check": 1640995200
      },
      "services": {
        "status": "ok",
        "all_monitors_active": true,
        "last_check": 1640995200
      }
    },
    "uptime": 86400,
    "last_restart": 1640908800
  }
}
```

## ⚙️ Configuration API

### Get Configuration

#### Endpoint
```http
GET /api/v1/config
```

#### Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `section` | string | Specific config section |
| `key` | string | Specific config key |

#### Example Response
```json
{
  "status": "success",
  "data": {
    "monitoring": {
      "file_monitor": {
        "enabled": true,
        "watch_directories": ["/home", "/etc", "/usr/bin"],
        "excluded_extensions": [".tmp", ".log"]
      },
      "usb_monitor": {
        "enabled": true,
        "alert_on_insertion": true,
        "whitelist_enabled": false
      }
    },
    "alerts": {
      "severity_thresholds": {
        "file_access_rate": 100,
        "usb_insertion_count": 5
      }
    },
    "ml": {
      "training_interval": 86400,
      "anomaly_threshold": 0.8
    }
  }
}
```

### Update Configuration

#### Endpoint
```http
PUT /api/v1/config
```

#### Request Body
```json
{
  "monitoring": {
    "file_monitor": {
      "watch_directories": ["/home", "/etc", "/usr/bin", "/opt"]
    }
  },
  "alerts": {
    "severity_thresholds": {
      "file_access_rate": 150
    }
  }
}
```

### Update Single Configuration Value

#### Endpoint
```http
PATCH /api/v1/config/{section}/{key}
```

#### Request Body
```json
{
  "value": 200
}
```

## 📄 Reports API

### Generate Report

#### Endpoint
```http
POST /api/v1/reports
```

#### Request Body
```json
{
  "type": "alert_summary",
  "format": "pdf",
  "parameters": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "include_charts": true,
    "severity_filter": ["critical", "high"]
  }
}
```

#### Example Response
```json
{
  "status": "success",
  "data": {
    "report_id": "report_001",
    "status": "generating",
    "estimated_completion": 1640995800,
    "download_url": "/api/v1/reports/report_001/download"
  }
}
```

### Get Report Status

#### Endpoint
```http
GET /api/v1/reports/{report_id}
```

#### Example Response
```json
{
  "status": "success",
  "data": {
    "report_id": "report_001",
    "status": "completed",
    "format": "pdf",
    "file_size": 2048000,
    "created_at": 1640995200,
    "completed_at": 1640995800,
    "download_url": "/api/v1/reports/report_001/download",
    "expires_at": 1641081600
  }
}
```

### Download Report

#### Endpoint
```http
GET /api/v1/reports/{report_id}/download
```

Returns the report file as binary content.

## 🤖 Machine Learning API

### Get ML Model Status

#### Endpoint
```http
GET /api/v1/ml/status
```

#### Example Response
```json
{
  "status": "success",
  "data": {
    "models": {
      "anomaly_detector": {
        "status": "active",
        "last_training": 1640995200,
        "training_data_size": 10000,
        "accuracy": 0.95,
        "version": "1.2.0"
      },
      "behavior_analyzer": {
        "status": "active", 
        "last_training": 1640995000,
        "training_data_size": 5000,
        "accuracy": 0.92,
        "version": "1.1.0"
      }
    },
    "predictions_today": 1500,
    "anomalies_detected": 25,
    "confidence_threshold": 0.8
  }
}
```

### Trigger ML Training

#### Endpoint
```http
POST /api/v1/ml/train
```

#### Request Body
```json
{
  "model": "anomaly_detector",
  "training_data_days": 30,
  "force_retrain": false
}
```

### Get ML Predictions

#### Endpoint
```http
GET /api/v1/ml/predictions
```

#### Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `start_time` | timestamp | Start time filter |
| `end_time` | timestamp | End time filter |
| `confidence_min` | float | Minimum confidence |
| `anomaly_only` | boolean | Only anomalous predictions |

## 🛠️ Rules Management API

### Get Rules

#### Endpoint
```http
GET /api/v1/rules
```

#### Example Response
```json
{
  "status": "success",
  "data": {
    "rules": [
      {
        "id": "rule_001",
        "name": "Malware Detection",
        "type": "yara",
        "enabled": true,
        "category": "malware",
        "severity": "critical",
        "description": "Detects known malware signatures",
        "created_at": 1640995200,
        "updated_at": 1640995200,
        "match_count": 15
      }
    ],
    "total_count": 50,
    "enabled_count": 48
  }
}
```

### Create Rule

#### Endpoint
```http
POST /api/v1/rules
```

#### Request Body
```json
{
  "name": "Custom Malware Rule",
  "type": "yara",
  "category": "malware",
  "severity": "high",
  "description": "Custom rule for detecting specific malware",
  "rule_content": "rule CustomMalware { ... }",
  "enabled": true
}
```

### Update Rule

#### Endpoint
```http
PUT /api/v1/rules/{rule_id}
```

### Delete Rule

#### Endpoint
```http
DELETE /api/v1/rules/{rule_id}
```

## 🐍 Python SDK

### Installation
```bash
pip install sentinair-sdk
```

### Basic Usage
```python
from sentinair_sdk import SentinairClient

# Initialize client
client = SentinairClient(
    base_url='https://localhost:8888',
    api_key='your_api_key'
)

# Get alerts
alerts = client.alerts.get_all(severity='critical', limit=10)

# Acknowledge alert
client.alerts.acknowledge('alert_001', user='analyst', comment='Investigated')

# Get system status
status = client.system.get_status()

# Generate report
report = client.reports.generate(
    type='alert_summary',
    format='pdf',
    start_date='2024-01-01',
    end_date='2024-01-31'
)
```

### Advanced Usage
```python
# Alert management
class AlertManager:
    def __init__(self, client):
        self.client = client
        
    def handle_critical_alerts(self):
        """Process all critical alerts"""
        alerts = self.client.alerts.get_all(
            severity='critical',
            status='open'
        )
        
        for alert in alerts:
            # Analyze alert
            if self.is_false_positive(alert):
                self.client.alerts.acknowledge(
                    alert['id'],
                    user='auto_handler',
                    comment='Automatic false positive detection'
                )
            else:
                # Escalate to security team
                self.escalate_alert(alert)
                
    def get_alert_trends(self, days=30):
        """Get alert trends over time"""
        end_time = time.time()
        start_time = end_time - (days * 24 * 3600)
        
        alerts = self.client.alerts.get_all(
            start_time=start_time,
            end_time=end_time
        )
        
        # Analyze trends
        trends = self.analyze_alert_patterns(alerts)
        return trends

# System monitoring
class SystemMonitor:
    def __init__(self, client):
        self.client = client
        
    def monitor_health(self):
        """Continuous health monitoring"""
        while True:
            status = self.client.system.get_status()
            health = self.client.system.get_health()
            
            if health['overall_health'] != 'healthy':
                self.handle_health_issue(health)
                
            time.sleep(300)  # Check every 5 minutes
            
    def get_performance_metrics(self):
        """Get detailed performance metrics"""
        status = self.client.system.get_status()
        
        return {
            'cpu_usage': status['performance']['cpu_usage'],
            'memory_usage': status['performance']['memory_usage'],
            'alert_rate': self.calculate_alert_rate(),
            'processing_speed': self.calculate_processing_speed()
        }
```

## 📝 Webhook Integration

### Register Webhook

#### Endpoint
```http
POST /api/v1/webhooks
```

#### Request Body
```json
{
  "url": "https://your-system.local/webhook",
  "events": ["alert.created", "alert.acknowledged", "system.health_change"],
  "secret": "webhook_secret_key",
  "active": true
}
```

### Webhook Payload Example
```json
{
  "event": "alert.created",
  "timestamp": 1640995200,
  "data": {
    "alert": {
      "id": "alert_001",
      "severity": "critical",
      "title": "Malicious file detected",
      "description": "Suspicious executable found",
      "timestamp": 1640995200
    }
  },
  "signature": "sha256=abc123..."
}
```

## 📋 API Best Practices

### Rate Limiting
- **Default Limits**: 100 requests per minute per API key
- **Burst Handling**: Up to 10 requests in 1 second burst
- **Response Headers**: Include rate limit headers

### Error Handling
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid severity level specified",
    "details": {
      "parameter": "severity",
      "valid_values": ["low", "medium", "high", "critical"]
    }
  },
  "timestamp": 1640995200
}
```

### Common Error Codes
| Code | Description |
|------|-------------|
| `AUTHENTICATION_REQUIRED` | API key required |
| `INVALID_API_KEY` | Invalid or expired API key |
| `INSUFFICIENT_PERMISSIONS` | API key lacks required permissions |
| `INVALID_PARAMETER` | Invalid parameter value |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |

### Security Considerations
- **HTTPS Only**: All API calls must use HTTPS
- **API Key Rotation**: Rotate API keys regularly
- **IP Restrictions**: Restrict API access by IP (optional)
- **Audit Logging**: All API calls are logged
- **Input Validation**: All inputs are validated and sanitized

---

**Next Steps:**
- [Configuration Reference](17-config-reference.md) - Complete configuration options
- [Integration Guide](12-integration.md) - API integration examples
- [Security Best Practices](08-security.md) - API security guidelines
