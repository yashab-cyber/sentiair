"""
File access monitoring module
Tracks file system access patterns for anomaly detection
"""

import os
import time
import threading
import logging
from pathlib import Path
from typing import Callable, Dict, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil

class FileAccessHandler(FileSystemEventHandler):
    """Handler for file system events"""
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_event('modified', event.src_path)
            
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_event('created', event.src_path)
            
    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_file_event('deleted', event.src_path)
            
    def on_moved(self, event):
        if not event.is_directory:
            self._handle_file_event('moved', event.src_path, event.dest_path)
            
    def _handle_file_event(self, access_type: str, file_path: str, dest_path: str = None):
        """Handle a file system event"""
        try:
            # Get additional context
            process_info = self._get_current_process_info()
            
            event_data = {
                'file_path': file_path,
                'access_type': access_type,
                'file_size': self._get_file_size(file_path),
                'file_extension': Path(file_path).suffix.lower(),
                'process_name': process_info.get('name'),
                'process_pid': process_info.get('pid'),
                'user_name': process_info.get('username')
            }
            
            if dest_path:
                event_data['dest_path'] = dest_path
                
            self.callback('file_access', event_data)
            
        except Exception as e:
            self.logger.error(f"Error handling file event: {e}")
            
    def _get_current_process_info(self) -> Dict[str, Any]:
        """Get information about the current process accessing the file"""
        try:
            current_process = psutil.Process()
            return {
                'name': current_process.name(),
                'pid': current_process.pid,
                'username': current_process.username(),
                'create_time': current_process.create_time()
            }
        except Exception as e:
            self.logger.debug(f"Could not get process info: {e}")
            return {}
            
    def _get_file_size(self, file_path: str) -> int:
        """Get file size safely"""
        try:
            return os.path.getsize(file_path)
        except (OSError, FileNotFoundError):
            return 0

class FileAccessMonitor:
    """Monitor for file access patterns"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.observer = None
        self.callback = None
        self.running = False
        
        # Paths to monitor
        self.monitor_paths = self._get_monitor_paths()
        
    def _get_monitor_paths(self) -> list:
        """Get list of paths to monitor"""
        default_paths = []
        
        # Add common sensitive directories
        if os.name == 'nt':  # Windows
            default_paths.extend([
                os.path.expanduser('~\\Documents'),
                os.path.expanduser('~\\Desktop'),
                os.path.expanduser('~\\Downloads'),
                'C:\\Windows\\System32',
                'C:\\Program Files',
                'C:\\Program Files (x86)'
            ])
        else:  # Linux/Unix
            default_paths.extend([
                os.path.expanduser('~/Documents'),
                os.path.expanduser('~/Desktop'),
                os.path.expanduser('~/Downloads'),
                '/etc',
                '/usr/bin',
                '/var/log'
            ])
            
        # Filter existing paths
        existing_paths = []
        for path in default_paths:
            if os.path.exists(path):
                existing_paths.append(path)
            else:
                self.logger.debug(f"Path does not exist: {path}")
                
        return existing_paths
        
    def start(self):
        """Start file access monitoring"""
        if self.running:
            return
            
        self.logger.info("Starting file access monitoring")
        self.running = True
        
        # Create observer and handler
        self.observer = Observer()
        handler = FileAccessHandler(self._on_file_event)
        
        # Add watchers for each path
        for path in self.monitor_paths:
            try:
                self.observer.schedule(handler, path, recursive=True)
                self.logger.debug(f"Monitoring path: {path}")
            except Exception as e:
                self.logger.error(f"Failed to monitor path {path}: {e}")
                
        # Start observer
        try:
            self.observer.start()
            self.logger.info(f"File monitoring started for {len(self.monitor_paths)} paths")
        except Exception as e:
            self.logger.error(f"Failed to start file monitoring: {e}")
            self.running = False
            
    def stop(self):
        """Stop file access monitoring"""
        if not self.running:
            return
            
        self.logger.info("Stopping file access monitoring")
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
    def set_callback(self, callback: Callable):
        """Set callback function for events"""
        self.callback = callback
        
    def _on_file_event(self, event_type: str, event_data: Dict[str, Any]):
        """Handle file access event"""
        if self.callback:
            self.callback(event_type, event_data)
            
    def is_running(self) -> bool:
        """Check if monitor is running"""
        return self.running
