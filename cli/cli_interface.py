"""
Command Line Interface for Sentinair
Provides terminal-based interaction with the threat detection system
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

class SentinairCLI:
    """Command Line Interface for Sentinair"""
    
    def __init__(self, engine, config):
        self.engine = engine
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        
        # CLI commands
        self.commands = {
            'help': self._cmd_help,
            'status': self._cmd_status,
            'start': self._cmd_start,
            'stop': self._cmd_stop,
            'alerts': self._cmd_alerts,
            'stats': self._cmd_stats,
            'config': self._cmd_config,
            'report': self._cmd_report,
            'train': self._cmd_train,
            'clear': self._cmd_clear,
            'exit': self._cmd_exit,
            'quit': self._cmd_exit
        }
        
    def run(self):
        """Start the CLI interface"""
        self.running = True
        self._print_banner()
        self._print_help()
        
        try:
            while self.running:
                try:
                    user_input = input("\nsentinair> ").strip()
                    if user_input:
                        self._process_command(user_input)
                except KeyboardInterrupt:
                    print("\nUse 'exit' or 'quit' to exit gracefully.")
                except EOFError:
                    break
                    
        except Exception as e:
            self.logger.error(f"CLI error: {e}")
        finally:
            self._cleanup()
            
    def _print_banner(self):
        """Print application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                         SENTINAIR                            ║
