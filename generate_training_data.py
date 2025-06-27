#!/usr/bin/env python3
"""
Direct database training data generator for Sentinair
"""

import random
from datetime import datetime, timedelta
from utils.config import Config
from utils.database import DatabaseManager
from utils.json_utils import safe_json_dumps

def generate_training_data():
    """Generate training data directly to database"""
    print("🔧 SENTINAIR TRAINING DATA GENERATOR")
    print("=" * 40)
    
    # Initialize database
    config = Config()
    db = DatabaseManager(config)
    
    print("📊 Generating normal behavioral patterns...")
    
    normal_events = 0
    base_time = datetime.now()
    
    # Generate normal file access events
    for i in range(100):
        event_time = base_time - timedelta(minutes=random.randint(0, 1440))
        
        event_data = {
            'event_type': 'file_access',
            'timestamp': event_time.isoformat(),
            'event_data': safe_json_dumps({
                'file_path': f'/home/user/documents/file_{i}.txt',
                'file_size': random.randint(1024, 10240),
                'process_name': random.choice(['gedit', 'libreoffice', 'vim', 'nano']),
                'user': 'user',
                'action': random.choice(['read', 'write', 'modify'])
            }),
            'risk_score': 0.1,
            'is_anomaly': False
        }
        
        try:
            db.insert_event(event_data)
            normal_events += 1
        except Exception as e:
            print(f"Error inserting normal event: {e}")
    
    # Generate normal process events
    for i in range(50):
        event_time = base_time - timedelta(minutes=random.randint(0, 1440))
        
        event_data = {
            'event_type': 'process_start',
            'timestamp': event_time.isoformat(),
            'event_data': safe_json_dumps({
                'process_name': random.choice(['firefox', 'chrome', 'gedit', 'terminal']),
                'pid': 1000 + i,
                'user': 'user',
                'command_line': f'/usr/bin/legitimate_app_{i % 10}'
            }),
            'risk_score': 0.1,
            'is_anomaly': False
        }
        
        try:
            db.insert_event(event_data)
            normal_events += 1
        except Exception as e:
            print(f"Error inserting process event: {e}")
    
    print(f"✅ Generated {normal_events} normal events")
    
    print("🚨 Generating anomalous behavioral patterns...")
    
    anomalous_events = 0
    
    # Generate suspicious file access events
    for i in range(30):
        event_time = base_time - timedelta(minutes=random.randint(0, 1440))
        
        suspicious_files = [
            '/etc/passwd', '/etc/shadow', '/root/.ssh/id_rsa',
            '/var/log/auth.log', '/etc/sudoers', '/boot/grub/grub.cfg'
        ]
        
        event_data = {
            'event_type': 'file_access',
            'timestamp': event_time.isoformat(),
            'event_data': safe_json_dumps({
                'file_path': random.choice(suspicious_files),
                'file_size': random.randint(100, 1000),
                'process_name': random.choice(['unknown_proc', 'suspicious_app', 'malware.exe']),
                'user': random.choice(['user', 'root']),
                'action': 'read',
                'anomaly_indicators': ['suspicious_path', 'unauthorized_access']
            }),
            'risk_score': 0.8,
            'is_anomaly': True
        }
        
        try:
            db.insert_event(event_data)
            anomalous_events += 1
        except Exception as e:
            print(f"Error inserting suspicious event: {e}")
    
    # Generate malicious process events
    for i in range(20):
        event_time = base_time - timedelta(minutes=random.randint(0, 1440))
        
        event_data = {
            'event_type': 'process_start',
            'timestamp': event_time.isoformat(),
            'event_data': safe_json_dumps({
                'process_name': f'malware_{i}.exe',
                'pid': 9000 + i,
                'user': random.choice(['root', 'admin']),
                'command_line': f'/tmp/suspicious_binary_{i}',
                'anomaly_indicators': ['unusual_location', 'elevated_privileges']
            }),
            'risk_score': 0.9,
            'is_anomaly': True
        }
        
        try:
            db.insert_event(event_data)
            anomalous_events += 1
        except Exception as e:
            print(f"Error inserting malicious event: {e}")
    
    print(f"✅ Generated {anomalous_events} anomalous events")
    
    # Verify events in database
    total_events_in_db = len(db.get_recent_events(days=7, limit=10000))
    
    print(f"\n📈 TRAINING DATA SUMMARY:")
    print(f"Normal events generated: {normal_events}")
    print(f"Anomalous events generated: {anomalous_events}")
    print(f"Total events in database: {total_events_in_db}")
    
    if anomalous_events > 0:
        print(f"Anomaly ratio: {anomalous_events/(normal_events + anomalous_events)*100:.1f}%")
    
    print(f"\n🎯 Training data generation completed!")
    print("Ready for machine learning model training.")
    
    return total_events_in_db > 0

if __name__ == "__main__":
    try:
        success = generate_training_data()
        if success:
            print("\n✅ Training data generation successful!")
        else:
            print("\n❌ Training data generation failed!")
    except Exception as e:
        print(f"\n❌ Error during training data generation: {e}")
        import traceback
        traceback.print_exc()
