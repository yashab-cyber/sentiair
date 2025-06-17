"""
Dashboard widget for Sentinair GUI
Displays system overview, statistics, and real-time status
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QProgressBar, QTableWidget, QTableWidgetItem,
    QGroupBox, QPushButton, QTextEdit, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DashboardWidget(QWidget):
    """Dashboard widget showing system overview"""
    
    def __init__(self, engine, config):
        super().__init__()
        self.engine = engine
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dashboard UI"""
        layout = QVBoxLayout(self)
        
        # Create top row with key metrics
        self.create_metrics_row(layout)
        
        # Create middle section with charts and recent activity
        self.create_main_section(layout)
        
        # Create bottom section with system status
        self.create_status_section(layout)
        
    def create_metrics_row(self, parent_layout):
        """Create top metrics row"""
        metrics_frame = QFrame()
        metrics_frame.setFrameStyle(QFrame.StyledPanel)
        metrics_layout = QHBoxLayout(metrics_frame)
        
        # Total Events
        self.total_events_widget = self.create_metric_widget("Total Events", "0", "#3498db")
        metrics_layout.addWidget(self.total_events_widget)
        
        # Active Alerts
        self.active_alerts_widget = self.create_metric_widget("Active Alerts", "0", "#e74c3c")
        metrics_layout.addWidget(self.active_alerts_widget)
        
        # Anomalies Today
        self.anomalies_today_widget = self.create_metric_widget("Anomalies Today", "0", "#f39c12")
        metrics_layout.addWidget(self.anomalies_today_widget)
        
        # System Health
        self.system_health_widget = self.create_metric_widget("System Health", "Good", "#27ae60")
        metrics_layout.addWidget(self.system_health_widget)
        
        parent_layout.addWidget(metrics_frame)
        
    def create_metric_widget(self, title: str, value: str, color: str) -> QGroupBox:
        """Create a metric display widget"""
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        
        # Value label
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        value_label.setFont(font)
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(value_label)
        
        # Store reference to update later
        group.value_label = value_label
        
        return group
        
    def create_main_section(self, parent_layout):
        """Create main dashboard section with charts and activity"""
        main_frame = QFrame()
        main_layout = QHBoxLayout(main_frame)
        
        # Left side - Charts
        charts_group = QGroupBox("Activity Overview")
        charts_layout = QVBoxLayout(charts_group)
        
        # Create matplotlib figure for charts
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        charts_layout.addWidget(self.canvas)
        
        main_layout.addWidget(charts_group, 2)  # 2/3 of space
        
        # Right side - Recent Activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_text = QTextEdit()
        self.activity_text.setReadOnly(True)
        self.activity_text.setMaximumHeight(200)
        activity_layout.addWidget(self.activity_text)
        
        # Recent Alerts Table
        alerts_label = QLabel("Recent Alerts")
        alerts_label.setFont(QFont("Arial", 10, QFont.Bold))
        activity_layout.addWidget(alerts_label)
        
        self.recent_alerts_table = QTableWidget()
        self.recent_alerts_table.setColumnCount(3)
        self.recent_alerts_table.setHorizontalHeaderLabels(["Time", "Type", "Severity"])
        self.recent_alerts_table.setMaximumHeight(150)
        activity_layout.addWidget(self.recent_alerts_table)
        
        main_layout.addWidget(activity_group, 1)  # 1/3 of space
        
        parent_layout.addWidget(main_frame)
        
    def create_status_section(self, parent_layout):
        """Create system status section"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QGridLayout(status_frame)
        
        # Engine Status
        status_layout.addWidget(QLabel("Engine Status:"), 0, 0)
        self.engine_status_label = QLabel("Stopped")
        self.engine_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        status_layout.addWidget(self.engine_status_label, 0, 1)
        
        # Model Status
        status_layout.addWidget(QLabel("ML Model:"), 0, 2)
        self.model_status_label = QLabel("Not Trained")
        self.model_status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        status_layout.addWidget(self.model_status_label, 0, 3)
        
        # Last Training
        status_layout.addWidget(QLabel("Last Training:"), 1, 0)
        self.last_training_label = QLabel("Never")
        status_layout.addWidget(self.last_training_label, 1, 1)
        
        # Database Size
        status_layout.addWidget(QLabel("Database Size:"), 1, 2)
        self.db_size_label = QLabel("Unknown")
        status_layout.addWidget(self.db_size_label, 1, 3)
        
        parent_layout.addWidget(status_frame)
        
    def update_data(self):
        """Update dashboard data"""
        try:
            # Update metrics
            self.update_metrics()
            
            # Update charts
            self.update_charts()
            
            # Update recent activity
            self.update_recent_activity()
            
            # Update status
            self.update_status()
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")
            
    def update_metrics(self):
        """Update metric widgets"""
        try:
            # Get engine status and statistics
            engine_status = self.engine.get_status()
            
            # Update total events (simplified - would query database in real implementation)
            self.total_events_widget.value_label.setText("1,234")
            
            # Update active alerts
            recent_alerts = self.engine.get_recent_alerts(24)
            active_alerts = [alert for alert in recent_alerts if not alert.get('acknowledged', False)]
            self.active_alerts_widget.value_label.setText(str(len(active_alerts)))
            
            # Update anomalies today
            today_anomalies = [alert for alert in recent_alerts 
                             if alert.get('timestamp', datetime.now()).date() == datetime.now().date()]
            self.anomalies_today_widget.value_label.setText(str(len(today_anomalies)))
            
            # Update system health
            if engine_status.get('running', False):
                health = "Good" if len(active_alerts) < 5 else "Warning"
                color = "#27ae60" if health == "Good" else "#f39c12"
            else:
                health = "Stopped"
                color = "#e74c3c"
                
            self.system_health_widget.value_label.setText(health)
            self.system_health_widget.value_label.setStyleSheet(f"color: {color};")
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
            
    def update_charts(self):
        """Update dashboard charts"""
        try:
            self.figure.clear()
            
            # Create subplots
            ax1 = self.figure.add_subplot(221)  # Top left
            ax2 = self.figure.add_subplot(222)  # Top right
            ax3 = self.figure.add_subplot(212)  # Bottom (full width)
            
            # Chart 1: Alert Severity Distribution
            recent_alerts = self.engine.get_recent_alerts(168)  # Last week
            severity_counts = {}
            for alert in recent_alerts:
                severity = alert.get('severity', 'unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
            if severity_counts:
                ax1.pie(severity_counts.values(), labels=severity_counts.keys(), autopct='%1.1f%%')
                ax1.set_title('Alert Severity Distribution')
            else:
                ax1.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Alert Severity Distribution')
                
            # Chart 2: Event Type Distribution
            event_types = {'file_access': 45, 'usb_event': 12, 'process_launch': 23, 'user_behavior': 20}
            ax2.bar(event_types.keys(), event_types.values())
            ax2.set_title('Event Types (24h)')
            ax2.tick_params(axis='x', rotation=45)
            
            # Chart 3: Activity Timeline
            hours = list(range(24))
            activity = [max(0, 10 + i * 2 + (i % 3) * 5) for i in hours]  # Sample data
            ax3.plot(hours, activity, marker='o')
            ax3.set_title('24-Hour Activity Timeline')
            ax3.set_xlabel('Hour')
            ax3.set_ylabel('Events')
            ax3.grid(True, alpha=0.3)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error updating charts: {e}")
            
    def update_recent_activity(self):
        """Update recent activity display"""
        try:
            # Update activity text
            activity_lines = [
                f"{datetime.now().strftime('%H:%M:%S')} - System monitoring active",
                f"{(datetime.now() - timedelta(minutes=2)).strftime('%H:%M:%S')} - File access detected: document.pdf",
                f"{(datetime.now() - timedelta(minutes=5)).strftime('%H:%M:%S')} - USB device inserted",
                f"{(datetime.now() - timedelta(minutes=8)).strftime('%H:%M:%S')} - Process launched: notepad.exe",
                f"{(datetime.now() - timedelta(minutes=12)).strftime('%H:%M:%S')} - Behavioral pattern analyzed"
            ]
            
            self.activity_text.setText("\n".join(activity_lines))
            
            # Update recent alerts table
            recent_alerts = self.engine.get_recent_alerts(24)[:5]  # Last 5 alerts
            
            self.recent_alerts_table.setRowCount(len(recent_alerts))
            
            for i, alert in enumerate(recent_alerts):
                # Time
                time_str = alert.get('timestamp', datetime.now()).strftime('%H:%M')
                self.recent_alerts_table.setItem(i, 0, QTableWidgetItem(time_str))
                
                # Type
                event_type = alert.get('alert_type', 'Unknown')
                self.recent_alerts_table.setItem(i, 1, QTableWidgetItem(event_type))
                
                # Severity
                severity = alert.get('severity', 'medium')
                severity_item = QTableWidgetItem(severity.title())
                
                # Color code by severity
                if severity == 'critical':
                    severity_item.setBackground(Qt.red)
                elif severity == 'high':
                    severity_item.setBackground(Qt.darkYellow)
                elif severity == 'medium':
                    severity_item.setBackground(Qt.yellow)
                    
                self.recent_alerts_table.setItem(i, 2, severity_item)
                
            self.recent_alerts_table.resizeColumnsToContents()
            
        except Exception as e:
            self.logger.error(f"Error updating recent activity: {e}")
            
    def update_status(self):
        """Update system status display"""
        try:
            engine_status = self.engine.get_status()
            
            # Engine status
            if engine_status.get('running', False):
                self.engine_status_label.setText("Running")
                self.engine_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.engine_status_label.setText("Stopped")
                self.engine_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
                
            # Model status
            if engine_status.get('model_trained', False):
                self.model_status_label.setText("Trained")
                self.model_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.model_status_label.setText("Not Trained")
                self.model_status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
                
            # Last training
            last_training = engine_status.get('last_training')
            if last_training:
                self.last_training_label.setText(last_training.strftime('%Y-%m-%d %H:%M'))
            else:
                self.last_training_label.setText("Never")
                
            # Database size (simplified)
            self.db_size_label.setText("2.3 MB")
            
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
