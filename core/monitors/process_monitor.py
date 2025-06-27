"""
Process monitoring module
Tracks application launches and process behavior
"""

import time
import threading
import logging
import psutil
from typing import Callable, Dict, Any, Set
from datetime import datetime

class ProcessMonitor:
    """Monitor for process launches and terminations"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.callback = None
        self.running = False
        self.monitor_thread = None
        
        # Track known processes
        self.known_processes: Set[int] = set()
        self._initialize_known_processes()
        
    def _initialize_known_processes(self):
        """Initialize list of currently running processes"""
        try:
            current_pids = {proc.pid for proc in psutil.process_iter()}
            self.known_processes = current_pids
            self.logger.info(f"Initialized with {len(self.known_processes)} known processes")
        except Exception as e:
            self.logger.error(f"Error initializing known processes: {e}")
            
    def start(self):
        """Start process monitoring"""
        if self.running:
            return
            
        self.logger.info("Starting process monitoring")
        self.running = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop(self):
        """Stop process monitoring"""
        if not self.running:
            return
            
        self.logger.info("Stopping process monitoring")
        self.running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            
    def set_callback(self, callback: Callable):
        """Set callback function for events"""
        self.callback = callback
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                current_processes = {proc.pid: proc for proc in psutil.process_iter()}
                current_pids = set(current_processes.keys())
                
                # Check for new processes (launches)
                new_pids = current_pids - self.known_processes
                for pid in new_pids:
                    if pid in current_processes:
                        self._handle_process_launch(current_processes[pid])
                        
                # Check for terminated processes
                terminated_pids = self.known_processes - current_pids
                for pid in terminated_pids:
                    self._handle_process_termination(pid)
                    
                # Update known processes
                self.known_processes = current_pids
                
            except Exception as e:
                self.logger.error(f"Error in process monitoring loop: {e}")
                
            time.sleep(1)  # Check every second
            
    def _handle_process_launch(self, process: psutil.Process):
        """Handle process launch event"""
        try:
            # Get process information
            process_info = self._get_process_info(process)
            
            event_data = {
                'event_type': 'launch',
                'process_id': process.pid,
                'app_name': process_info['name'],
                'app_path': process_info['exe'],
                'command_line': process_info['cmdline'],
                'parent_pid': process_info['ppid'],
                'username': process_info['username'],
                'create_time': process_info['create_time'],
                'memory_usage': process_info['memory_info'],
                'cpu_percent': process_info['cpu_percent'],
                'is_suspicious': self._is_suspicious_process(process_info)
            }
            
            if self.callback:
                self.callback('process_launch', event_data)
                
            # Log suspicious processes
            if event_data['is_suspicious']:
                self.logger.warning(f"Suspicious process launched: {process_info['name']} (PID: {process.pid})")
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            self.logger.debug(f"Could not get info for process {process.pid}: {e}")
        except Exception as e:
            self.logger.error(f"Error handling process launch: {e}")
            
    def _handle_process_termination(self, pid: int):
        """Handle process termination event"""
        try:
            event_data = {
                'event_type': 'termination',
                'process_id': pid,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.callback:
                self.callback('process_termination', event_data)
                
        except Exception as e:
            self.logger.error(f"Error handling process termination: {e}")
            
    def _get_process_info(self, process: psutil.Process) -> Dict[str, Any]:
        """Get comprehensive process information"""
        info = {
            'name': 'unknown',
            'exe': 'unknown',
            'cmdline': [],
            'ppid': 0,
            'username': 'unknown',
            'create_time': 0,
            'memory_info': 0,
            'cpu_percent': 0.0
        }
        
        try:
            info['name'] = process.name()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
            
        try:
            info['exe'] = process.exe()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
            
        try:
            info['cmdline'] = process.cmdline()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
            
        try:
            info['ppid'] = process.ppid()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
            
        try:
            info['username'] = process.username()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
            
        try:
            info['create_time'] = process.create_time()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
            
        try:
            memory_info = process.memory_info()
            info['memory_info'] = memory_info.rss  # Resident Set Size
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
            
        try:
            info['cpu_percent'] = process.cpu_percent()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
            
        return info
        
    def _is_suspicious_process(self, process_info: Dict[str, Any]) -> bool:
        """Check if process exhibits suspicious characteristics"""
        suspicious_indicators = []
        
        # Check executable path
        exe_path = process_info.get('exe', '').lower()
        suspicious_paths = [
            'temp', 'tmp', 'appdata', 'roaming', 'downloads',
            'recycle', 'system32', 'windows\\system32'
        ]
        
        if any(path in exe_path for path in suspicious_paths):
            suspicious_indicators.append('suspicious_path')
            
        # Check process name
        process_name = process_info.get('name', '').lower()
        suspicious_names = [
            'cmd.exe', 'powershell.exe', 'wscript.exe', 'cscript.exe',
            'regsvr32.exe', 'rundll32.exe', 'mshta.exe', 'certutil.exe'
        ]
        
        if process_name in suspicious_names:
            suspicious_indicators.append('suspicious_name')
            
        # Check command line arguments
        cmdline = ' '.join(process_info.get('cmdline', [])).lower()
        suspicious_cmdline_patterns = [
            'powershell -enc', 'powershell -e ', 'cmd /c echo',
            'wget', 'curl', 'invoke-webrequest', 'downloadstring',
            'base64', 'bypass', 'hidden', 'noprofile'
        ]
        
        if any(pattern in cmdline for pattern in suspicious_cmdline_patterns):
            suspicious_indicators.append('suspicious_cmdline')
            
        # Check if running from unusual location
        if exe_path and not any(allowed in exe_path for allowed in [
            'program files', 'windows', 'system32', 'program files (x86)'
        ]):
            if any(unusual in exe_path for unusual in ['temp', 'appdata', 'downloads']):
                suspicious_indicators.append('unusual_location')
                
        # Check memory usage (unusually high for simple processes)
        memory_mb = process_info.get('memory_info', 0) / (1024 * 1024)
        if memory_mb > 500:  # More than 500MB
            suspicious_indicators.append('high_memory')
            
        return len(suspicious_indicators) >= 2  # At least 2 indicators
        
    def is_running(self) -> bool:
        """Check if monitor is running"""
        return self.running
        
    def get_running_processes(self) -> list:
        """Get list of currently running processes"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.error(f"Error getting running processes: {e}")
            
        return processes
