"""
Report generation module for Sentinair
Generates PDF and CSV reports of detection activities and system status
"""

import os
import csv
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.piecharts import Pie
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class ReportGenerator:
    """Generate various types of reports for Sentinair"""
    
    def __init__(self, config, db_manager):
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Report configuration
        self.report_dir = "data/reports"
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Style configuration
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#F18F01',
            'warning': '#C73E1D',
            'danger': '#8B0000'
        }
        
    def generate_daily_report(self, report_date: Optional[datetime] = None) -> Dict[str, str]:
        """Generate daily summary report"""
        if report_date is None:
            report_date = datetime.now()
            
        try:
            self.logger.info(f"Generating daily report for {report_date.date()}")
            
            # Collect data for the report
            report_data = self._collect_daily_data(report_date)
            
            # Generate reports in requested formats
            report_paths = {}
            
            formats = self.config.get('reporting.report_formats', ['pdf', 'csv'])
            
            if 'pdf' in formats and REPORTLAB_AVAILABLE:
                pdf_path = self._generate_pdf_report(report_data, 'daily')
                if pdf_path:
                    report_paths['pdf'] = pdf_path
                    
            if 'csv' in formats:
                csv_path = self._generate_csv_report(report_data, 'daily')
                if csv_path:
                    report_paths['csv'] = csv_path
                    
            self.logger.info(f"Daily report generated: {list(report_paths.keys())}")
            return report_paths
            
        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")
            return {}
            
    def generate_weekly_report(self, week_start: Optional[datetime] = None) -> Dict[str, str]:
        """Generate weekly summary report"""
        if week_start is None:
            week_start = datetime.now() - timedelta(days=7)
            
        try:
            self.logger.info(f"Generating weekly report starting {week_start.date()}")
            
            # Collect weekly data
            report_data = self._collect_weekly_data(week_start)
            
            # Generate reports
            report_paths = {}
            formats = self.config.get('reporting.report_formats', ['pdf', 'csv'])
            
            if 'pdf' in formats and REPORTLAB_AVAILABLE:
                pdf_path = self._generate_pdf_report(report_data, 'weekly')
                if pdf_path:
                    report_paths['pdf'] = pdf_path
                    
            if 'csv' in formats:
                csv_path = self._generate_csv_report(report_data, 'weekly')
                if csv_path:
                    report_paths['csv'] = csv_path
                    
            return report_paths
            
        except Exception as e:
            self.logger.error(f"Error generating weekly report: {e}")
            return {}
            
    def generate_incident_report(self, alert_ids: List[int]) -> Dict[str, str]:
        """Generate incident report for specific alerts"""
        try:
            self.logger.info(f"Generating incident report for {len(alert_ids)} alerts")
            
            # Collect incident data
            report_data = self._collect_incident_data(alert_ids)
            
            # Generate reports
            report_paths = {}
            
            if REPORTLAB_AVAILABLE:
                pdf_path = self._generate_pdf_report(report_data, 'incident')
                if pdf_path:
                    report_paths['pdf'] = pdf_path
                    
            csv_path = self._generate_csv_report(report_data, 'incident')
            if csv_path:
                report_paths['csv'] = csv_path
                
            return report_paths
            
        except Exception as e:
            self.logger.error(f"Error generating incident report: {e}")
            return {}
            
    def _collect_daily_data(self, report_date: datetime) -> Dict[str, Any]:
        """Collect data for daily report"""
        start_date = report_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        data = {
            'report_type': 'daily',
            'report_date': report_date.date(),
            'start_time': start_date,
            'end_time': end_date,
            'summary': {},
            'events': [],
            'alerts': [],
            'statistics': {}
        }
        
        try:
            # Get events from database (simplified - would use actual database queries)
            data['summary'] = {
                'total_events': 0,
                'file_access_events': 0,
                'usb_events': 0,
                'process_events': 0,
                'behavior_events': 0,
                'total_alerts': 0,
                'high_severity_alerts': 0
            }
            
            # Add placeholder data for demonstration
            data['events'] = [
                {
                    'timestamp': report_date,
                    'type': 'file_access',
                    'description': 'Unusual file access pattern detected',
                    'risk_score': 0.8
                }
            ]
            
            data['alerts'] = [
                {
                    'timestamp': report_date,
                    'severity': 'high',
                    'description': 'Suspicious USB device detected',
                    'confidence': 0.9
                }
            ]
            
        except Exception as e:
            self.logger.error(f"Error collecting daily data: {e}")
            
        return data
        
    def _collect_weekly_data(self, week_start: datetime) -> Dict[str, Any]:
        """Collect data for weekly report"""
        end_date = week_start + timedelta(days=7)
        
        data = {
            'report_type': 'weekly',
            'week_start': week_start.date(),
            'week_end': end_date.date(),
            'start_time': week_start,
            'end_time': end_date,
            'daily_summaries': [],
            'trends': {},
            'top_alerts': []
        }
        
        # Collect daily summaries for the week
        for i in range(7):
            day = week_start + timedelta(days=i)
            daily_data = self._collect_daily_data(day)
            data['daily_summaries'].append(daily_data)
            
        return data
        
    def _collect_incident_data(self, alert_ids: List[int]) -> Dict[str, Any]:
        """Collect data for incident report"""
        data = {
            'report_type': 'incident',
            'generated_at': datetime.now(),
            'alert_ids': alert_ids,
            'alerts': [],
            'timeline': [],
            'affected_systems': [],
            'recommendations': []
        }
        
        # Get alert details (would query actual database)
        for alert_id in alert_ids:
            # Placeholder alert data
            data['alerts'].append({
                'id': alert_id,
                'timestamp': datetime.now(),
                'severity': 'high',
                'description': f'Incident alert {alert_id}',
                'confidence': 0.85
            })
            
        return data
        
    def _generate_pdf_report(self, data: Dict[str, Any], report_type: str) -> Optional[str]:
        """Generate PDF report"""
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("ReportLab not available, cannot generate PDF")
            return None
            
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sentinair_{report_type}_report_{timestamp}.pdf"
            filepath = os.path.join(self.report_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor(self.colors['primary'])
            )
            
            story.append(Paragraph(f"Sentinair {report_type.title()} Report", title_style))
            story.append(Spacer(1, 12))
            
            # Report metadata
            if report_type == 'daily':
                story.append(Paragraph(f"Report Date: {data['report_date']}", styles['Normal']))
            elif report_type == 'weekly':
                story.append(Paragraph(f"Week: {data['week_start']} to {data['week_end']}", styles['Normal']))
            elif report_type == 'incident':
                story.append(Paragraph(f"Generated: {data['generated_at']}", styles['Normal']))
                
            story.append(Paragraph(f"Generated by: Sentinair v1.0", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Summary section
            if 'summary' in data:
                story.append(Paragraph("Executive Summary", styles['Heading2']))
                summary_data = [
                    ['Metric', 'Count'],
                    ['Total Events', str(data['summary'].get('total_events', 0))],
                    ['Total Alerts', str(data['summary'].get('total_alerts', 0))],
                    ['High Severity Alerts', str(data['summary'].get('high_severity_alerts', 0))]
                ]
                
                table = Table(summary_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors['primary'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 20))
                
            # Alerts section
            if 'alerts' in data and data['alerts']:
                story.append(Paragraph("Security Alerts", styles['Heading2']))
                
                alert_data = [['Time', 'Severity', 'Description', 'Confidence']]
                for alert in data['alerts'][:10]:  # Show top 10 alerts
                    alert_data.append([
                        alert.get('timestamp', '').strftime('%H:%M:%S') if hasattr(alert.get('timestamp', ''), 'strftime') else str(alert.get('timestamp', '')),
                        alert.get('severity', 'Unknown').upper(),
                        alert.get('description', 'No description')[:50] + '...' if len(alert.get('description', '')) > 50 else alert.get('description', ''),
                        f"{alert.get('confidence', 0) * 100:.1f}%"
                    ])
                    
                alert_table = Table(alert_data, colWidths=[1.5*inch, 1*inch, 3*inch, 1*inch])
                alert_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors['secondary'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(alert_table)
                story.append(Spacer(1, 20))
                
            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey
            )
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                "This report was generated by Sentinair - Offline AI-Powered Behavioral Threat Detection System",
                footer_style
            ))
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"PDF report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {e}")
            return None
            
    def _generate_csv_report(self, data: Dict[str, Any], report_type: str) -> Optional[str]:
        """Generate CSV report"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sentinair_{report_type}_report_{timestamp}.csv"
            filepath = os.path.join(self.report_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header information
                writer.writerow(['Sentinair Report'])
                writer.writerow(['Report Type', report_type.title()])
                
                if report_type == 'daily':
                    writer.writerow(['Report Date', str(data['report_date'])])
                elif report_type == 'weekly':
                    writer.writerow(['Week Start', str(data['week_start'])])
                    writer.writerow(['Week End', str(data['week_end'])])
                elif report_type == 'incident':
                    writer.writerow(['Generated', str(data['generated_at'])])
                    
                writer.writerow(['Generated By', 'Sentinair v1.0'])
                writer.writerow([])  # Empty row
                
                # Write summary data
                if 'summary' in data:
                    writer.writerow(['SUMMARY'])
                    writer.writerow(['Metric', 'Value'])
                    for key, value in data['summary'].items():
                        writer.writerow([key.replace('_', ' ').title(), value])
                    writer.writerow([])
                    
                # Write alerts data
                if 'alerts' in data and data['alerts']:
                    writer.writerow(['ALERTS'])
                    writer.writerow(['Timestamp', 'Severity', 'Description', 'Confidence'])
                    for alert in data['alerts']:
                        writer.writerow([
                            str(alert.get('timestamp', '')),
                            alert.get('severity', 'Unknown').upper(),
                            alert.get('description', 'No description'),
                            f"{alert.get('confidence', 0) * 100:.1f}%"
                        ])
                    writer.writerow([])
                    
                # Write events data
                if 'events' in data and data['events']:
                    writer.writerow(['EVENTS'])
                    writer.writerow(['Timestamp', 'Type', 'Description', 'Risk Score'])
                    for event in data['events']:
                        writer.writerow([
                            str(event.get('timestamp', '')),
                            event.get('type', 'Unknown'),
                            event.get('description', 'No description'),
                            f"{event.get('risk_score', 0):.2f}"
                        ])
                        
            self.logger.info(f"CSV report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating CSV report: {e}")
            return None
            
    def _create_charts(self, data: Dict[str, Any]) -> List[str]:
        """Create charts for reports"""
        if not MATPLOTLIB_AVAILABLE:
            return []
            
        charts = []
        
        try:
            # Create charts directory
            charts_dir = os.path.join(self.report_dir, 'charts')
            os.makedirs(charts_dir, exist_ok=True)
            
            # Alert severity distribution pie chart
            if 'alerts' in data and data['alerts']:
                severity_counts = {}
                for alert in data['alerts']:
                    severity = alert.get('severity', 'unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                if severity_counts:
                    plt.figure(figsize=(8, 6))
                    plt.pie(severity_counts.values(), labels=severity_counts.keys(), autopct='%1.1f%%')
                    plt.title('Alert Severity Distribution')
                    
                    chart_path = os.path.join(charts_dir, 'severity_distribution.png')
                    plt.savefig(chart_path)
                    plt.close()
                    charts.append(chart_path)
                    
        except Exception as e:
            self.logger.error(f"Error creating charts: {e}")
            
        return charts
        
    def cleanup_old_reports(self, days_to_keep: int = 30):
        """Clean up old report files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for filename in os.listdir(self.report_dir):
                filepath = os.path.join(self.report_dir, filename)
                
                if os.path.isfile(filepath):
                    file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_modified < cutoff_date:
                        os.remove(filepath)
                        self.logger.info(f"Removed old report: {filename}")
                        
        except Exception as e:
            self.logger.error(f"Error cleaning up old reports: {e}")