║            Offline AI-Powered Threat Detection              ║
║                    Command Line Interface                    ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def _print_help(self):
        """Print available commands"""
        help_text = """
Available Commands:
  help     - Show this help message
  status   - Show system status
  start    - Start monitoring
  stop     - Stop monitoring
  alerts   - Show recent alerts
  stats    - Show detection statistics
  config   - Show/modify configuration
  report   - Generate reports
  train    - Manually trigger model training
  clear    - Clear screen
  exit     - Exit application
        """
        print(help_text)
        
    def _process_command(self, user_input: str):
        """Process user command"""
        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            try:
                self.commands[command](args)
            except Exception as e:
                print(f"Error executing command: {e}")
                self.logger.error(f"Command error: {e}")
        else:
            print(f"Unknown command: {command}. Type 'help' for available commands.")
            
    def _cmd_help(self, args: List[str]):
        """Show help information"""
        if not args:
            self._print_help()
        else:
            command = args[0].lower()
            help_info = {
                'status': 'status - Show current system status including monitoring state and model info',
                'start': 'start - Begin behavioral monitoring and anomaly detection',
                'stop': 'stop - Stop all monitoring activities',
                'alerts': 'alerts [hours] - Show alerts from last N hours (default: 24)',
                'stats': 'stats - Display detection statistics and performance metrics',
                'config': 'config [key] [value] - Show or modify configuration settings',
                'report': 'report [type] - Generate report (pdf, csv, or both)',
                'train': 'train - Manually trigger model retraining'
            }
            
            if command in help_info:
                print(f"\n{help_info[command]}")
            else:
                print(f"No help available for command: {command}")
                
    def _cmd_status(self, args: List[str]):
        """Show system status"""
        try:
            status = self.engine.get_status()
            
            print("\n" + "="*60)
            print("SENTINAIR SYSTEM STATUS")
            print("="*60)
            
            # Overall status
            status_icon = "🟢" if status['running'] else "🔴"
            print(f"System Status: {status_icon} {'RUNNING' if status['running'] else 'STOPPED'}")
            
            if status['stealth_mode']:
                print("Mode: 🥷 STEALTH")
            else:
                print("Mode: 👁️  NORMAL")
                
            # Model status
            model_icon = "🧠" if status['model_trained'] else "❌"
            print(f"AI Model: {model_icon} {'TRAINED' if status['model_trained'] else 'NOT TRAINED'}")
            
            if status['last_training']:
                print(f"Last Training: {status['last_training']}")
                
            # Monitor status
            print("\nMonitor Status:")
            for monitor_name, is_running in status['monitors'].items():
                icon = "✅" if is_running else "❌"
                print(f"  {icon} {monitor_name.title()} Monitor")
                
            # Queue status
            if status['events_queued'] > 0:
                print(f"\nEvents Queued: {status['events_queued']}")
                
            print("="*60)
            
        except Exception as e:
            print(f"Error getting status: {e}")
            
    def _cmd_start(self, args: List[str]):
        """Start monitoring"""
        try:
            if self.engine.get_status()['running']:
                print("System is already running.")
                return
                
            print("Starting Sentinair monitoring...")
            self.engine.start()
            
            # Wait a moment for startup
            time.sleep(2)
            
            if self.engine.get_status()['running']:
                print("✅ Monitoring started successfully!")
            else:
                print("❌ Failed to start monitoring. Check logs for details.")
                
        except Exception as e:
            print(f"Error starting monitoring: {e}")
            
    def _cmd_stop(self, args: List[str]):
        """Stop monitoring"""
        try:
            if not self.engine.get_status()['running']:
                print("System is not running.")
                return
                
            print("Stopping Sentinair monitoring...")
            self.engine.stop()
            
            # Wait a moment for shutdown
            time.sleep(2)
            
            print("✅ Monitoring stopped.")
            
        except Exception as e:
            print(f"Error stopping monitoring: {e}")
            
    def _cmd_alerts(self, args: List[str]):
        """Show recent alerts"""
        try:
            hours = 24
            if args and args[0].isdigit():
                hours = int(args[0])
                
            alerts = self.engine.get_recent_alerts(hours)
            
            if not alerts:
                print(f"No alerts in the last {hours} hours.")
                return
                
            print(f"\n📢 ALERTS (Last {hours} hours)")
            print("="*60)
            
            for alert in alerts[:20]:  # Show up to 20 most recent
                timestamp = alert.get('timestamp', 'Unknown')
                severity = alert.get('severity', 'unknown').upper()
                description = alert.get('description', 'No description')
                confidence = alert.get('confidence', 0) * 100
                
                # Color coding for severity
                severity_icons = {
                    'LOW': '🟡',
                    'MEDIUM': '🟠', 
                    'HIGH': '🔴',
                    'CRITICAL': '🚨'
                }
                
                icon = severity_icons.get(severity, '⚠️')
                
                print(f"{icon} {timestamp}")
                print(f"   Severity: {severity} | Confidence: {confidence:.1f}%")
                print(f"   {description}")
                print("-" * 40)
                
        except Exception as e:
            print(f"Error retrieving alerts: {e}")
            
    def _cmd_stats(self, args: List[str]):
        """Show detection statistics"""
        try:
            # This would typically query the database for statistics
            print("\n📊 DETECTION STATISTICS")
            print("="*60)
            print("Feature not yet implemented in this version.")
            print("This would show:")
            print("  • Total events processed")
            print("  • Anomalies detected")
            print("  • Model accuracy metrics") 
            print("  • Resource usage")
            print("="*60)
            
        except Exception as e:
            print(f"Error retrieving statistics: {e}")
            
    def _cmd_config(self, args: List[str]):
        """Show or modify configuration"""
        try:
            if not args:
                # Show current configuration
                print("\n⚙️  CONFIGURATION")
                print("="*60)
                print("Key configuration settings:")
                
                settings = [
                    ('detection.anomaly_threshold', 'Anomaly Threshold'),
                    ('detection.training_interval_hours', 'Training Interval (hours)'),
                    ('ml.model_type', 'ML Model Type'),
                    ('ml.contamination_rate', 'Contamination Rate'),
                    ('security.encrypt_logs', 'Encrypt Logs')
                ]
                
                for key, label in settings:
                    value = self.config.get(key, 'Not set')
                    print(f"  {label}: {value}")
                    
                print("\nUse 'config <key> <value>' to modify settings")
                print("="*60)
                
            elif len(args) == 1:
                # Show specific setting
                key = args[0]
                value = self.config.get(key, 'Setting not found')
                print(f"{key}: {value}")
                
            elif len(args) >= 2:
                # Modify setting
                key = args[0]
                value = ' '.join(args[1:])
                
                # Try to convert to appropriate type
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit():
                    value = float(value)
                    
                self.config.set(key, value)
                self.config.save_config()
                print(f"✅ Updated {key} = {value}")
                
        except Exception as e:
            print(f"Error handling configuration: {e}")
            
    def _cmd_report(self, args: List[str]):
        """Generate reports"""
        try:
            report_type = args[0] if args else 'pdf'
            
            print(f"📄 Generating {report_type.upper()} report...")
            print("Report generation not yet implemented in this version.")
            print("This would generate:")
            print("  • Summary of detections")
            print("  • Alert timeline")
            print("  • System statistics")
            print("  • Behavioral analysis")
            
        except Exception as e:
            print(f"Error generating report: {e}")
            
    def _cmd_train(self, args: List[str]):
        """Manually trigger model training"""
        try:
            print("🧠 Triggering manual model training...")
            print("Training initiated. This may take several minutes...")
            
            # In a real implementation, this would trigger the training
            print("Training not yet implemented in CLI.")
            print("Training is performed automatically every 24 hours.")
            
        except Exception as e:
            print(f"Error triggering training: {e}")
            
    def _cmd_clear(self, args: List[str]):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self._print_banner()
        
    def _cmd_exit(self, args: List[str]):
        """Exit application"""
        print("Shutting down Sentinair...")
        self.running = False
        
    def _cleanup(self):
        """Cleanup on exit"""
        try:
            if self.engine.get_status()['running']:
                print("Stopping monitoring...")
                self.engine.stop()
        except:
            pass
        print("Goodbye!")
