"""
Configuration management for Sentinair
"""

import os
import yaml
import hashlib
import logging
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for Sentinair"""
    
    def __init__(self, config_path: str = "config/default.yaml"):
        self.config_path = config_path
        self.config_data = {}
        self.logger = logging.getLogger(__name__)
        
        self.load_config()
        
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config_data = yaml.safe_load(f) or {}
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.warning(f"Configuration file not found: {self.config_path}")
                self.config_data = self._get_default_config()
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config_data = self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'system': {
                'platform': 'auto',
                'stealth_mode': False,
                'admin_password_hash': ''
            },
            'detection': {
                'track_file_access': True,
                'track_usb_events': True,
                'track_app_launches': True,
                'track_user_behavior': True,
                'anomaly_threshold': 0.7,
                'training_interval_hours': 24,
                'min_training_samples': 1000,
                'alert_severity_threshold': 'medium',
                'max_alerts_per_hour': 10
            },
            'ml': {
                'model_type': 'isolation_forest',
                'contamination_rate': 0.1,
                'n_estimators': 100,
                'random_state': 42
            },
            'storage': {
                'max_log_size_mb': 500,
                'log_retention_days': 30,
                'auto_cleanup': True
            },
            'gui': {
                'theme': 'dark',
                'window_size': [1200, 800],
                'refresh_interval_seconds': 5
            },
            'reporting': {
                'auto_generate_daily': True,
                'report_formats': ['pdf', 'csv'],
                'include_graphs': True
            },
            'security': {
                'encrypt_logs': True,
                'secure_delete': True,
                'tamper_detection': True
            }
        }
        
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        try:
            keys = key_path.split('.')
            value = self.config_data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
                    
            return value
            
        except Exception as e:
            self.logger.debug(f"Error getting config value for {key_path}: {e}")
            return default
            
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        try:
            keys = key_path.split('.')
            config = self.config_data
            
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
                
            # Set the value
            config[keys[-1]] = value
            
        except Exception as e:
            self.logger.error(f"Error setting config value for {key_path}: {e}")
            
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
                
            self.logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            
    def validate_stealth_key(self, provided_key: str) -> bool:
        """Validate stealth mode unlock key"""
        try:
            stored_hash = self.get('system.admin_password_hash', '')
            if not stored_hash:
                self.logger.warning("No admin password hash configured")
                return False
                
            provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
            return provided_hash == stored_hash
            
        except Exception as e:
            self.logger.error(f"Error validating stealth key: {e}")
            return False
            
    def get_database_path(self) -> str:
        """Get database file path"""
        return os.path.join('data', 'sentinair.db')
        
    def get_encryption_key_path(self) -> str:
        """Get encryption key file path"""
        return os.path.join('config', 'encryption.key')
        
    def get_log_directory(self) -> str:
        """Get log directory path"""
        return os.path.join('data', 'logs')
        
    def get_report_directory(self) -> str:
        """Get report directory path"""
        return os.path.join('data', 'reports')
        
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        feature_map = {
            'file_monitoring': 'detection.track_file_access',
            'usb_monitoring': 'detection.track_usb_events',
            'process_monitoring': 'detection.track_app_launches',
            'behavior_monitoring': 'detection.track_user_behavior',
            'encryption': 'security.encrypt_logs',
            'auto_reporting': 'reporting.auto_generate_daily'
        }
        
        config_key = feature_map.get(feature)
        if config_key:
            return self.get(config_key, False)
        else:
            self.logger.warning(f"Unknown feature: {feature}")
            return False
            
    def get_alert_threshold(self) -> float:
        """Get anomaly detection threshold"""
        return self.get('detection.anomaly_threshold', 0.7)
        
    def get_training_interval(self) -> int:
        """Get model training interval in hours"""
        return self.get('detection.training_interval_hours', 24)
        
    def get_max_log_size(self) -> int:
        """Get maximum log size in MB"""
        return self.get('storage.max_log_size_mb', 500)
        
    def get_log_retention_days(self) -> int:
        """Get log retention period in days"""
        return self.get('storage.log_retention_days', 30)
        
    def get_gui_theme(self) -> str:
        """Get GUI theme"""
        return self.get('gui.theme', 'dark')
        
    def get_window_size(self) -> tuple:
        """Get default window size"""
        size = self.get('gui.window_size', [1200, 800])
        return tuple(size)
        
    def get_refresh_interval(self) -> int:
        """Get GUI refresh interval in seconds"""
        return self.get('gui.refresh_interval_seconds', 5)
