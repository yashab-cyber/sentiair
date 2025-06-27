"""
Database management for Sentinair
Handles SQLite database operations for event storage and retrieval
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import threading

class DatabaseManager:
    """Database manager for Sentinair events and data"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.db_path = config.get_database_path()
        self.lock = threading.RLock()  # Reentrant lock for thread safety
        
        # Initialize database
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize database with required tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create tables if they don't exist
                self._create_tables(cursor)
                
                # Create indexes for better performance
                self._create_indexes(cursor)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
            
    def _create_tables(self, cursor):
        """Create database tables"""
        
        # System events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                event_data TEXT,
                risk_score REAL DEFAULT 0.0,
                is_anomaly BOOLEAN DEFAULT 0,
                acknowledged BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # File access events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT NOT NULL,
                access_type TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                file_extension TEXT,
                process_name TEXT,
                process_pid INTEGER,
                user_name TEXT,
                is_suspicious BOOLEAN DEFAULT 0
            )
        ''')
        
        # USB events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usb_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                device_path TEXT,
                device_name TEXT,
                vendor_id TEXT,
                product_id TEXT,
                mount_point TEXT,
                file_system TEXT,
                total_bytes INTEGER DEFAULT 0,
                is_suspicious BOOLEAN DEFAULT 0
            )
        ''')
        
        # Application launches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_launches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                app_name TEXT NOT NULL,
                app_path TEXT,
                process_id INTEGER,
                parent_pid INTEGER,
                command_line TEXT,
                username TEXT,
                memory_usage INTEGER DEFAULT 0,
                is_suspicious BOOLEAN DEFAULT 0
            )
        ''')
        
        # User behavior events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_behavior (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                behavior_type TEXT NOT NULL,
                duration_seconds INTEGER DEFAULT 0,
                keystroke_count INTEGER DEFAULT 0,
                mouse_events INTEGER DEFAULT 0,
                activity_level TEXT DEFAULT 'normal',
                patterns_data TEXT
            )
        ''')
        
        # Anomaly alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomaly_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                event_id INTEGER,
                description TEXT,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_at DATETIME,
                acknowledged_by TEXT,
                false_positive BOOLEAN DEFAULT 0
            )
        ''')
        
        # System configuration and state
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
    def _create_indexes(self, cursor):
        """Create database indexes for better performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_system_events_anomaly ON system_events(is_anomaly)",
            "CREATE INDEX IF NOT EXISTS idx_file_access_timestamp ON file_access(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_file_access_path ON file_access(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_usb_events_timestamp ON usb_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_app_launches_timestamp ON application_launches(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_user_behavior_timestamp ON user_behavior(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_anomaly_alerts_timestamp ON anomaly_alerts(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_anomaly_alerts_severity ON anomaly_alerts(severity)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                self.logger.debug(f"Index creation warning: {e}")
                
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            with self.lock:
                conn = sqlite3.connect(
                    self.db_path,
                    timeout=30.0,
                    check_same_thread=False
                )
                conn.row_factory = sqlite3.Row  # Enable column access by name
                yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                
    def insert_event(self, event_data: Dict[str, Any]) -> int:
        """Insert a system event into the database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO system_events 
                    (timestamp, event_type, event_data, risk_score, is_anomaly)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    event_data.get('timestamp', datetime.now()),
                    event_data['event_type'],
                    event_data.get('event_data', ''),
                    event_data.get('risk_score', 0.0),
                    event_data.get('is_anomaly', False)
                ))
                
                event_id = cursor.lastrowid
                conn.commit()
                
                return event_id
                
        except Exception as e:
            self.logger.error(f"Error inserting event: {e}")
            return -1
            
    def insert_file_access(self, file_data: Dict[str, Any]) -> int:
        """Insert file access event"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO file_access 
                    (timestamp, file_path, access_type, file_size, file_extension, 
                     process_name, process_pid, user_name, is_suspicious)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_data.get('timestamp', datetime.now()),
                    file_data['file_path'],
                    file_data['access_type'],
                    file_data.get('file_size', 0),
                    file_data.get('file_extension', ''),
                    file_data.get('process_name', ''),
                    file_data.get('process_pid', 0),
                    file_data.get('user_name', ''),
                    file_data.get('is_suspicious', False)
                ))
                
                file_id = cursor.lastrowid
                conn.commit()
                
                return file_id
                
        except Exception as e:
            self.logger.error(f"Error inserting file access: {e}")
            return -1
            
    def insert_usb_event(self, usb_data: Dict[str, Any]) -> int:
        """Insert USB event"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO usb_events 
                    (timestamp, event_type, device_path, device_name, vendor_id, 
                     product_id, mount_point, file_system, total_bytes, is_suspicious)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    usb_data.get('timestamp', datetime.now()),
                    usb_data['event_type'],
                    usb_data.get('device_path', ''),
                    usb_data.get('device_name', ''),
                    usb_data.get('vendor_id', ''),
                    usb_data.get('product_id', ''),
                    usb_data.get('mount_point', ''),
                    usb_data.get('file_system', ''),
                    usb_data.get('total_bytes', 0),
                    usb_data.get('is_suspicious', False)
                ))
                
                usb_id = cursor.lastrowid
                conn.commit()
                
                return usb_id
                
        except Exception as e:
            self.logger.error(f"Error inserting USB event: {e}")
            return -1
            
    def insert_alert(self, alert_data: Dict[str, Any]) -> int:
        """Insert anomaly alert"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO anomaly_alerts 
                    (timestamp, alert_type, severity, confidence_score, 
                     event_id, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    alert_data.get('timestamp', datetime.now()),
                    alert_data['alert_type'],
                    alert_data['severity'],
                    alert_data['confidence_score'],
                    alert_data.get('event_id'),
                    alert_data.get('description', '')
                ))
                
                alert_id = cursor.lastrowid
                conn.commit()
                
                return alert_id
                
        except Exception as e:
            self.logger.error(f"Error inserting alert: {e}")
            return -1
            
    def get_recent_events(self, days: int = 7, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get recent events for training"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                since_date = datetime.now() - timedelta(days=days)
                
                cursor.execute('''
                    SELECT timestamp, event_type, event_data, risk_score, is_anomaly
                    FROM system_events 
                    WHERE timestamp >= ? AND event_data IS NOT NULL AND event_data != ''
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (since_date, limit))
                
                events = []
                for row in cursor.fetchall():
                    try:
                        event = dict(row)
                        # Parse JSON event_data if it's a string
                        if isinstance(event['event_data'], str) and event['event_data'].strip():
                            event['event_data'] = json.loads(event['event_data'])
                        elif not event['event_data']:
                            # Skip events with empty event_data
                            continue
                        events.append(event)
                    except json.JSONDecodeError as je:
                        self.logger.warning(f"Skipping event with invalid JSON: {je}")
                        continue
                    except Exception as ee:
                        self.logger.warning(f"Skipping problematic event: {ee}")
                        continue
                
                return events
                
        except Exception as e:
            self.logger.error(f"Error getting recent events: {e}")
            return []
            
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                since_time = datetime.now() - timedelta(hours=hours)
                
                cursor.execute('''
                    SELECT * FROM anomaly_alerts 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (since_time,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Error getting recent alerts: {e}")
            return []
            
    def acknowledge_alert(self, alert_id: int, acknowledged_by: str = "system") -> bool:
        """Acknowledge an alert"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE anomaly_alerts 
                    SET acknowledged = 1, acknowledged_at = ?, acknowledged_by = ?
                    WHERE id = ?
                ''', (datetime.now(), acknowledged_by, alert_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
            return False
            
    def mark_false_positive(self, alert_id: int) -> bool:
        """Mark alert as false positive"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE anomaly_alerts 
                    SET false_positive = 1, acknowledged = 1, acknowledged_at = ?
                    WHERE id = ?
                ''', (datetime.now(), alert_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Error marking false positive: {e}")
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count events by type
                cursor.execute('''
                    SELECT event_type, COUNT(*) as count 
                    FROM system_events 
                    GROUP BY event_type
                ''')
                stats['events_by_type'] = dict(cursor.fetchall())
                
                # Count recent anomalies
                cursor.execute('''
                    SELECT COUNT(*) as count 
                    FROM system_events 
                    WHERE is_anomaly = 1 AND timestamp >= ?
                ''', (datetime.now() - timedelta(days=1),))
                stats['recent_anomalies'] = cursor.fetchone()[0]
                
                # Count alerts by severity
                cursor.execute('''
                    SELECT severity, COUNT(*) as count 
                    FROM anomaly_alerts 
                    WHERE timestamp >= ?
                    GROUP BY severity
                ''', (datetime.now() - timedelta(days=7),))
                stats['alerts_by_severity'] = dict(cursor.fetchall())
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
            
    def cleanup_old_data(self, retention_days: int = 30) -> bool:
        """Clean up old data based on retention policy"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                
                # Clean up old events
                cursor.execute('''
                    DELETE FROM system_events 
                    WHERE timestamp < ? AND acknowledged = 1
                ''', (cutoff_date,))
                
                deleted_events = cursor.rowcount
                
                # Clean up old file access records
                cursor.execute('''
                    DELETE FROM file_access 
                    WHERE timestamp < ?
                ''', (cutoff_date,))
                
                deleted_files = cursor.rowcount
                
                conn.commit()
                
                self.logger.info(f"Cleaned up {deleted_events} events and {deleted_files} file records")
                return True
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
            return False
