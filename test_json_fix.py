#!/usr/bin/env python3
"""
Quick test to verify JSON serialization fixes
"""

import sys
from pathlib import Path
from datetime import datetime
import time

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.engine import SentinairEngine
from utils.config import Config
from utils.logger import setup_logging

def main():
    print("🧪 Testing JSON serialization fixes...")
    
    setup_logging("WARNING")
    config = Config()
    engine = SentinairEngine(config)
    
    print("📡 Starting engine...")
    engine.start()
    time.sleep(1)
    
    # Test event with datetime objects
    test_data = {
        'file_path': '/etc/passwd',
        'operation': 'read',
        'access_time': datetime.now().isoformat(),
        'test_datetime': datetime.now(),  # This should be handled now
        'nested_data': {
            'timestamp': datetime.now(),
            'value': 'test'
        }
    }
    
    try:
        print("📝 Storing test event with datetime objects...")
        engine._on_event('file_access', test_data)
        print('✅ Event stored successfully - JSON fix working!')
        
        time.sleep(2)
        status = engine.get_status()
        print(f'📊 Status: Events queued: {status["events_queued"]}')
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False
        
    finally:
        engine.stop()

if __name__ == "__main__":
    success = main()
    print("✅ Test passed!" if success else "❌ Test failed!")
