"""
Core detection engine for Sentinair
Handles behavioral monitoring and anomaly detection
"""

import time
import threading
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from utils.json_utils import safe_json_dumps, sanitize_datetime_objects

from core.monitors.file_monitor import FileAccessMonitor
from core.monitors.usb_monitor import USBMonitor
from core.monitors.process_monitor import ProcessMonitor
from core.monitors.behavior_monitor import BehaviorMonitor
from ml.anomaly_detector import AnomalyDetector
from alerts.alert_manager import AlertManager
from utils.database import DatabaseManager
from utils.encryption import DataEncryption

@dataclass
class DetectionEvent:
    """Represents a detection event"""
    timestamp: datetime
    event_type: str
    data: Dict[str, Any]
    risk_score: float = 0.0
    is_anomaly: bool = False

class SentinairEngine:
    """Main detection engine for Sentinair"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.stealth_mode = False
        
        # Initialize components
        self.db_manager = DatabaseManager(config)
        self.encryption = DataEncryption(config)
        self.anomaly_detector = AnomalyDetector(config)
        self.alert_manager = AlertManager(config)
        
        # Initialize monitors
        self.monitors = {}
        if config.get('detection', {}).get('track_file_access', True):
            self.monitors['file'] = FileAccessMonitor(config)
            
        if config.get('detection', {}).get('track_usb_events', True):
            self.monitors['usb'] = USBMonitor(config)
            
        if config.get('detection', {}).get('track_app_launches', True):
            self.monitors['process'] = ProcessMonitor(config)
            
        if config.get('detection', {}).get('track_user_behavior', True):
            self.monitors['behavior'] = BehaviorMonitor(config)
        
        # Event queue for processing
        self.event_queue = []
        self.queue_lock = threading.Lock()
        
        # Training thread
        self.training_thread = None
        self.last_training_time = None
        
    def start(self):
        """Start the detection engine"""
        if self.running:
            self.logger.warning("Engine is already running")
            return
            
        self.logger.info("Starting Sentinair detection engine")
        self.running = True
        
        # Start all monitors
        for name, monitor in self.monitors.items():
            try:
                monitor.start()
                monitor.set_callback(self._on_event)
                self.logger.info(f"Started {name} monitor")
            except Exception as e:
                self.logger.error(f"Failed to start {name} monitor: {e}")
        
        # Start event processing thread
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
        
        # Start periodic training
        self.training_thread = threading.Thread(target=self._periodic_training, daemon=True)
        self.training_thread.start()
        
        # Load existing model if available
        try:
            self.anomaly_detector.load_model()
            self.logger.info("Loaded existing anomaly detection model")
        except Exception as e:
            self.logger.info(f"No existing model found, will train new one: {e}")
            
    def stop(self):
        """Stop the detection engine"""
        if not self.running:
            return
            
        self.logger.info("Stopping Sentinair detection engine")
        self.running = False
        
        # Stop all monitors
        for name, monitor in self.monitors.items():
            try:
                monitor.stop()
                self.logger.info(f"Stopped {name} monitor")
            except Exception as e:
                self.logger.error(f"Error stopping {name} monitor: {e}")
        
        # Wait for processing thread to finish
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join(timeout=5)
            
    def run_stealth_mode(self):
        """Run in stealth mode (background)"""
        self.stealth_mode = True
        self.logger.info("Running in stealth mode")
        
        self.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Stealth mode interrupted")
        finally:
            self.stop()
            
    def _on_event(self, event_type: str, event_data: Dict[str, Any]):
        """Handle events from monitors"""
        event = DetectionEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            data=event_data
        )
        
        with self.queue_lock:
            self.event_queue.append(event)
            
    def _process_events(self):
        """Process events from the queue"""
        while self.running:
            events_to_process = []
            
            with self.queue_lock:
                if self.event_queue:
                    events_to_process = self.event_queue.copy()
                    self.event_queue.clear()
            
            for event in events_to_process:
                try:
                    self._analyze_event(event)
                except Exception as e:
                    self.logger.error(f"Error processing event: {e}")
            
            time.sleep(0.1)  # Small delay to prevent busy waiting
            
    def _analyze_event(self, event: DetectionEvent):
        """Analyze a single event for anomalies"""
        try:
            # Convert event to feature vector
            features = self._extract_features(event)
            
            # Check for anomaly if model is available
            if self.anomaly_detector.is_trained():
                is_anomaly, confidence = self.anomaly_detector.predict(features)
                event.is_anomaly = is_anomaly
                event.risk_score = confidence
                
                # Generate alert if anomaly detected
                if is_anomaly and confidence >= self.config.get('detection', {}).get('anomaly_threshold', 0.7):
                    self._generate_alert(event, confidence)
            
            # Store event in database
            self._store_event(event)
            
        except Exception as e:
            self.logger.error(f"Error analyzing event: {e}")
            
    def _extract_features(self, event: DetectionEvent) -> List[float]:
        """Extract numerical features from an event"""
        features = []
        
        # Time-based features
        hour = event.timestamp.hour
        day_of_week = event.timestamp.weekday()
        features.extend([hour, day_of_week])
        
        # Event type features (one-hot encoding)
        event_types = ['file_access', 'usb_event', 'process_launch', 'user_behavior']
        for i, etype in enumerate(event_types):
            features.append(1.0 if event.event_type == etype else 0.0)
        
        # Event-specific features
        if event.event_type == 'file_access':
            # File extension, path depth, etc.
            file_path = event.data.get('file_path', '')
            features.extend([
                len(file_path),
                file_path.count('/') + file_path.count('\\'),
                1.0 if file_path.endswith('.exe') else 0.0,
                1.0 if 'system' in file_path.lower() else 0.0
            ])
        elif event.event_type == 'usb_event':
            # USB device features
            features.extend([
                1.0 if event.data.get('event_type') == 'insert' else 0.0,
                len(event.data.get('device_name', '')),
                1.0 if event.data.get('vendor_id') == 'unknown' else 0.0
            ])
        elif event.event_type == 'process_launch':
            # Process features
            app_name = event.data.get('app_name', '')
            features.extend([
                len(app_name),
                1.0 if app_name.endswith('.exe') else 0.0,
                1.0 if 'temp' in event.data.get('app_path', '').lower() else 0.0
            ])
        elif event.event_type == 'user_behavior':
            # Behavior features
            features.extend([
                event.data.get('duration_seconds', 0) / 3600.0,  # Convert to hours
                len(event.data.get('keystroke_patterns', [])),
                len(event.data.get('mouse_patterns', []))
            ])
        
        # Pad or truncate to fixed size
        target_size = 20
        if len(features) < target_size:
            features.extend([0.0] * (target_size - len(features)))
        elif len(features) > target_size:
            features = features[:target_size]
            
        return features
        
    def _generate_alert(self, event: DetectionEvent, confidence: float):
        """Generate an alert for anomalous behavior"""
        severity = self._calculate_severity(confidence)
        
        # Sanitize event data to remove datetime objects
        sanitized_event_data = sanitize_datetime_objects(event.data)
        
        alert_data = {
            'timestamp': event.timestamp.isoformat(),
            'event_type': event.event_type,
            'event_data': sanitized_event_data,
            'confidence': confidence,
            'severity': severity,
            'description': self._generate_alert_description(event)
        }
        
        self.alert_manager.create_alert(alert_data)
        
    def _calculate_severity(self, confidence: float) -> str:
        """Calculate alert severity based on confidence score"""
        if confidence >= 0.9:
            return 'critical'
        elif confidence >= 0.8:
            return 'high'
        elif confidence >= 0.7:
            return 'medium'
        else:
            return 'low'
            
    def _generate_alert_description(self, event: DetectionEvent) -> str:
        """Generate human-readable alert description"""
        descriptions = {
            'file_access': f"Unusual file access pattern detected: {event.data.get('file_path', 'unknown')}",
            'usb_event': f"Suspicious USB activity: {event.data.get('device_name', 'unknown device')}",
            'process_launch': f"Anomalous process execution: {event.data.get('app_name', 'unknown')}",
            'user_behavior': "Unusual user behavior pattern detected"
        }
        
        return descriptions.get(event.event_type, "Unknown anomaly detected")
        
    def _store_event(self, event: DetectionEvent):
        """Store event in database"""
        try:
            # Sanitize event data to remove datetime objects
            sanitized_event_data = sanitize_datetime_objects(event.data)
            
            event_data = {
                'timestamp': event.timestamp.isoformat(),
                'event_type': event.event_type,
                'event_data': safe_json_dumps(sanitized_event_data),
                'risk_score': event.risk_score,
                'is_anomaly': event.is_anomaly
            }
            
            # Encrypt sensitive data if configured
            if self.config.get('security', {}).get('encrypt_logs', True):
                event_data['event_data'] = self.encryption.encrypt(event_data['event_data'])
            
            self.db_manager.insert_event(event_data)
            
        except Exception as e:
            self.logger.error(f"Error storing event: {e}")
            
    def _periodic_training(self):
        """Periodically retrain the anomaly detection model"""
        training_interval = self.config.get('detection', {}).get('training_interval_hours', 24)
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check if it's time to train
                should_train = (
                    self.last_training_time is None or
                    current_time - self.last_training_time >= timedelta(hours=training_interval)
                )
                
                if should_train:
                    self.logger.info("Starting periodic model training")
                    self._train_model()
                    self.last_training_time = current_time
                    
            except Exception as e:
                self.logger.error(f"Error in periodic training: {e}")
                
            # Sleep for 1 hour before checking again
            time.sleep(3600)
            
    def _train_model(self):
        """Train the anomaly detection model with recent data"""
        try:
            # Get training data from database
            training_data = self.db_manager.get_recent_events(
                days=7,  # Use last 7 days of data
                limit=10000  # Maximum number of samples
            )
            
            min_samples = self.config.get('detection', {}).get('min_training_samples', 1000)
            if len(training_data) < min_samples:
                self.logger.warning(f"Insufficient training data: {len(training_data)} < {min_samples}")
                return
                
            # Extract features from training data
            features = []
            for event_data in training_data:
                # Handle timestamp - it might be string or datetime
                timestamp = event_data['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                
                event = DetectionEvent(
                    timestamp=timestamp,
                    event_type=event_data['event_type'],
                    data=json.loads(event_data['event_data']) if isinstance(event_data['event_data'], str) else event_data['event_data']
                )
                features.append(self._extract_features(event))
            
            # Train the model
            self.anomaly_detector.train(features)
            self.anomaly_detector.save_model()
            
            self.logger.info(f"Model trained successfully with {len(features)} samples")
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        return {
            'running': self.running,
            'stealth_mode': self.stealth_mode,
            'monitors': {name: monitor.is_running() for name, monitor in self.monitors.items()},
            'model_trained': self.anomaly_detector.is_trained(),
            'last_training': self.last_training_time.isoformat() if self.last_training_time else None,
            'events_queued': len(self.event_queue)
        }
        
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self.alert_manager.get_recent_alerts(hours)
        
    def acknowledge_alert(self, alert_id: int):
        """Acknowledge an alert"""
        self.alert_manager.acknowledge_alert(alert_id)
