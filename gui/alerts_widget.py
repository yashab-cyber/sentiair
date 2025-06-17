"""
Alerts widget for Sentinair GUI
Displays and manages security alerts
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QGroupBox, QComboBox, QLabel, QTextEdit, QSplitter,
    QHeaderView, QAbstractItemView, QMessageBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

class AlertDetailsDialog(QDialog):
    """Dialog for showing detailed alert information"""
    
    def __init__(self, alert_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.alert_data = alert_data
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Alert Details")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Alert information
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        
        # Format alert details
        details = f"""
Alert ID: {self.alert_data.get('id', 'Unknown')}
Timestamp: {self.alert_data.get('timestamp', 'Unknown')}
Type: {self.alert_data.get('alert_type', 'Unknown')}
Severity: {self.alert_data.get('severity', 'Unknown')}
Confidence: {self.alert_data.get('confidence_score', 0):.2f}

Description:
{self.alert_data.get('description', 'No description available')}

Event Data:
{str(self.alert_data.get('event_data', {}))}

Status: {'Acknowledged' if self.alert_data.get('acknowledged', False) else 'Active'}
"""
        
        info_text.setPlainText(details.strip())
        layout.addWidget(info_text)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

class AlertsWidget(QWidget):
    """Widget for displaying and managing alerts"""
    
    alert_acknowledged = pyqtSignal(int)  # Signal for alert acknowledgment
    
    def __init__(self, engine, config):
        super().__init__()
        self.engine = engine
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the alerts UI"""
        layout = QVBoxLayout(self)
        
        # Controls section
        self.create_controls_section(layout)
        
        # Main alerts table
        self.create_alerts_table(layout)
        
        # Action buttons
        self.create_action_buttons(layout)
        
    def create_controls_section(self, parent_layout):
        """Create controls for filtering and options"""
        controls_group = QGroupBox("Alert Filters")
        controls_layout = QHBoxLayout(controls_group)
        
        # Severity filter
        controls_layout.addWidget(QLabel("Severity:"))
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["All", "Critical", "High", "Medium", "Low"])
        self.severity_filter.currentTextChanged.connect(self.filter_alerts)
        controls_layout.addWidget(self.severity_filter)
        
        # Status filter
        controls_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Acknowledged", "False Positive"])
        self.status_filter.currentTextChanged.connect(self.filter_alerts)
        controls_layout.addWidget(self.status_filter)
        
        # Time range filter
        controls_layout.addWidget(QLabel("Time Range:"))
        self.time_filter = QComboBox()
        self.time_filter.addItems(["Last Hour", "Last 24 Hours", "Last Week", "All Time"])
        self.time_filter.setCurrentText("Last 24 Hours")
        self.time_filter.currentTextChanged.connect(self.filter_alerts)
        controls_layout.addWidget(self.time_filter)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.update_data)
        controls_layout.addWidget(self.refresh_button)
        
        controls_layout.addStretch()
        
        parent_layout.addWidget(controls_group)
        
    def create_alerts_table(self, parent_layout):
        """Create the main alerts table"""
        table_group = QGroupBox("Security Alerts")
        table_layout = QVBoxLayout(table_group)
        
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(7)
        self.alerts_table.setHorizontalHeaderLabels([
            "ID", "Timestamp", "Type", "Severity", "Confidence", "Description", "Status"
        ])
        
        # Configure table
        self.alerts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.alerts_table.setAlternatingRowColors(True)
        self.alerts_table.setSortingEnabled(True)
        
        # Resize columns
        header = self.alerts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Timestamp
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Severity
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Confidence
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Status
        
        # Double-click to show details
        self.alerts_table.doubleClicked.connect(self.show_alert_details)
        
        table_layout.addWidget(self.alerts_table)
        parent_layout.addWidget(table_group)
        
    def create_action_buttons(self, parent_layout):
        """Create action buttons"""
        buttons_layout = QHBoxLayout()
        
        # Acknowledge button
        self.acknowledge_button = QPushButton("Acknowledge Selected")
        self.acknowledge_button.clicked.connect(self.acknowledge_selected_alerts)
        buttons_layout.addWidget(self.acknowledge_button)
        
        # Mark as false positive button
        self.false_positive_button = QPushButton("Mark as False Positive")
        self.false_positive_button.clicked.connect(self.mark_false_positive)
        buttons_layout.addWidget(self.false_positive_button)
        
        # Show details button
        self.details_button = QPushButton("Show Details")
        self.details_button.clicked.connect(self.show_selected_alert_details)
        buttons_layout.addWidget(self.details_button)
        
        # Export button
        self.export_button = QPushButton("Export Alerts")
        self.export_button.clicked.connect(self.export_alerts)
        buttons_layout.addWidget(self.export_button)
        
        buttons_layout.addStretch()
        
        # Alert count label
        self.alert_count_label = QLabel("Total: 0 alerts")
        buttons_layout.addWidget(self.alert_count_label)
        
        parent_layout.addLayout(buttons_layout)
        
    def update_data(self):
        """Update alerts data"""
        try:
            # Get time range
            time_range_map = {
                "Last Hour": 1,
                "Last 24 Hours": 24,
                "Last Week": 168,
                "All Time": 8760  # ~1 year
            }
            
            hours = time_range_map.get(self.time_filter.currentText(), 24)
            
            # Get alerts from engine
            alerts = self.engine.get_recent_alerts(hours)
            
            # Apply filters
            filtered_alerts = self.apply_filters(alerts)
            
            # Update table
            self.populate_alerts_table(filtered_alerts)
            
            # Update count
            self.alert_count_label.setText(f"Total: {len(filtered_alerts)} alerts")
            
        except Exception as e:
            self.logger.error(f"Error updating alerts data: {e}")
            
    def apply_filters(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply current filters to alerts list"""
        filtered_alerts = alerts
        
        # Severity filter
        severity_filter = self.severity_filter.currentText()
        if severity_filter != "All":
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert.get('severity', '').lower() == severity_filter.lower()
            ]
            
        # Status filter
        status_filter = self.status_filter.currentText()
        if status_filter != "All":
            if status_filter == "Active":
                filtered_alerts = [
                    alert for alert in filtered_alerts
                    if not alert.get('acknowledged', False) and not alert.get('false_positive', False)
                ]
            elif status_filter == "Acknowledged":
                filtered_alerts = [
                    alert for alert in filtered_alerts
                    if alert.get('acknowledged', False) and not alert.get('false_positive', False)
                ]
            elif status_filter == "False Positive":
                filtered_alerts = [
                    alert for alert in filtered_alerts
                    if alert.get('false_positive', False)
                ]
                
        return filtered_alerts
        
    def populate_alerts_table(self, alerts: List[Dict[str, Any]]):
        """Populate the alerts table with data"""
        try:
            self.alerts_table.setRowCount(len(alerts))
            
            for row, alert in enumerate(alerts):
                # ID
                id_item = QTableWidgetItem(str(alert.get('id', '')))
                self.alerts_table.setItem(row, 0, id_item)
                
                # Timestamp
                timestamp = alert.get('timestamp', datetime.now())
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                self.alerts_table.setItem(row, 1, QTableWidgetItem(time_str))
                
                # Type
                alert_type = alert.get('alert_type', 'Unknown')
                self.alerts_table.setItem(row, 2, QTableWidgetItem(alert_type))
                
                # Severity
                severity = alert.get('severity', 'medium')
                severity_item = QTableWidgetItem(severity.title())
                
                # Color code by severity
                if severity == 'critical':
                    severity_item.setBackground(QColor(231, 76, 60))  # Red
                    severity_item.setForeground(QColor(255, 255, 255))  # White text
                elif severity == 'high':
                    severity_item.setBackground(QColor(230, 126, 34))  # Orange
                    severity_item.setForeground(QColor(255, 255, 255))  # White text
                elif severity == 'medium':
                    severity_item.setBackground(QColor(241, 196, 15))  # Yellow
                elif severity == 'low':
                    severity_item.setBackground(QColor(52, 152, 219))  # Blue
                    severity_item.setForeground(QColor(255, 255, 255))  # White text
                    
                self.alerts_table.setItem(row, 3, severity_item)
                
                # Confidence
                confidence = alert.get('confidence_score', 0.0)
                confidence_item = QTableWidgetItem(f"{confidence:.2f}")
                self.alerts_table.setItem(row, 4, confidence_item)
                
                # Description
                description = alert.get('description', 'No description')
                # Truncate long descriptions
                if len(description) > 50:
                    description = description[:47] + "..."
                self.alerts_table.setItem(row, 5, QTableWidgetItem(description))
                
                # Status
                if alert.get('false_positive', False):
                    status = "False Positive"
                    status_color = QColor(149, 165, 166)  # Gray
                elif alert.get('acknowledged', False):
                    status = "Acknowledged"
                    status_color = QColor(39, 174, 96)  # Green
                else:
                    status = "Active"
                    status_color = QColor(231, 76, 60)  # Red
                    
                status_item = QTableWidgetItem(status)
                status_item.setForeground(status_color)
                font = QFont()
                font.setBold(True)
                status_item.setFont(font)
                self.alerts_table.setItem(row, 6, status_item)
                
                # Store alert data in first column for reference
                id_item.setData(Qt.UserRole, alert)
                
        except Exception as e:
            self.logger.error(f"Error populating alerts table: {e}")
            
    def filter_alerts(self):
        """Apply filters when filter controls change"""
        self.update_data()
        
    def get_selected_alerts(self) -> List[Dict[str, Any]]:
        """Get currently selected alerts"""
        selected_alerts = []
        
        for row in range(self.alerts_table.rowCount()):
            if self.alerts_table.item(row, 0).isSelected():
                alert_data = self.alerts_table.item(row, 0).data(Qt.UserRole)
                if alert_data:
                    selected_alerts.append(alert_data)
                    
        return selected_alerts
        
    def acknowledge_selected_alerts(self):
        """Acknowledge selected alerts"""
        try:
            selected_rows = set()
            for item in self.alerts_table.selectedItems():
                selected_rows.add(item.row())
                
            if not selected_rows:
                QMessageBox.information(self, "No Selection", "Please select alerts to acknowledge.")
                return
                
            acknowledged_count = 0
            
            for row in selected_rows:
                alert_data = self.alerts_table.item(row, 0).data(Qt.UserRole)
                if alert_data and not alert_data.get('acknowledged', False):
                    alert_id = alert_data.get('id')
                    if alert_id and self.engine.acknowledge_alert(alert_id):
                        acknowledged_count += 1
                        self.alert_acknowledged.emit(alert_id)
                        
            if acknowledged_count > 0:
                QMessageBox.information(self, "Success", f"Acknowledged {acknowledged_count} alerts.")
                self.update_data()
            else:
                QMessageBox.warning(self, "Warning", "No alerts were acknowledged.")
                
        except Exception as e:
            self.logger.error(f"Error acknowledging alerts: {e}")
            QMessageBox.critical(self, "Error", f"Failed to acknowledge alerts: {e}")
            
    def mark_false_positive(self):
        """Mark selected alerts as false positives"""
        try:
            selected_rows = set()
            for item in self.alerts_table.selectedItems():
                selected_rows.add(item.row())
                
            if not selected_rows:
                QMessageBox.information(self, "No Selection", "Please select alerts to mark as false positive.")
                return
                
            reply = QMessageBox.question(
                self, "Confirm", 
                f"Mark {len(selected_rows)} alerts as false positives?\\n\\nThis will help improve the detection model.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
                
            marked_count = 0
            
            for row in selected_rows:
                alert_data = self.alerts_table.item(row, 0).data(Qt.UserRole)
                if alert_data:
                    alert_id = alert_data.get('id')
                    if alert_id:
                        # Mark as false positive in alert manager
                        if hasattr(self.engine, 'alert_manager'):
                            if self.engine.alert_manager.mark_false_positive(alert_id):
                                marked_count += 1
                                
            if marked_count > 0:
                QMessageBox.information(self, "Success", f"Marked {marked_count} alerts as false positives.")
                self.update_data()
            else:
                QMessageBox.warning(self, "Warning", "No alerts were marked as false positives.")
                
        except Exception as e:
            self.logger.error(f"Error marking false positives: {e}")
            QMessageBox.critical(self, "Error", f"Failed to mark false positives: {e}")
            
    def show_selected_alert_details(self):
        """Show details for the selected alert"""
        try:
            current_row = self.alerts_table.currentRow()
            if current_row < 0:
                QMessageBox.information(self, "No Selection", "Please select an alert to view details.")
                return
                
            alert_data = self.alerts_table.item(current_row, 0).data(Qt.UserRole)
            if alert_data:
                dialog = AlertDetailsDialog(alert_data, self)
                dialog.exec_()
                
        except Exception as e:
            self.logger.error(f"Error showing alert details: {e}")
            
    def show_alert_details(self, index):
        """Show alert details on double-click"""
        try:
            row = index.row()
            alert_data = self.alerts_table.item(row, 0).data(Qt.UserRole)
            if alert_data:
                dialog = AlertDetailsDialog(alert_data, self)
                dialog.exec_()
                
        except Exception as e:
            self.logger.error(f"Error showing alert details: {e}")
            
    def export_alerts(self):
        """Export alerts to file"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Alerts",
                f"sentinair_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                # Get current filtered alerts
                time_range_map = {
                    "Last Hour": 1,
                    "Last 24 Hours": 24,
                    "Last Week": 168,
                    "All Time": 8760
                }
                
                hours = time_range_map.get(self.time_filter.currentText(), 24)
                
                if hasattr(self.engine, 'alert_manager'):
                    if self.engine.alert_manager.export_alerts(file_path, hours):
                        QMessageBox.information(self, "Export", f"Alerts exported to {file_path}")
                    else:
                        QMessageBox.warning(self, "Export", "Failed to export alerts")
                        
        except Exception as e:
            self.logger.error(f"Error exporting alerts: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export alerts: {e}")
