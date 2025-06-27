"""
User behavior monitoring module
Tracks user interaction patterns for anomaly detection
"""

import time
import threading
import logging
from typing import Callable, Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil

# Optional: Import pynput for keystroke and mouse monitoring
try:
    from pynput import keyboard, mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

class BehaviorMonitor:
    """Monitor for user behavior patterns"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.callback = None
        self.running = False
        self.monitor_thread = None
        
        # Behavior tracking
        self.keystroke_patterns = deque(maxlen=1000)
        self.mouse_patterns = deque(maxlen=1000)
        self.activity_periods = []
        self.idle_periods = []
        
        # System state tracking
        self.last_activity_time = datetime.now()
        self.idle_threshold_seconds = 300  # 5 minutes
        self.is_idle = False
        
        # Keyboard and mouse listeners
        self.keyboard_listener = None
        self.mouse_listener = None
        
    def start(self):
        """Start behavior monitoring"""
        if self.running:
            return
            
        self.logger.info("Starting user behavior monitoring")
        self.running = True
        
        # Start system monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Start input monitoring if available
        if PYNPUT_AVAILABLE:
            self._start_input_monitoring()
        else:
            self.logger.warning("pynput not available, limited behavior monitoring")
            
    def stop(self):
        """Stop behavior monitoring"""
        if not self.running:
            return
            
        self.logger.info("Stopping user behavior monitoring")
        self.running = False
        
        # Stop input listeners
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
            
        # Stop monitoring thread
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            
    def set_callback(self, callback: Callable):
        """Set callback function for events"""
        self.callback = callback
        
    def _start_input_monitoring(self):
        """Start keyboard and mouse monitoring"""
        try:
            # Keyboard listener
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()
            
            # Mouse listener
            self.mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            self.mouse_listener.start()
            
            self.logger.info("Input monitoring started")
            
        except Exception as e:
            self.logger.error(f"Failed to start input monitoring: {e}")
            
    def _on_key_press(self, key):
        """Handle key press events"""
        try:
            current_time = datetime.now()
            self._update_activity_time(current_time)
            
            # Record keystroke timing (privacy-preserving)
            keystroke_data = {
                'timestamp': current_time,
                'key_type': self._classify_key(key),
                'time_since_last': self._get_time_since_last_keystroke()
            }
            
            self.keystroke_patterns.append(keystroke_data)
            
        except Exception as e:
            self.logger.debug(f"Error handling key press: {e}")
            
    def _on_key_release(self, key):
        """Handle key release events"""
        try:
            current_time = datetime.now()
            self._update_activity_time(current_time)
            
        except Exception as e:
            self.logger.debug(f"Error handling key release: {e}")
            
    def _on_mouse_move(self, x, y):
        """Handle mouse movement events"""
        try:
            current_time = datetime.now()
            self._update_activity_time(current_time)
            
            # Record mouse movement pattern (sampling to avoid too much data)
            if len(self.mouse_patterns) == 0 or \
               (current_time - self.mouse_patterns[-1]['timestamp']).total_seconds() > 1:
                
                mouse_data = {
                    'timestamp': current_time,
                    'event_type': 'move',
                    'distance_from_last': self._calculate_mouse_distance(x, y)
                }
                
                self.mouse_patterns.append(mouse_data)
                
        except Exception as e:
            self.logger.debug(f"Error handling mouse move: {e}")
            
    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        try:
            current_time = datetime.now()
            self._update_activity_time(current_time)
            
            if pressed:  # Only record press events
                mouse_data = {
                    'timestamp': current_time,
                    'event_type': 'click',
                    'button': str(button),
                    'time_since_last_click': self._get_time_since_last_click()
                }
                
                self.mouse_patterns.append(mouse_data)
                
        except Exception as e:
            self.logger.debug(f"Error handling mouse click: {e}")
            
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events"""
        try:
            current_time = datetime.now()
            self._update_activity_time(current_time)
            
        except Exception as e:
            self.logger.debug(f"Error handling mouse scroll: {e}")
            
    def _update_activity_time(self, current_time: datetime):
        """Update last activity time and handle idle state changes"""
        was_idle = self.is_idle
        self.last_activity_time = current_time
        self.is_idle = False
        
        # If we were idle and now active, record the idle period
        if was_idle:
            self._handle_idle_to_active_transition(current_time)
            
    def _handle_idle_to_active_transition(self, current_time: datetime):
        """Handle transition from idle to active state"""
        try:
            # Calculate idle duration
            if self.idle_periods:
                idle_start = self.idle_periods[-1]['start_time']
                idle_duration = (current_time - idle_start).total_seconds()
                
                # Update the last idle period
                self.idle_periods[-1]['end_time'] = current_time
                self.idle_periods[-1]['duration_seconds'] = idle_duration
                
                # Generate behavior event
                self._generate_behavior_event('idle_to_active', {
                    'idle_duration_seconds': idle_duration,
                    'idle_start': idle_start,
                    'idle_end': current_time
                })
                
        except Exception as e:
            self.logger.error(f"Error handling idle transition: {e}")
            
    def _monitor_loop(self):
        """Main monitoring loop for system state"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check for idle state
                time_since_activity = (current_time - self.last_activity_time).total_seconds()
                
                if not self.is_idle and time_since_activity > self.idle_threshold_seconds:
                    # Transition to idle state
                    self.is_idle = True
                    self.idle_periods.append({
                        'start_time': current_time,
                        'end_time': None,
                        'duration_seconds': 0
                    })
                    
                    self._generate_behavior_event('active_to_idle', {
                        'last_activity': self.last_activity_time,
                        'idle_start': current_time
                    })
                    
                # Periodic behavior analysis
                self._analyze_behavior_patterns()
                
            except Exception as e:
                self.logger.error(f"Error in behavior monitoring loop: {e}")
                
            time.sleep(30)  # Check every 30 seconds
            
    def _analyze_behavior_patterns(self):
        """Analyze collected behavior patterns for anomalies"""
        try:
            current_time = datetime.now()
            
            # Analyze keystroke patterns
            keystroke_analysis = self._analyze_keystroke_patterns()
            
            # Analyze mouse patterns
            mouse_analysis = self._analyze_mouse_patterns()
            
            # Analyze activity patterns
            activity_analysis = self._analyze_activity_patterns()
            
            # Generate behavior summary event
            behavior_data = {
                'analysis_time': current_time,
                'keystroke_analysis': keystroke_analysis,
                'mouse_analysis': mouse_analysis,
                'activity_analysis': activity_analysis,
                'is_anomalous': self._is_behavior_anomalous(
                    keystroke_analysis, mouse_analysis, activity_analysis
                )
            }
            
            self._generate_behavior_event('behavior_analysis', behavior_data)
            
        except Exception as e:
            self.logger.error(f"Error analyzing behavior patterns: {e}")
            
    def _analyze_keystroke_patterns(self) -> Dict[str, Any]:
        """Analyze keystroke timing patterns"""
        if not self.keystroke_patterns:
            return {}
            
        recent_keystrokes = [
            ks for ks in self.keystroke_patterns
            if (datetime.now() - ks['timestamp']).total_seconds() < 3600  # Last hour
        ]
        
        if not recent_keystrokes:
            return {}
            
        # Calculate statistics
        intervals = [ks['time_since_last'] for ks in recent_keystrokes if ks['time_since_last'] > 0]
        
        analysis = {
            'total_keystrokes': len(recent_keystrokes),
            'average_interval': sum(intervals) / len(intervals) if intervals else 0,
            'typing_speed_wpm': self._calculate_typing_speed(recent_keystrokes),
            'key_type_distribution': self._get_key_type_distribution(recent_keystrokes)
        }
        
        return analysis
        
    def _analyze_mouse_patterns(self) -> Dict[str, Any]:
        """Analyze mouse movement and click patterns"""
        if not self.mouse_patterns:
            return {}
            
        recent_mouse = [
            mp for mp in self.mouse_patterns
            if (datetime.now() - mp['timestamp']).total_seconds() < 3600  # Last hour
        ]
        
        if not recent_mouse:
            return {}
            
        clicks = [mp for mp in recent_mouse if mp['event_type'] == 'click']
        moves = [mp for mp in recent_mouse if mp['event_type'] == 'move']
        
        analysis = {
            'total_clicks': len(clicks),
            'total_moves': len(moves),
            'click_frequency': len(clicks) / 60 if clicks else 0,  # clicks per minute
            'average_move_distance': sum(mp['distance_from_last'] for mp in moves) / len(moves) if moves else 0
        }
        
        return analysis
        
    def _analyze_activity_patterns(self) -> Dict[str, Any]:
        """Analyze overall activity patterns"""
        current_time = datetime.now()
        
        # Get recent activity
        recent_idle_periods = [
            ip for ip in self.idle_periods
            if ip['end_time'] and (current_time - ip['end_time']).total_seconds() < 86400  # Last 24 hours
        ]
        
        analysis = {
            'total_idle_periods': len(recent_idle_periods),
            'total_idle_time': sum(ip['duration_seconds'] for ip in recent_idle_periods),
            'average_idle_duration': sum(ip['duration_seconds'] for ip in recent_idle_periods) / len(recent_idle_periods) if recent_idle_periods else 0,
            'is_currently_idle': self.is_idle,
            'current_idle_duration': (current_time - self.last_activity_time).total_seconds() if self.is_idle else 0
        }
        
        return analysis
        
    def _is_behavior_anomalous(self, keystroke_analysis: Dict, mouse_analysis: Dict, activity_analysis: Dict) -> bool:
        """Determine if current behavior patterns are anomalous"""
        anomaly_indicators = []
        
        # Check keystroke anomalies
        if keystroke_analysis:
            typing_speed = keystroke_analysis.get('typing_speed_wpm', 0)
            if typing_speed > 120 or typing_speed < 10:  # Unusually fast or slow
                anomaly_indicators.append('unusual_typing_speed')
                
        # Check mouse anomalies
        if mouse_analysis:
            click_frequency = mouse_analysis.get('click_frequency', 0)
            if click_frequency > 5:  # More than 5 clicks per minute
                anomaly_indicators.append('high_click_frequency')
                
        # Check activity anomalies
        if activity_analysis:
            if activity_analysis.get('is_currently_idle') and \
               activity_analysis.get('current_idle_duration', 0) > 14400:  # 4 hours
                anomaly_indicators.append('extended_idle')
                
        return len(anomaly_indicators) > 0
        
    def _generate_behavior_event(self, event_type: str, event_data: Dict[str, Any]):
        """Generate a behavior event"""
        if self.callback:
            self.callback('user_behavior', {
                'behavior_type': event_type,
                'timestamp': datetime.now().isoformat(),
                **event_data
            })
            
    def _classify_key(self, key) -> str:
        """Classify key type for privacy-preserving analysis"""
        try:
            if hasattr(key, 'char') and key.char:
                if key.char.isalpha():
                    return 'letter'
                elif key.char.isdigit():
                    return 'digit'
                elif key.char in ' \t\n':
                    return 'whitespace'
                else:
                    return 'symbol'
            else:
                return 'special'
        except:
            return 'unknown'
            
    def _get_time_since_last_keystroke(self) -> float:
        """Get time since last keystroke in milliseconds"""
        if len(self.keystroke_patterns) < 2:
            return 0
            
        last_keystroke = self.keystroke_patterns[-2]
        current_time = datetime.now()
        return (current_time - last_keystroke['timestamp']).total_seconds() * 1000
        
    def _get_time_since_last_click(self) -> float:
        """Get time since last mouse click in milliseconds"""
        clicks = [mp for mp in self.mouse_patterns if mp['event_type'] == 'click']
        if len(clicks) < 2:
            return 0
            
        last_click = clicks[-2]
        current_time = datetime.now()
        return (current_time - last_click['timestamp']).total_seconds() * 1000
        
    def _calculate_mouse_distance(self, x: int, y: int) -> float:
        """Calculate distance from last mouse position"""
        moves = [mp for mp in self.mouse_patterns if mp['event_type'] == 'move']
        if not moves:
            return 0
            
        # This is a simplified calculation
        # In practice, you'd store the actual coordinates
        return 0
        
    def _calculate_typing_speed(self, keystrokes: List[Dict]) -> float:
        """Calculate typing speed in words per minute"""
        if len(keystrokes) < 10:
            return 0
            
        # Simplified calculation
        letter_keys = [ks for ks in keystrokes if ks['key_type'] == 'letter']
        if not letter_keys:
            return 0
            
        time_span = (letter_keys[-1]['timestamp'] - letter_keys[0]['timestamp']).total_seconds()
        if time_span == 0:
            return 0
            
        # Assume average word length of 5 characters
        words = len(letter_keys) / 5
        minutes = time_span / 60
        
        return words / minutes if minutes > 0 else 0
        
    def _get_key_type_distribution(self, keystrokes: List[Dict]) -> Dict[str, int]:
        """Get distribution of key types"""
        distribution = defaultdict(int)
        for ks in keystrokes:
            distribution[ks['key_type']] += 1
        return dict(distribution)
        
    def is_running(self) -> bool:
        """Check if monitor is running"""
        return self.running
