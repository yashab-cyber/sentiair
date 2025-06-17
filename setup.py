#!/usr/bin/env python3
"""
Setup script for Sentinair
Initializes the application environment and databases
"""

import os
import sys
import sqlite3
import hashlib
import getpass
from pathlib import Path
from cryptography.fernet import Fernet

def create_directory_structure():
    """Create necessary directories"""
    directories = [
        "core",
        "ml",
        "gui",
        "cli", 
        "data",
        "data/logs",
        "data/models",
        "data/reports",
        "alerts",
        "reports",
        "utils",
        "config",
        "signatures"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files for Python packages
        if directory in ["core", "ml", "gui", "cli", "alerts", "reports", "utils"]:
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✓ Directory structure created")

def create_database():
    """Initialize SQLite database"""
    db_path = "data/sentinair.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            event_data TEXT,
            risk_score REAL DEFAULT 0.0,
            is_anomaly BOOLEAN DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT NOT NULL,
            access_type TEXT NOT NULL,
            process_name TEXT,
            user_name TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usb_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            device_id TEXT,
            device_name TEXT,
            event_type TEXT NOT NULL,
            vendor_id TEXT,
            product_id TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS application_launches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            app_name TEXT NOT NULL,
            app_path TEXT,
            process_id INTEGER,
            command_line TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_behavior (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            activity_type TEXT NOT NULL,
            duration_seconds INTEGER,
            keystroke_patterns TEXT,
            mouse_patterns TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anomaly_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT,
            confidence_score REAL,
            acknowledged BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✓ Database initialized")

def generate_encryption_key():
    """Generate encryption key for data protection"""
    key = Fernet.generate_key()
    
    # Save key to file (in production, this should be more secure)
    key_path = "config/encryption.key"
    with open(key_path, "wb") as key_file:
        key_file.write(key)
    
    # Set file permissions (read-only for owner)
    os.chmod(key_path, 0o600)
    
    print("✓ Encryption key generated")

def create_default_config():
    """Create default configuration file"""
    config_content = """# Sentinair Configuration File

# System Settings
system:
  platform: auto  # auto, linux, windows
  stealth_mode: false
  admin_password_hash: ""  # Will be set during setup
  
# Detection Settings
detection:
  # Behavioral tracking
  track_file_access: true
  track_usb_events: true
  track_app_launches: true
  track_user_behavior: true
  
  # Anomaly detection
  anomaly_threshold: 0.7  # 0.0 to 1.0
  training_interval_hours: 24
  min_training_samples: 1000
  
  # Alert settings
  alert_severity_threshold: "medium"  # low, medium, high, critical
  max_alerts_per_hour: 10
  
# Machine Learning
ml:
  model_type: "isolation_forest"  # isolation_forest, autoencoder
  contamination_rate: 0.1
  n_estimators: 100
  random_state: 42
  
# Storage
storage:
  max_log_size_mb: 500
  log_retention_days: 30
  auto_cleanup: true
  
# GUI Settings
gui:
  theme: "dark"  # dark, light
  window_size: [1200, 800]
  refresh_interval_seconds: 5
  
# Reporting
reporting:
  auto_generate_daily: true
  report_formats: ["pdf", "csv"]
  include_graphs: true
  
# Security
security:
  encrypt_logs: true
  secure_delete: true
  tamper_detection: true
"""
    
    config_path = "config/default.yaml"
    with open(config_path, "w") as config_file:
        config_file.write(config_content)
    
    print("✓ Default configuration created")

def setup_admin_password():
    """Setup admin password for stealth mode"""
    print("\n=== Admin Password Setup ===")
    print("This password will be used to unlock stealth mode and access admin features.")
    
    while True:
        password = getpass.getpass("Enter admin password: ")
        confirm = getpass.getpass("Confirm admin password: ")
        
        if password == confirm:
            if len(password) < 8:
                print("Password must be at least 8 characters long.")
                continue
            break
        else:
            print("Passwords do not match. Please try again.")
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Update config file
    config_path = "config/default.yaml"
    with open(config_path, "r") as f:
        content = f.read()
    
    content = content.replace('admin_password_hash: ""', f'admin_password_hash: "{password_hash}"')
    
    with open(config_path, "w") as f:
        f.write(content)
    
    print("✓ Admin password configured")

def create_sample_yara_rules():
    """Create sample YARA rules for malware detection"""
    yara_rules = """
/*
    Sample YARA rules for Sentinair
    Add your custom rules here
*/

rule SuspiciousExecutable
{
    meta:
        description = "Detects suspicious executable patterns"
        author = "Sentinair"
        date = "2024-01-01"
        
    strings:
        $hex1 = { 4D 5A 90 00 03 00 00 00 }
        $text1 = "CreateRemoteThread"
        $text2 = "VirtualAllocEx"
        $text3 = "WriteProcessMemory"
        
    condition:
        $hex1 at 0 and 2 of ($text*)
}

rule NetworkActivity
{
    meta:
        description = "Detects potential network activity in air-gapped system"
        
    strings:
        $net1 = "socket"
        $net2 = "connect"
        $net3 = "send"
        $net4 = "recv"
        
    condition:
        3 of them
}
"""
    
    yara_path = "signatures/default.yar"
    with open(yara_path, "w") as yara_file:
        yara_file.write(yara_rules)
    
    print("✓ Sample YARA rules created")

def main():
    """Main setup function"""
    print("=" * 50)
    print("      Sentinair Setup")
    print("=" * 50)
    print()
    
    try:
        create_directory_structure()
        create_database()
        generate_encryption_key()
        create_default_config()
        setup_admin_password()
        create_sample_yara_rules()
        
        print()
        print("=" * 50)
        print("✓ Setup completed successfully!")
        print("=" * 50)
        print()
        print("You can now run Sentinair using:")
        print("  python main.py --mode gui     # GUI mode")
        print("  python main.py --mode cli     # CLI mode")
        print("  python main.py --mode stealth # Stealth mode")
        print()
        
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
