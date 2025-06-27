"""
Alert management system for Sentinair
Handles creation, notification, and management of security alerts
"""

import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable, Optional
from collections import defaultdict, deque
import json

from utils.json_utils import sanitize_datetime_objects

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

class AlertManager:
    """Manages security alerts and notifications"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Alert configuration
        self.severity_threshold = config.get('detection.alert_severity_threshold', 'medium')
        self.max_alerts_per_hour = config.get('detection.max_alerts_per_hour', 10)
        
        # Alert storage
        self.active_alerts = []
        self.alert_history = deque(maxlen=1000)
        self.alert_lock = threading.RLock()
        
        # Rate limiting
        self.alert_timestamps = defaultdict(deque)
        
        # Notification callbacks
        self.notification_callbacks = []
        
        # Alert statistics
        self.alert_stats = {
            'total_alerts': 0,
            'alerts_by_severity': defaultdict(int),
            'alerts_by_type': defaultdict(int),
            'false_positives': 0
        }
        
    def create_alert(self, alert_data: Dict[str, Any]) -> int:
        """Create a new security alert"""
        try:
            # Generate unique alert ID
            alert_id = int(time.time() * 1000000)  # Microsecond timestamp
            
            # Get timestamp and convert to ISO format if it's a datetime
            timestamp = alert_data.get('timestamp', datetime.now())
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
            
            # Prepare alert with sanitized data
            alert = {
                'id': alert_id,
                'timestamp': timestamp,
                'event_type': alert_data.get('event_type', 'unknown'),
                'severity': alert_data.get('severity', 'medium'),
                'confidence': alert_data.get('confidence', 0.0),
                'description': alert_data.get('description', 'Anomaly detected'),
                'event_data': sanitize_datetime_objects(alert_data.get('event_data', {})),
                'acknowledged': False,
                'false_positive': False,
                'created_at': datetime.now().isoformat()
            }
            
            # Check if alert should be created based on severity threshold
            if not self._should_create_alert(alert):
                self.logger.debug(f"Alert filtered out: severity {alert['severity']} below threshold")
                return -1
                
            # Rate limiting check
            if not self._check_rate_limit(alert):
                self.logger.warning("Alert rate limit exceeded, suppressing alert")
                return -1
                
            with self.alert_lock:
                # Add to active alerts
                self.active_alerts.append(alert)
                
                # Add to history
                self.alert_history.append(alert.copy())
                
                # Update statistics
                self._update_statistics(alert)
                
            # Send notifications
            self._send_notifications(alert)
            
            # Log the alert
            self._log_alert(alert)
            
            self.logger.info(f"Alert created: {alert['id']} - {alert['description']}")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            return -1
            
    def _should_create_alert(self, alert: Dict[str, Any]) -> bool:
        """Check if alert should be created based on severity threshold"""
        severity_levels = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        alert_level = severity_levels.get(alert['severity'], 1)
        threshold_level = severity_levels.get(self.severity_threshold, 2)
        
        return alert_level >= threshold_level
        
    def _check_rate_limit(self, alert: Dict[str, Any]) -> bool:
        """Check if alert creation is within rate limits"""
        current_time = datetime.now()
        alert_type = alert['event_type']
        
        # Clean old timestamps (older than 1 hour)
        hour_ago = current_time - timedelta(hours=1)
        while (self.alert_timestamps[alert_type] and 
               self.alert_timestamps[alert_type][0] < hour_ago):
            self.alert_timestamps[alert_type].popleft()
            
        # Check if we're under the limit
        if len(self.alert_timestamps[alert_type]) >= self.max_alerts_per_hour:
            return False
            
        # Add current timestamp
        self.alert_timestamps[alert_type].append(current_time)
        return True
        
    def _update_statistics(self, alert: Dict[str, Any]):
        """Update alert statistics"""
        self.alert_stats['total_alerts'] += 1
        self.alert_stats['alerts_by_severity'][alert['severity']] += 1
        self.alert_stats['alerts_by_type'][alert['event_type']] += 1
        
    def _send_notifications(self, alert: Dict[str, Any]):
        """Send notifications for the alert"""
        try:
            # Desktop notification
            if PLYER_AVAILABLE:
                self._send_desktop_notification(alert)
                
            # Custom notification callbacks
            for callback in self.notification_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in notification callback: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")
            
    def _send_desktop_notification(self, alert: Dict[str, Any]):
        """Send desktop notification"""
        try:
            title = f"Sentinair Alert - {alert['severity'].upper()}"
            message = alert['description']
            
            # Limit message length
            if len(message) > 100:
                message = message[:97] + "..."
                
            notification.notify(
                title=title,
                message=message,
                timeout=10
            )
            
        except Exception as e:
            self.logger.debug(f"Desktop notification failed: {e}")
            
    def _log_alert(self, alert: Dict[str, Any]):
        """Log alert to security audit log"""
        try:
            from utils.logger import SecurityAuditLogger
            
            audit_logger = SecurityAuditLogger()
            audit_logger.log_anomaly_detection(
                confidence=alert['confidence'],
                event_data={
                    'alert_id': alert['id'],
                    'event_type': alert['event_type'],
                    'severity': alert['severity'],
                    'description': alert['description']
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error logging alert: {e}")
            
    def acknowledge_alert(self, alert_id: int, acknowledged_by: str = "user") -> bool:
        """Acknowledge an alert"""
        try:
            with self.alert_lock:
                for alert in self.active_alerts:
                    if alert['id'] == alert_id:
                        alert['acknowledged'] = True
                        alert['acknowledged_at'] = datetime.now().isoformat()
                        alert['acknowledged_by'] = acknowledged_by
                        
                        self.logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
                        return True
                        
            self.logger.warning(f"Alert not found for acknowledgment: {alert_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
            return False
            
    def mark_false_positive(self, alert_id: int, marked_by: str = "user") -> bool:
        """Mark an alert as false positive"""
        try:
            with self.alert_lock:
                for alert in self.active_alerts:
                    if alert['id'] == alert_id:
                        alert['false_positive'] = True
                        alert['acknowledged'] = True
                        alert['acknowledged_at'] = datetime.now().isoformat()
                        alert['acknowledged_by'] = marked_by
                        
                        # Update statistics
                        self.alert_stats['false_positives'] += 1
                        
                        self.logger.info(f"Alert marked as false positive: {alert_id} by {marked_by}")
                        return True
                        
            self.logger.warning(f"Alert not found for false positive marking: {alert_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error marking false positive: {e}")
            return False
            
    def get_active_alerts(self, severity_filter: str = None) -> List[Dict[str, Any]]:
        """Get list of active (unacknowledged) alerts"""
        try:
            with self.alert_lock:
                alerts = [alert for alert in self.active_alerts if not alert['acknowledged']]
                
                if severity_filter:
                    alerts = [alert for alert in alerts if alert['severity'] == severity_filter]
                    
                # Sort by timestamp (newest first)
                alerts.sort(key=lambda x: x['timestamp'], reverse=True)
                
                return alerts
                
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
            
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts within specified time window"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with self.alert_lock:
                recent_alerts = [
                    alert for alert in self.alert_history
                    if alert['timestamp'] >= cutoff_time
                ]
                
                # Sort by timestamp (newest first)
                recent_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
                
                return recent_alerts
                
        except Exception as e:
            self.logger.error(f"Error getting recent alerts: {e}")
            return []
            
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        try:
            with self.alert_lock:
                stats = self.alert_stats.copy()
                
                # Add additional statistics
                stats['active_alerts'] = len([a for a in self.active_alerts if not a['acknowledged']])
                stats['total_active'] = len(self.active_alerts)
                
                # Recent activity (last 24 hours)
                recent_alerts = self.get_recent_alerts(24)
                stats['alerts_last_24h'] = len(recent_alerts)
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error getting alert statistics: {e}")
            return {}
            
    def cleanup_old_alerts(self, days: int = 7) -> int:
        """Clean up old acknowledged alerts"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            with self.alert_lock:
                original_count = len(self.active_alerts)
                
                # Keep only recent alerts or unacknowledged alerts
                self.active_alerts = [
                    alert for alert in self.active_alerts
                    if (not alert['acknowledged'] or 
                        alert.get('acknowledged_at', alert['timestamp']) >= cutoff_time)
                ]
                
                cleaned_count = original_count - len(self.active_alerts)
                
                if cleaned_count > 0:
                    self.logger.info(f"Cleaned up {cleaned_count} old alerts")
                    
                return cleaned_count
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old alerts: {e}")
            return 0
            
    def add_notification_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a custom notification callback"""
        self.notification_callbacks.append(callback)
        
    def remove_notification_callback(self, callback: Callable):
        """Remove a notification callback"""
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)
            
    def export_alerts(self, file_path: str, hours: int = 24) -> bool:
        """Export recent alerts to JSON file"""
        try:
            alerts = self.get_recent_alerts(hours)
            
            # Convert datetime objects to strings for JSON serialization
            exportable_alerts = []
            for alert in alerts:
                exportable_alert = alert.copy()
                for key, value in exportable_alert.items():
                    if isinstance(value, datetime):
                        exportable_alert[key] = value.isoformat()
                exportable_alerts.append(exportable_alert)
                
            with open(file_path, 'w') as f:
                json.dump(exportable_alerts, f, indent=2)
                
            self.logger.info(f"Exported {len(alerts)} alerts to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting alerts: {e}")
            return False
            
    def get_alert_by_id(self, alert_id: int) -> Optional[Dict[str, Any]]:
        """Get specific alert by ID"""
        try:
            with self.alert_lock:
                for alert in self.active_alerts:
                    if alert['id'] == alert_id:
                        return alert.copy()
                        
                # Check history if not in active alerts
                for alert in self.alert_history:
                    if alert['id'] == alert_id:
                        return alert.copy()
                        
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting alert by ID: {e}")
            return None
