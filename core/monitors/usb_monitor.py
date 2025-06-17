"""
USB device monitoring module
Tracks USB device insertion and removal events
"""

import time
import threading
import logging
import platform
from typing import Callable, Dict, Any, List
import psutil

if platform.system() == "Windows":
    try:
        import win32file
        import win32con
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False

class USBMonitor:
    """Monitor for USB device events"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.callback = None
        self.running = False
        self.monitor_thread = None
        
        # Track known devices
        self.known_devices = set()
        self._initialize_known_devices()
        
    def _initialize_known_devices(self):
        """Initialize list of currently connected USB devices"""
        try:
            current_devices = self._get_current_usb_devices()
            self.known_devices = {self._device_signature(device) for device in current_devices}
            self.logger.info(f"Initialized with {len(self.known_devices)} known USB devices")
        except Exception as e:
            self.logger.error(f"Error initializing known devices: {e}")
            
    def _get_current_usb_devices(self) -> List[Dict[str, Any]]:
        """Get list of currently connected USB devices"""
        devices = []
        
        try:
            # Use psutil to get disk partitions (includes USB drives)
            partitions = psutil.disk_partitions()
            for partition in partitions:
                if 'removable' in partition.opts or 'usb' in partition.device.lower():
                    device_info = self._get_device_info(partition)
                    if device_info:
                        devices.append(device_info)
                        
            # Platform-specific device detection
            if platform.system() == "Windows":
                devices.extend(self._get_windows_usb_devices())
            else:
                devices.extend(self._get_linux_usb_devices())
                
        except Exception as e:
            self.logger.error(f"Error getting USB devices: {e}")
            
        return devices
        
    def _get_device_info(self, partition) -> Dict[str, Any]:
        """Extract device information from partition"""
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            return {
                'device_path': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total_bytes': usage.total,
                'free_bytes': usage.free,
                'device_type': 'removable'
            }
        except Exception as e:
            self.logger.debug(f"Could not get device info for {partition.device}: {e}")
            return None
            
    def _get_windows_usb_devices(self) -> List[Dict[str, Any]]:
        """Get USB devices on Windows using WMI (if available)"""
        devices = []
        
        if not WIN32_AVAILABLE:
            return devices
            
        try:
            # This is a simplified implementation
            # In a full implementation, you'd use WMI to query USB devices
            # For now, we'll rely on the disk partition method
            pass
        except Exception as e:
            self.logger.debug(f"Error getting Windows USB devices: {e}")
            
        return devices
        
    def _get_linux_usb_devices(self) -> List[Dict[str, Any]]:
        """Get USB devices on Linux"""
        devices = []
        
        try:
            # Read from /proc/mounts to find USB devices
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        device, mountpoint, fstype = parts[0], parts[1], parts[2]
                        if '/media/' in mountpoint or '/mnt/' in mountpoint:
                            devices.append({
                                'device_path': device,
                                'mountpoint': mountpoint,
                                'fstype': fstype,
                                'device_type': 'usb'
                            })
        except Exception as e:
            self.logger.debug(f"Error reading /proc/mounts: {e}")
            
        return devices
        
    def _device_signature(self, device: Dict[str, Any]) -> str:
        """Create a unique signature for a device"""
        return f"{device.get('device_path', '')}-{device.get('fstype', '')}-{device.get('total_bytes', 0)}"
        
    def start(self):
        """Start USB device monitoring"""
        if self.running:
            return
            
        self.logger.info("Starting USB device monitoring")
        self.running = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop(self):
        """Stop USB device monitoring"""
        if not self.running:
            return
            
        self.logger.info("Stopping USB device monitoring")
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
                current_devices = self._get_current_usb_devices()
                current_signatures = {self._device_signature(device) for device in current_devices}
                
                # Check for new devices (insertions)
                new_devices = current_signatures - self.known_devices
                for signature in new_devices:
                    device = next((d for d in current_devices if self._device_signature(d) == signature), None)
                    if device:
                        self._handle_device_event('insert', device)
                        
                # Check for removed devices
                removed_devices = self.known_devices - current_signatures
                for signature in removed_devices:
                    self._handle_device_event('remove', {'signature': signature})
                    
                # Update known devices
                self.known_devices = current_signatures
                
            except Exception as e:
                self.logger.error(f"Error in USB monitoring loop: {e}")
                
            time.sleep(2)  # Check every 2 seconds
            
    def _handle_device_event(self, event_type: str, device: Dict[str, Any]):
        """Handle USB device event"""
        try:
            event_data = {
                'event_type': event_type,
                'device_path': device.get('device_path', 'unknown'),
                'device_name': self._get_device_name(device),
                'mountpoint': device.get('mountpoint', ''),
                'fstype': device.get('fstype', 'unknown'),
                'total_bytes': device.get('total_bytes', 0),
                'vendor_id': self._extract_vendor_id(device),
                'product_id': self._extract_product_id(device),
                'is_suspicious': self._is_suspicious_device(device)
            }
            
            if self.callback:
                self.callback('usb_event', event_data)
                
            self.logger.info(f"USB {event_type}: {event_data['device_name']}")
            
        except Exception as e:
            self.logger.error(f"Error handling USB event: {e}")
            
    def _get_device_name(self, device: Dict[str, Any]) -> str:
        """Get human-readable device name"""
        device_path = device.get('device_path', '')
        if device_path:
            return device_path.split('/')[-1] if '/' in device_path else device_path
        return 'Unknown USB Device'
        
    def _extract_vendor_id(self, device: Dict[str, Any]) -> str:
        """Extract vendor ID from device (simplified)"""
        # In a full implementation, this would parse USB device information
        return 'unknown'
        
    def _extract_product_id(self, device: Dict[str, Any]) -> str:
        """Extract product ID from device (simplified)"""
        # In a full implementation, this would parse USB device information
        return 'unknown'
        
    def _is_suspicious_device(self, device: Dict[str, Any]) -> bool:
        """Check if device exhibits suspicious characteristics"""
        suspicious_indicators = [
            # Very small or very large devices
            device.get('total_bytes', 0) < 1024 * 1024,  # Less than 1MB
            device.get('total_bytes', 0) > 1024 * 1024 * 1024 * 1024,  # More than 1TB
            
            # Unknown filesystem
            device.get('fstype', '').lower() in ['unknown', ''],
            
            # Suspicious naming patterns
            any(suspicious in device.get('device_path', '').lower() 
                for suspicious in ['hidden', 'stealth', 'badusb'])
        ]
        
        return any(suspicious_indicators)
        
    def is_running(self) -> bool:
        """Check if monitor is running"""
        return self.running
        
    def get_connected_devices(self) -> List[Dict[str, Any]]:
        """Get list of currently connected USB devices"""
        return self._get_current_usb_devices()
