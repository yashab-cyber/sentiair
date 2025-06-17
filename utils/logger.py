"""
Logging configuration and utilities for Sentinair
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_dir: str = "data/logs"):
    """Setup logging configuration for Sentinair"""
    
    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Configure logging level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = os.path.join(log_dir, "sentinair.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error log file
    error_log_file = os.path.join(log_dir, "sentinair_errors.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Security events log
    security_log_file = os.path.join(log_dir, "security_events.log")
    security_handler = logging.handlers.RotatingFileHandler(
        security_log_file,
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(detailed_formatter)
    
    # Create security logger
    security_logger = logging.getLogger('security')
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False  # Don't propagate to root logger
    
    logging.info("Logging system initialized")

def get_security_logger():
    """Get the security events logger"""
    return logging.getLogger('security')

class SecurityAuditLogger:
    """Special logger for security audit events"""
    
    def __init__(self, log_dir: str = "data/logs"):
        self.logger = logging.getLogger('security_audit')
        self.log_dir = log_dir
        
        if not self.logger.handlers:
            self._setup_audit_logger()
            
    def _setup_audit_logger(self):
        """Setup audit logging"""
        audit_log_file = os.path.join(self.log_dir, "audit.log")
        
        # Create audit log handler with strict rotation
        audit_handler = logging.handlers.RotatingFileHandler(
            audit_log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=20
        )
        
        # Detailed audit formatter
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
        )
        
        audit_handler.setFormatter(audit_formatter)
        self.logger.addHandler(audit_handler)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
    def log_event(self, event_type: str, details: dict):
        """Log security audit event"""
        try:
            message = f"{event_type}: {details}"
            self.logger.info(message)
        except Exception as e:
            # Fallback to standard logging
            logging.error(f"Failed to log audit event: {e}")
            
    def log_anomaly_detection(self, confidence: float, event_data: dict):
        """Log anomaly detection event"""
        self.log_event("ANOMALY_DETECTED", {
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'event_data': event_data
        })
        
    def log_admin_access(self, action: str, success: bool):
        """Log admin access attempt"""
        self.log_event("ADMIN_ACCESS", {
            'action': action,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
        
    def log_system_event(self, event_type: str, details: dict):
        """Log system-level security event"""
        self.log_event("SYSTEM_EVENT", {
            'event_type': event_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
