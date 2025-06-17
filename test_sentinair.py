#!/usr/bin/env python3
"""
Test script for Sentinair
Verifies that all components are working correctly
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        # Core modules
        from core.engine import SentinairEngine
        from core.monitors.file_monitor import FileAccessMonitor
        from core.monitors.usb_monitor import USBMonitor
        from core.monitors.process_monitor import ProcessMonitor
        from core.monitors.behavior_monitor import BehaviorMonitor
        
        # ML modules
        from ml.anomaly_detector import AnomalyDetector
        
        # Utility modules
        from utils.config import Config
        from utils.database import DatabaseManager
        from utils.encryption import DataEncryption
        from utils.logger import setup_logging
        
        # Alert modules
        from alerts.alert_manager import AlertManager
        
        # GUI modules (optional)
        try:
            from gui.main_window import SentinairGUI
            from gui.dashboard_widget import DashboardWidget
            from gui.alerts_widget import AlertsWidget
            gui_available = True
        except ImportError as e:
            print(f"⚠️  GUI modules not available: {e}")
            gui_available = False
        
        # CLI modules
        from cli.cli_interface import SentinairCLI
        
        # Report modules
        from reports.report_generator import ReportGenerator
        
        print("✅ All core modules imported successfully")
        return True, gui_available
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False, False

def test_configuration():
    """Test configuration loading and management"""
    print("🧪 Testing configuration...")
    
    try:
        # Test with default config
        config = Config("config/default.yaml")
        
        # Test getting values
        assert config.get('ml.model_type') == 'isolation_forest'
        assert config.get('detection.anomaly_threshold') == 0.7
        assert config.get('nonexistent.key', 'default') == 'default'
        
        # Test setting values
        original_value = config.get('detection.anomaly_threshold')
        config.set('detection.anomaly_threshold', 0.8)
        assert config.get('detection.anomaly_threshold') == 0.8
        
        # Restore original value
        config.set('detection.anomaly_threshold', original_value)
        
        print("✅ Configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database():
    """Test database operations"""
    print("🧪 Testing database...")
    
    try:
        from utils.config import Config
        from utils.database import DatabaseManager
        
        # Create temporary config
        config = Config("config/default.yaml")
        
        # Test database manager
        db_manager = DatabaseManager(config)
        
        # Test basic operations
        test_event = {
            'timestamp': time.time(),
            'event_type': 'test_event',
            'event_data': '{"test": "data"}',
            'risk_score': 0.5,
            'is_anomaly': False
        }
        
        # Insert test event
        db_manager.insert_event(test_event)
        
        # Query recent events
        recent_events = db_manager.get_recent_events(days=1, limit=10)
        assert len(recent_events) >= 1
        
        print("✅ Database test passed")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_encryption():
    """Test encryption functionality"""
    print("🧪 Testing encryption...")
    
    try:
        from utils.config import Config
        from utils.encryption import DataEncryption
        
        config = Config("config/default.yaml")
        encryption = DataEncryption(config)
        
        # Test encryption/decryption
        test_data = "This is a test message for encryption"
        encrypted = encryption.encrypt(test_data)
        decrypted = encryption.decrypt(encrypted)
        
        assert decrypted == test_data
        assert encrypted != test_data
        
        print("✅ Encryption test passed")
        return True
        
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False

def test_anomaly_detector():
    """Test anomaly detection"""
    print("🧪 Testing anomaly detector...")
    
    try:
        from utils.config import Config
        from ml.anomaly_detector import AnomalyDetector
        import numpy as np
        
        config = Config("config/default.yaml")
        detector = AnomalyDetector(config)
        
        # Generate sample training data
        np.random.seed(42)
        normal_data = np.random.normal(0, 1, (1000, 10))
        
        # Train the model
        training_data = normal_data.tolist()
        success = detector.train(training_data)
        
        assert success
        assert detector.is_trained()
        
        # Test prediction
        test_normal = np.random.normal(0, 1, 10).tolist()
        test_anomaly = np.random.normal(5, 1, 10).tolist()  # Clearly different
        
        is_anomaly_normal, confidence_normal = detector.predict(test_normal)
        is_anomaly_anomaly, confidence_anomaly = detector.predict(test_anomaly)
        
        # Normal data should have lower confidence for being anomaly
        assert confidence_normal < confidence_anomaly
        
        print("✅ Anomaly detector test passed")
        return True
        
    except Exception as e:
        print(f"❌ Anomaly detector test failed: {e}")
        return False

def test_alert_manager():
    """Test alert management"""
    print("🧪 Testing alert manager...")
    
    try:
        from utils.config import Config
        from alerts.alert_manager import AlertManager
        
        config = Config("config/default.yaml")
        alert_manager = AlertManager(config)
        
        # Create test alert
        alert_data = {
            'timestamp': time.time(),
            'event_type': 'test_alert',
            'severity': 'medium',
            'description': 'Test alert for verification',
            'confidence': 0.8
        }
        
        alert_id = alert_manager.create_alert(alert_data)
        assert alert_id is not None
        
        # Get recent alerts
        recent_alerts = alert_manager.get_recent_alerts(hours=1)
        assert len(recent_alerts) >= 1
        
        # Acknowledge alert
        alert_manager.acknowledge_alert(alert_id)
        
        print("✅ Alert manager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Alert manager test failed: {e}")
        return False

def test_monitors():
    """Test monitoring components (basic initialization)"""
    print("🧪 Testing monitors...")
    
    try:
        from utils.config import Config
        from core.monitors.file_monitor import FileAccessMonitor
        from core.monitors.usb_monitor import USBMonitor
        from core.monitors.process_monitor import ProcessMonitor
        from core.monitors.behavior_monitor import BehaviorMonitor
        
        config = Config("config/default.yaml")
        
        # Test monitor initialization
        file_monitor = FileAccessMonitor(config)
        usb_monitor = USBMonitor(config)
        process_monitor = ProcessMonitor(config)
        behavior_monitor = BehaviorMonitor(config)
        
        # Test that they can be created without errors
        assert file_monitor is not None
        assert usb_monitor is not None
        assert process_monitor is not None
        assert behavior_monitor is not None
        
        print("✅ Monitor initialization test passed")
        return True
        
    except Exception as e:
        print(f"❌ Monitor test failed: {e}")
        return False

def test_engine():
    """Test the main detection engine"""
    print("🧪 Testing detection engine...")
    
    try:
        from utils.config import Config
        from core.engine import SentinairEngine
        
        config = Config("config/default.yaml")
        engine = SentinairEngine(config)
        
        # Test basic functionality
        status = engine.get_status()
        assert 'running' in status
        assert 'model_trained' in status
        
        # Test alert retrieval
        alerts = engine.get_recent_alerts(hours=1)
        assert isinstance(alerts, list)
        
        print("✅ Detection engine test passed")
        return True
        
    except Exception as e:
        print(f"❌ Detection engine test failed: {e}")
        return False

def test_cli():
    """Test CLI interface"""
    print("🧪 Testing CLI interface...")
    
    try:
        from utils.config import Config
        from core.engine import SentinairEngine
        from cli.cli_interface import SentinairCLI
        
        config = Config("config/default.yaml")
        engine = SentinairEngine(config)
        cli = SentinairCLI(engine, config)
        
        # Test that CLI can be created
        assert cli is not None
        assert hasattr(cli, 'commands')
        assert 'help' in cli.commands
        
        print("✅ CLI interface test passed")
        return True
        
    except Exception as e:
        print(f"❌ CLI interface test failed: {e}")
        return False

def test_reports():
    """Test report generation"""
    print("🧪 Testing report generation...")
    
    try:
        from utils.config import Config
        from utils.database import DatabaseManager
        from reports.report_generator import ReportGenerator
        
        config = Config("config/default.yaml")
        db_manager = DatabaseManager(config)
        report_generator = ReportGenerator(config, db_manager)
        
        # Test that report generator can be created
        assert report_generator is not None
        
        print("✅ Report generation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Report generation test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files and directories exist"""
    print("🧪 Testing file structure...")
    
    required_files = [
        'main.py',
        'setup.py',
        'requirements.txt',
        'config/default.yaml',
        'signatures/default.yar'
    ]
    
    required_dirs = [
        'core',
        'ml',
        'utils',
        'alerts',
        'gui',
        'cli',
        'reports',
        'examples'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ File structure test passed")
    return True

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("         SENTINAIR COMPONENT TESTS")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Encryption", test_encryption),
        ("Anomaly Detector", test_anomaly_detector),
        ("Alert Manager", test_alert_manager),
        ("Monitors", test_monitors),
        ("Detection Engine", test_engine),
        ("CLI Interface", test_cli),
        ("Reports", test_reports)
    ]
    
    results = []
    gui_available = False
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_name == "Module Imports":
                result, gui_available = test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("                 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if gui_available:
        print("GUI: Available")
    else:
        print("GUI: Not Available (PyQt5 not installed)")
    
    print("=" * 60)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Sentinair is ready to use.")
        print("\nNext steps:")
        print("1. Run: python main.py --mode gui")
        print("2. Or: python main.py --mode cli")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("Try running: pip install -r requirements.txt")
    
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
