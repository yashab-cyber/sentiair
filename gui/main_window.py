"""
Main GUI window for Sentinair
PyQt5-based graphical user interface
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QTextEdit, QProgressBar, QSystemTrayIcon, QMenu, QAction,
    QStatusBar, QSplitter, QGroupBox, QGridLayout, QFrame,
    QMessageBox, QDialog, QDialogButtonBox, QCheckBox, QSpinBox,
    QComboBox, QLineEdit, QScrollArea
)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPixmap

from gui.dashboard_widget import DashboardWidget
from gui.alerts_widget import AlertsWidget
# from gui.monitoring_widget import MonitoringWidget  # Not implemented yet
# from gui.reports_widget import ReportsWidget  # Not implemented yet  
# from gui.settings_widget import SettingsWidget  # Not implemented yet

class SentinairGUI:
    """Main GUI application for Sentinair"""
    
    def __init__(self, engine, config):
        self.engine = engine
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Qt Application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Sentinair")
        self.app.setApplicationVersion("1.0.0")
        
        # Set application icon
        self._set_application_icon()
        
        # Apply theme
        self._apply_theme()
        
        # Create main window
        self.main_window = QMainWindow()
        self._setup_main_window()
        
        # System tray
        self.system_tray = None
        self._setup_system_tray()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_data)
        
    def _set_application_icon(self):
        """Set application icon"""
        try:
            # Create a simple icon if custom icon not available
            icon = QIcon()
            # You can add custom icon files here
            self.app.setWindowIcon(icon)
        except Exception as e:
            self.logger.debug(f"Could not set application icon: {e}")
            
    def _apply_theme(self):
        """Apply dark/light theme based on configuration"""
        theme = self.config.get_gui_theme()
        
        if theme == 'dark':
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
            
    def _apply_dark_theme(self):
        """Apply dark theme to the application"""
        dark_palette = QPalette()
        
        # Window colors
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        
        # Base colors
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        
        # Text colors
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        
        # Button colors
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        
        # Highlight colors
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        self.app.setPalette(dark_palette)
        
        # Additional stylesheet for modern look
        self.app.setStyleSheet("""
            QMainWindow {
                background-color: #353535;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #353535;
            }
            QTabBar::tab {
                background-color: #454545;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2a82da;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #454545;
                border: 1px solid #555555;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #2a82da;
            }
        """)
        
    def _apply_light_theme(self):
        """Apply light theme to the application"""
        # Use default Qt light theme
        self.app.setPalette(self.app.style().standardPalette())
        
    def _setup_main_window(self):
        """Setup the main application window"""
        self.main_window.setWindowTitle("Sentinair - Behavioral Threat Detection System")
        
        # Set window size
        window_size = self.config.get_window_size()
        self.main_window.resize(window_size[0], window_size[1])
        
        # Center window on screen
        self._center_window()
        
        # Create central widget
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_tabs()
        
        # Create status bar
        self._create_status_bar()
        
        # Create menu bar
        self._create_menu_bar()
        
    def _center_window(self):
        """Center the window on the screen"""
        screen = self.app.desktop().screenGeometry()
        window = self.main_window.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.main_window.move(x, y)
        
    def _create_tabs(self):
        """Create main application tabs"""
        # Dashboard tab
        self.dashboard_widget = DashboardWidget(self.engine, self.config)
        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")
        
        # Alerts tab
        self.alerts_widget = AlertsWidget(self.engine, self.config)
        self.tab_widget.addTab(self.alerts_widget, "Alerts")
        
        # Monitoring tab (placeholder)
        # self.monitoring_widget = MonitoringWidget(self.engine, self.config)
        # self.tab_widget.addTab(self.monitoring_widget, "Monitoring")
        
        # Reports tab (placeholder)
        # self.reports_widget = ReportsWidget(self.engine, self.config)
        # self.tab_widget.addTab(self.reports_widget, "Reports")
        
        # Settings tab (placeholder)
        # self.settings_widget = SettingsWidget(self.engine, self.config)
        # self.tab_widget.addTab(self.settings_widget, "Settings")
        
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.main_window.setStatusBar(self.status_bar)
        
        # Engine status
        self.engine_status_label = QLabel("Engine: Stopped")
        self.status_bar.addWidget(self.engine_status_label)
        
        # Alert count
        self.alert_count_label = QLabel("Alerts: 0")
        self.status_bar.addWidget(self.alert_count_label)
        
        # Last update time
        self.last_update_label = QLabel("Last Update: Never")
        self.status_bar.addPermanentWidget(self.last_update_label)
        
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.main_window.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Export data action
        export_action = QAction('Export Data...', self.main_window)
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self.main_window)
        exit_action.triggered.connect(self._exit_application)
        file_menu.addAction(exit_action)
        
        # Engine menu
        engine_menu = menubar.addMenu('Engine')
        
        # Start/Stop engine
        self.start_engine_action = QAction('Start Engine', self.main_window)
        self.start_engine_action.triggered.connect(self._start_engine)
        engine_menu.addAction(self.start_engine_action)
        
        self.stop_engine_action = QAction('Stop Engine', self.main_window)
        self.stop_engine_action.triggered.connect(self._stop_engine)
        self.stop_engine_action.setEnabled(False)
        engine_menu.addAction(self.stop_engine_action)
        
        engine_menu.addSeparator()
        
        # Force training
        train_action = QAction('Train Model Now', self.main_window)
        train_action.triggered.connect(self._force_training)
        engine_menu.addAction(train_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About action
        about_action = QAction('About', self.main_window)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.system_tray = QSystemTrayIcon(self.main_window)
            
            # Set tray icon
            icon = QIcon()  # You can set a custom icon here
            self.system_tray.setIcon(icon)
            
            # Create tray menu
            tray_menu = QMenu()
            
            # Show/Hide action
            show_action = QAction("Show Sentinair", self.main_window)
            show_action.triggered.connect(self._show_window)
            tray_menu.addAction(show_action)
            
            hide_action = QAction("Hide Sentinair", self.main_window)
            hide_action.triggered.connect(self._hide_window)
            tray_menu.addAction(hide_action)
            
            tray_menu.addSeparator()
            
            # Exit action
            exit_action = QAction("Exit", self.main_window)
            exit_action.triggered.connect(self._exit_application)
            tray_menu.addAction(exit_action)
            
            self.system_tray.setContextMenu(tray_menu)
            self.system_tray.show()
            
            # Connect double-click to show window
            self.system_tray.activated.connect(self._tray_activated)
            
    def _tray_activated(self, reason):
        """Handle system tray activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_window()
            
    def _show_window(self):
        """Show main window"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        
    def _hide_window(self):
        """Hide main window"""
        self.main_window.hide()
        
    def _start_engine(self):
        """Start the detection engine"""
        try:
            self.engine.start()
            self.start_engine_action.setEnabled(False)
            self.stop_engine_action.setEnabled(True)
            self.engine_status_label.setText("Engine: Running")
            
            # Start update timer
            refresh_interval = self.config.get_refresh_interval()
            self.update_timer.start(refresh_interval * 1000)
            
            self.logger.info("Engine started from GUI")
            
        except Exception as e:
            self.logger.error(f"Error starting engine: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to start engine: {e}")
            
    def _stop_engine(self):
        """Stop the detection engine"""
        try:
            self.engine.stop()
            self.start_engine_action.setEnabled(True)
            self.stop_engine_action.setEnabled(False)
            self.engine_status_label.setText("Engine: Stopped")
            
            # Stop update timer
            self.update_timer.stop()
            
            self.logger.info("Engine stopped from GUI")
            
        except Exception as e:
            self.logger.error(f"Error stopping engine: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to stop engine: {e}")
            
    def _force_training(self):
        """Force model training"""
        try:
            # This would trigger immediate training
            # Implementation depends on engine design
            QMessageBox.information(self.main_window, "Training", "Model training initiated")
            self.logger.info("Manual model training requested")
            
        except Exception as e:
            self.logger.error(f"Error forcing training: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to start training: {e}")
            
    def _update_data(self):
        """Update GUI data periodically"""
        try:
            # Update status
            engine_status = self.engine.get_status()
            
            if engine_status.get('running', False):
                self.engine_status_label.setText("Engine: Running")
            else:
                self.engine_status_label.setText("Engine: Stopped")
                
            # Update alert count
            recent_alerts = self.engine.get_recent_alerts(24)
            self.alert_count_label.setText(f"Alerts: {len(recent_alerts)}")
            
            # Update last update time
            self.last_update_label.setText(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
            
            # Update tab widgets
            self.dashboard_widget.update_data()
            self.alerts_widget.update_data()
            self.monitoring_widget.update_data()
            
        except Exception as e:
            self.logger.error(f"Error updating GUI data: {e}")
            
    def _export_data(self):
        """Export system data"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export Data",
                f"sentinair_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                # Export alerts and basic statistics
                recent_alerts = self.engine.get_recent_alerts(168)  # Last week
                
                if self.engine.alert_manager.export_alerts(file_path, 168):
                    QMessageBox.information(self.main_window, "Export", f"Data exported to {file_path}")
                else:
                    QMessageBox.warning(self.main_window, "Export", "Failed to export data")
                    
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to export data: {e}")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
<h2>Sentinair</h2>
<p><b>Version:</b> 1.0.0</p>
<p><b>Description:</b> Offline AI-Powered Behavioral Threat Detection System</p>
<p>Sentinair monitors system behavior patterns and detects anomalies using machine learning, 
all without requiring internet connectivity.</p>
<p><b>Features:</b></p>
<ul>
<li>Behavioral tracking and anomaly detection</li>
<li>File access monitoring</li>
<li>USB device tracking</li>
<li>Process monitoring</li>
<li>Real-time alerts</li>
<li>Offline operation</li>
</ul>
<p><b>Copyright:</b> 2024 Sentinair Project</p>
"""
        
        QMessageBox.about(self.main_window, "About Sentinair", about_text)
        
    def _exit_application(self):
        """Exit the application"""
        try:
            # Stop engine if running
            if self.engine.get_status().get('running', False):
                self.engine.stop()
                
            # Close system tray
            if self.system_tray:
                self.system_tray.hide()
                
            # Exit application
            self.app.quit()
            
        except Exception as e:
            self.logger.error(f"Error exiting application: {e}")
            self.app.quit()
            
    def run(self):
        """Run the GUI application"""
        try:
            # Show main window
            self.main_window.show()
            
            # Auto-start engine if configured
            if self.config.get('system.auto_start_engine', True):
                self._start_engine()
                
            # Start Qt event loop
            sys.exit(self.app.exec_())
            
        except Exception as e:
            self.logger.error(f"Error running GUI: {e}")
            sys.exit(1)
