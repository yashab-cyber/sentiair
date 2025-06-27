# System Maintenance Guide

This comprehensive guide covers regular maintenance tasks, system updates, health monitoring, and long-term care of Sentinair deployments.

## 🔧 Maintenance Overview

### Maintenance Philosophy
- **Preventive Maintenance**: Regular tasks to prevent issues
- **Predictive Maintenance**: Monitor trends to predict problems
- **Corrective Maintenance**: Fix issues when they occur
- **Adaptive Maintenance**: Adjust system for changing requirements

### Maintenance Categories
1. **Daily Maintenance**: Routine checks and monitoring
2. **Weekly Maintenance**: Performance analysis and cleanup
3. **Monthly Maintenance**: Comprehensive system review
4. **Quarterly Maintenance**: Major updates and assessments
5. **Annual Maintenance**: Strategic planning and major upgrades

## 📅 Maintenance Schedules

### Daily Maintenance Tasks

#### System Health Check
```bash
#!/bin/bash
# maintenance/daily_health_check.sh

echo "=== Sentinair Daily Health Check ==="
echo "Date: $(date)"
echo

# Check if Sentinair is running
if pgrep -f "main.py" > /dev/null; then
    echo "✅ Sentinair is running"
    
    # Get process details
    SENTINAIR_PID=$(pgrep -f "main.py")
    echo "   PID: $SENTINAIR_PID"
    echo "   Uptime: $(ps -o etime= -p $SENTINAIR_PID)"
    
    # Check resource usage
    CPU_USAGE=$(ps -p $SENTINAIR_PID -o %cpu= | awk '{print int($1)}')
    MEM_USAGE=$(ps -p $SENTINAIR_PID -o %mem= | awk '{print int($1)}')
    echo "   CPU Usage: ${CPU_USAGE}%"
    echo "   Memory Usage: ${MEM_USAGE}%"
    
    # Alert if usage is high
    if [ $CPU_USAGE -gt 50 ]; then
        echo "⚠️  WARNING: High CPU usage detected"
    fi
    
    if [ $MEM_USAGE -gt 30 ]; then
        echo "⚠️  WARNING: High memory usage detected"
    fi
    
else
    echo "❌ Sentinair is not running"
    echo "   Attempting to restart..."
    python /opt/sentinair/main.py --daemon &
    sleep 5
    
    if pgrep -f "main.py" > /dev/null; then
        echo "✅ Sentinair restarted successfully"
    else
        echo "❌ Failed to restart Sentinair - manual intervention required"
    fi
fi

# Check log file sizes
echo
echo "📊 Log File Status:"
LOG_DIR="/opt/sentinair/data/logs"
for log_file in "$LOG_DIR"/*.log; do
    if [ -f "$log_file" ]; then
        SIZE=$(du -h "$log_file" | cut -f1)
        echo "   $(basename "$log_file"): $SIZE"
    fi
done

# Check disk space
echo
echo "💾 Disk Space:"
DISK_USAGE=$(df /opt/sentinair | awk 'NR==2 {print $5}' | sed 's/%//')
echo "   Sentinair directory: ${DISK_USAGE}% used"

if [ $DISK_USAGE -gt 90 ]; then
    echo "⚠️  WARNING: Low disk space"
fi

# Check database size
echo
echo "🗃️  Database Status:"
DB_SIZE=$(du -h /opt/sentinair/data/sentinair.db | cut -f1)
echo "   Database size: $DB_SIZE"

# Check for critical alerts
echo
echo "🚨 Recent Critical Alerts:"
python /opt/sentinair/maintenance/check_critical_alerts.py --hours 24

echo
echo "=== Health Check Complete ==="
```

#### Log Monitoring
```python
# maintenance/log_monitor.py
import os
import re
import datetime
from collections import defaultdict

class LogMonitor:
    def __init__(self, log_dir="/opt/sentinair/data/logs"):
        self.log_dir = log_dir
        self.error_patterns = [
            r'ERROR',
            r'CRITICAL',
            r'Exception',
            r'Traceback',
            r'Failed to',
            r'Connection refused',
            r'Permission denied'
        ]
        
    def daily_log_analysis(self):
        """Analyze logs for the past 24 hours"""
        yesterday = datetime.datetime.now() - datetime.timedelta(hours=24)
        
        results = {
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'error_details': defaultdict(int),
            'performance_issues': []
        }
        
        for log_file in os.listdir(self.log_dir):
            if log_file.endswith('.log'):
                self._analyze_log_file(
                    os.path.join(self.log_dir, log_file),
                    yesterday,
                    results
                )
                
        return results
        
    def _analyze_log_file(self, file_path, since_time, results):
        """Analyze a single log file"""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    # Parse timestamp
                    timestamp = self._extract_timestamp(line)
                    if timestamp and timestamp > since_time:
                        
                        # Count log levels
                        if 'ERROR' in line:
                            results['error_count'] += 1
                            error_type = self._extract_error_type(line)
                            results['error_details'][error_type] += 1
                            
                        elif 'WARNING' in line:
                            results['warning_count'] += 1
                            
                        elif 'INFO' in line:
                            results['info_count'] += 1
                            
                        # Check for performance issues
                        if 'slow' in line.lower() or 'timeout' in line.lower():
                            results['performance_issues'].append(line.strip())
                            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
    def generate_daily_report(self):
        """Generate daily log analysis report"""
        analysis = self.daily_log_analysis()
        
        report = []
        report.append("Daily Log Analysis Report")
        report.append("=" * 30)
        report.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
        report.append("")
        
        # Summary
        report.append("Summary:")
        report.append(f"  Errors: {analysis['error_count']}")
        report.append(f"  Warnings: {analysis['warning_count']}")
        report.append(f"  Info messages: {analysis['info_count']}")
        report.append("")
        
        # Error details
        if analysis['error_details']:
            report.append("Error Breakdown:")
            for error_type, count in analysis['error_details'].items():
                report.append(f"  {error_type}: {count}")
            report.append("")
            
        # Performance issues
        if analysis['performance_issues']:
            report.append("Performance Issues:")
            for issue in analysis['performance_issues'][:10]:  # Top 10
                report.append(f"  {issue}")
            report.append("")
            
        return "\n".join(report)

# Run daily log monitoring
if __name__ == "__main__":
    monitor = LogMonitor()
    report = monitor.generate_daily_report()
    print(report)
    
    # Save report
    with open(f"/opt/sentinair/maintenance/reports/daily_log_{datetime.datetime.now().strftime('%Y%m%d')}.txt", 'w') as f:
        f.write(report)
```

### Weekly Maintenance Tasks

#### Performance Analysis
```python
# maintenance/weekly_performance_analysis.py
import sqlite3
import statistics
import datetime
import matplotlib.pyplot as plt
import json

class WeeklyPerformanceAnalysis:
    def __init__(self):
        self.db_path = "/opt/sentinair/data/sentinair.db"
        self.analysis_period = 7  # days
        
    def analyze_weekly_performance(self):
        """Comprehensive weekly performance analysis"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=self.analysis_period)
        
        analysis = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'alerts': self._analyze_alerts(start_date, end_date),
            'events': self._analyze_events(start_date, end_date),
            'performance': self._analyze_performance_metrics(start_date, end_date),
            'ml_model': self._analyze_ml_performance(start_date, end_date),
            'recommendations': []
        }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
        
    def _analyze_alerts(self, start_date, end_date):
        """Analyze alert patterns over the week"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Alert counts by severity
        cursor.execute("""
            SELECT severity, COUNT(*) 
            FROM alerts 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY severity
        """, (start_date.timestamp(), end_date.timestamp()))
        
        severity_counts = dict(cursor.fetchall())
        
        # Alert trends by day
        cursor.execute("""
            SELECT DATE(datetime(timestamp, 'unixepoch')) as alert_date, COUNT(*) 
            FROM alerts 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY alert_date
            ORDER BY alert_date
        """, (start_date.timestamp(), end_date.timestamp()))
        
        daily_trends = dict(cursor.fetchall())
        
        # Top alert categories
        cursor.execute("""
            SELECT category, COUNT(*) 
            FROM alerts 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY category
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """, (start_date.timestamp(), end_date.timestamp()))
        
        top_categories = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_alerts': sum(severity_counts.values()),
            'by_severity': severity_counts,
            'daily_trends': daily_trends,
            'top_categories': top_categories,
            'false_positive_rate': self._calculate_false_positive_rate(start_date, end_date)
        }
        
    def _analyze_performance_metrics(self, start_date, end_date):
        """Analyze system performance metrics"""
        metrics_file = "/opt/sentinair/data/performance_metrics.json"
        
        if not os.path.exists(metrics_file):
            return {'error': 'Performance metrics not available'}
            
        with open(metrics_file, 'r') as f:
            all_metrics = [json.loads(line) for line in f if line.strip()]
            
        # Filter metrics for the analysis period
        period_metrics = [
            m for m in all_metrics 
            if start_date.timestamp() <= m['timestamp'] <= end_date.timestamp()
        ]
        
        if not period_metrics:
            return {'error': 'No metrics available for period'}
            
        # Calculate statistics
        cpu_values = [m['cpu_usage'] for m in period_metrics]
        memory_values = [m['memory_usage'] for m in period_metrics]
        
        return {
            'cpu_usage': {
                'avg': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values),
                'stddev': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
            },
            'memory_usage': {
                'avg': statistics.mean(memory_values),
                'max': max(memory_values),
                'min': min(memory_values),
                'stddev': statistics.stdev(memory_values) if len(memory_values) > 1 else 0
            },
            'throughput': self._calculate_throughput(period_metrics),
            'response_times': self._analyze_response_times(period_metrics)
        }
        
    def generate_weekly_report(self):
        """Generate comprehensive weekly report"""
        analysis = self.analyze_weekly_performance()
        
        report = []
        report.append("Sentinair Weekly Performance Report")
        report.append("=" * 40)
        report.append(f"Period: {analysis['period']['start']} to {analysis['period']['end']}")
        report.append("")
        
        # Alert Analysis
        alerts = analysis['alerts']
        report.append("Alert Analysis:")
        report.append(f"  Total Alerts: {alerts['total_alerts']}")
        report.append("  By Severity:")
        for severity, count in alerts['by_severity'].items():
            report.append(f"    {severity}: {count}")
        report.append(f"  False Positive Rate: {alerts['false_positive_rate']:.2%}")
        report.append("")
        
        # Performance Analysis
        if 'error' not in analysis['performance']:
            perf = analysis['performance']
            report.append("Performance Analysis:")
            report.append(f"  Average CPU Usage: {perf['cpu_usage']['avg']:.1f}%")
            report.append(f"  Peak CPU Usage: {perf['cpu_usage']['max']:.1f}%")
            report.append(f"  Average Memory Usage: {perf['memory_usage']['avg']:.1f}%")
            report.append(f"  Peak Memory Usage: {perf['memory_usage']['max']:.1f}%")
            report.append("")
        
        # Recommendations
        if analysis['recommendations']:
            report.append("Recommendations:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                report.append(f"  {i}. {rec}")
            report.append("")
            
        return "\n".join(report)

# Run weekly analysis
if __name__ == "__main__":
    analyzer = WeeklyPerformanceAnalysis()
    report = analyzer.generate_weekly_report()
    print(report)
    
    # Save report
    week_number = datetime.datetime.now().isocalendar()[1]
    year = datetime.datetime.now().year
    with open(f"/opt/sentinair/maintenance/reports/weekly_performance_{year}_W{week_number:02d}.txt", 'w') as f:
        f.write(report)
```

#### Database Maintenance
```python
# maintenance/database_maintenance.py
import sqlite3
import os
import shutil
import datetime

class DatabaseMaintenance:
    def __init__(self, db_path="/opt/sentinair/data/sentinair.db"):
        self.db_path = db_path
        self.backup_dir = "/opt/sentinair/maintenance/backups"
        
    def weekly_maintenance(self):
        """Perform weekly database maintenance"""
        print("Starting weekly database maintenance...")
        
        # 1. Create backup
        backup_path = self._create_backup()
        print(f"✅ Database backup created: {backup_path}")
        
        # 2. Analyze database
        stats = self._analyze_database()
        print(f"📊 Database analysis complete")
        
        # 3. Optimize database
        self._optimize_database()
        print("🔧 Database optimization complete")
        
        # 4. Clean old data
        cleaned_records = self._clean_old_data()
        print(f"🧹 Cleaned {cleaned_records} old records")
        
        # 5. Update statistics
        self._update_statistics()
        print("📈 Statistics updated")
        
        # 6. Verify integrity
        integrity_ok = self._verify_integrity()
        if integrity_ok:
            print("✅ Database integrity verified")
        else:
            print("❌ Database integrity issues detected")
            
        return {
            'backup_path': backup_path,
            'stats': stats,
            'cleaned_records': cleaned_records,
            'integrity_ok': integrity_ok
        }
        
    def _create_backup(self):
        """Create database backup"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"sentinair_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        os.makedirs(self.backup_dir, exist_ok=True)
        shutil.copy2(self.db_path, backup_path)
        
        return backup_path
        
    def _analyze_database(self):
        """Analyze database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Table sizes
        tables = ['alerts', 'events', 'ml_features', 'file_events', 'usb_events']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                stats[f'{table}_count'] = 0
                
        # Database size
        stats['db_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
        
        # Oldest and newest records
        for table in ['alerts', 'events']:
            try:
                cursor.execute(f"SELECT MIN(timestamp), MAX(timestamp) FROM {table}")
                min_ts, max_ts = cursor.fetchone()
                if min_ts and max_ts:
                    stats[f'{table}_date_range'] = {
                        'oldest': datetime.datetime.fromtimestamp(min_ts).isoformat(),
                        'newest': datetime.datetime.fromtimestamp(max_ts).isoformat()
                    }
            except sqlite3.OperationalError:
                pass
                
        conn.close()
        return stats
        
    def _optimize_database(self):
        """Optimize database performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyze tables
        cursor.execute("ANALYZE")
        
        # Vacuum database
        cursor.execute("VACUUM")
        
        # Reindex
        cursor.execute("REINDEX")
        
        conn.close()
        
    def _clean_old_data(self, retention_days=90):
        """Clean old data based on retention policy"""
        cutoff_time = time.time() - (retention_days * 24 * 3600)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cleaned_count = 0
        
        # Clean old events (keep alerts longer)
        cursor.execute("DELETE FROM events WHERE timestamp < ?", (cutoff_time,))
        cleaned_count += cursor.rowcount
        
        # Clean old ML features
        cursor.execute("DELETE FROM ml_features WHERE timestamp < ?", (cutoff_time,))
        cleaned_count += cursor.rowcount
        
        # Clean acknowledged alerts older than retention period
        alert_cutoff = time.time() - (retention_days * 2 * 24 * 3600)  # Keep alerts twice as long
        cursor.execute("""
            DELETE FROM alerts 
            WHERE timestamp < ? AND status = 'acknowledged'
        """, (alert_cutoff,))
        cleaned_count += cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return cleaned_count
        
    def _verify_integrity(self):
        """Verify database integrity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            return result == "ok"
        except Exception:
            conn.close()
            return False
```

### Monthly Maintenance Tasks

#### System Audit
```bash
#!/bin/bash
# maintenance/monthly_system_audit.sh

echo "=== Monthly Sentinair System Audit ==="
echo "Date: $(date)"
echo

# 1. Security Audit
echo "🔒 Security Audit:"
echo "  Checking file permissions..."
find /opt/sentinair -type f -name "*.py" -not -perm 644 | head -10
find /opt/sentinair -type f -name "*.yaml" -not -perm 600 | head -10

echo "  Checking for suspicious files..."
find /opt/sentinair -name "*.tmp" -o -name "core.*" -o -name "*.pyc" | head -10

echo "  Verifying checksums..."
python /opt/sentinair/maintenance/verify_checksums.py

# 2. Configuration Audit
echo
echo "⚙️  Configuration Audit:"
python /opt/sentinair/maintenance/config_audit.py

# 3. Performance Audit
echo
echo "📊 Performance Audit:"
python /opt/sentinair/maintenance/performance_audit.py

# 4. Storage Audit
echo
echo "💾 Storage Audit:"
echo "  Disk usage by component:"
du -sh /opt/sentinair/data/logs/
du -sh /opt/sentinair/data/models/
du -sh /opt/sentinair/data/reports/
du -sh /opt/sentinair/maintenance/backups/

echo "  Log file rotation status:"
ls -la /opt/sentinair/data/logs/ | grep "$(date +%Y-%m)"

# 5. Update Check
echo
echo "🔄 Update Check:"
python /opt/sentinair/maintenance/check_updates.py

echo
echo "=== Monthly Audit Complete ==="
```

#### Capacity Planning
```python
# maintenance/capacity_planning.py
import os
import sqlite3
import datetime
import numpy as np
from sklearn.linear_model import LinearRegression

class CapacityPlanner:
    def __init__(self):
        self.db_path = "/opt/sentinair/data/sentinair.db"
        self.data_dir = "/opt/sentinair/data"
        
    def analyze_growth_trends(self):
        """Analyze data growth trends for capacity planning"""
        # Database growth
        db_growth = self._analyze_database_growth()
        
        # Log file growth
        log_growth = self._analyze_log_growth()
        
        # Model storage growth
        model_growth = self._analyze_model_storage_growth()
        
        # Overall storage growth
        total_growth = self._analyze_total_storage_growth()
        
        return {
            'database': db_growth,
            'logs': log_growth,
            'models': model_growth,
            'total_storage': total_growth,
            'projections': self._generate_projections()
        }
        
    def _analyze_database_growth(self):
        """Analyze database size growth over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get record counts over time
        cursor.execute("""
            SELECT DATE(datetime(timestamp, 'unixepoch')) as date, COUNT(*) 
            FROM events 
            WHERE timestamp > ?
            GROUP BY date
            ORDER BY date
        """, (time.time() - 30*24*3600,))  # Last 30 days
        
        daily_records = cursor.fetchall()
        conn.close()
        
        if len(daily_records) < 7:
            return {'error': 'Insufficient data for analysis'}
            
        # Calculate growth rate
        dates = [datetime.datetime.strptime(d[0], '%Y-%m-%d') for d in daily_records]
        counts = [d[1] for d in daily_records]
        
        # Linear regression for trend
        X = np.array([(d - dates[0]).days for d in dates]).reshape(-1, 1)
        y = np.array(counts)
        
        model = LinearRegression()
        model.fit(X, y)
        
        daily_growth_rate = model.coef_[0]
        
        return {
            'daily_growth_rate': daily_growth_rate,
            'current_size_mb': os.path.getsize(self.db_path) / (1024 * 1024),
            'projected_size_30_days': self._project_database_size(30),
            'projected_size_90_days': self._project_database_size(90)
        }
        
    def _generate_projections(self):
        """Generate capacity projections"""
        current_total = self._get_total_storage_usage()
        
        # Simple linear projection based on recent growth
        weekly_growth = self._calculate_weekly_growth_rate()
        
        projections = {}
        for period in [30, 60, 90, 180, 365]:
            weeks = period / 7
            projected_size = current_total * (1 + weekly_growth) ** weeks
            projections[f'{period}_days'] = {
                'storage_gb': projected_size / (1024**3),
                'warning_threshold': projected_size > 10 * (1024**3),  # 10GB warning
                'critical_threshold': projected_size > 50 * (1024**3)  # 50GB critical
            }
            
        return projections
        
    def generate_capacity_report(self):
        """Generate capacity planning report"""
        analysis = self.analyze_growth_trends()
        
        report = []
        report.append("Monthly Capacity Planning Report")
        report.append("=" * 35)
        report.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
        report.append("")
        
        # Current usage
        current_usage = self._get_detailed_storage_usage()
        report.append("Current Storage Usage:")
        for component, size in current_usage.items():
            report.append(f"  {component}: {size:.1f} MB")
        report.append("")
        
        # Growth analysis
        if 'error' not in analysis['database']:
            db = analysis['database']
            report.append("Database Growth Analysis:")
            report.append(f"  Current size: {db['current_size_mb']:.1f} MB")
            report.append(f"  Daily growth rate: {db['daily_growth_rate']:.0f} records/day")
            report.append(f"  Projected size (30 days): {db['projected_size_30_days']:.1f} MB")
            report.append("")
        
        # Projections
        projections = analysis['projections']
        report.append("Storage Projections:")
        for period, proj in projections.items():
            days = period.replace('_days', '')
            status = "⚠️ WARNING" if proj['warning_threshold'] else "✅ OK"
            if proj['critical_threshold']:
                status = "🚨 CRITICAL"
            report.append(f"  {days} days: {proj['storage_gb']:.1f} GB {status}")
        report.append("")
        
        # Recommendations
        recommendations = self._generate_capacity_recommendations(analysis)
        if recommendations:
            report.append("Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"  {i}. {rec}")
        
        return "\n".join(report)

# Run capacity planning
if __name__ == "__main__":
    planner = CapacityPlanner()
    report = planner.generate_capacity_report()
    print(report)
    
    # Save report
    month_year = datetime.datetime.now().strftime("%Y_%m")
    with open(f"/opt/sentinair/maintenance/reports/capacity_planning_{month_year}.txt", 'w') as f:
        f.write(report)
```

## 🔄 Update Management

### Update Process

#### Update Checker
```python
# maintenance/update_checker.py
import json
import hashlib
import subprocess
import os

class UpdateChecker:
    def __init__(self):
        self.current_version = self._get_current_version()
        self.update_info_file = "/opt/sentinair/maintenance/update_info.json"
        
    def check_for_updates(self, update_source="local"):
        """Check for available updates"""
        if update_source == "local":
            return self._check_local_updates()
        else:
            # For air-gapped environments, updates come via removable media
            return self._check_removable_media_updates()
            
    def _check_local_updates(self):
        """Check for locally staged updates"""
        update_dir = "/opt/sentinair/updates"
        if not os.path.exists(update_dir):
            return {'updates_available': False}
            
        available_updates = []
        for update_file in os.listdir(update_dir):
            if update_file.endswith('.update'):
                update_info = self._parse_update_file(
                    os.path.join(update_dir, update_file)
                )
                if self._is_newer_version(update_info['version']):
                    available_updates.append(update_info)
                    
        return {
            'updates_available': len(available_updates) > 0,
            'available_updates': available_updates,
            'current_version': self.current_version
        }
        
    def apply_update(self, update_file):
        """Apply a specific update"""
        print(f"Applying update: {update_file}")
        
        # 1. Verify update integrity
        if not self._verify_update_integrity(update_file):
            raise Exception("Update integrity verification failed")
            
        # 2. Create backup
        backup_path = self._create_pre_update_backup()
        print(f"Backup created: {backup_path}")
        
        # 3. Stop Sentinair
        self._stop_sentinair()
        
        try:
            # 4. Apply update
            self._extract_update(update_file)
            
            # 5. Run update scripts
            self._run_update_scripts()
            
            # 6. Verify installation
            if not self._verify_installation():
                raise Exception("Post-update verification failed")
                
            # 7. Start Sentinair
            self._start_sentinair()
            
            print("Update applied successfully")
            return True
            
        except Exception as e:
            print(f"Update failed: {e}")
            print("Rolling back to previous version...")
            self._rollback_update(backup_path)
            self._start_sentinair()
            raise
            
    def _verify_update_integrity(self, update_file):
        """Verify update file integrity"""
        # Check file signature/checksum
        expected_hash = self._get_expected_hash(update_file)
        actual_hash = self._calculate_file_hash(update_file)
        
        return expected_hash == actual_hash
        
    def _create_pre_update_backup(self):
        """Create backup before applying update"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"/opt/sentinair/maintenance/backups/pre_update_{timestamp}"
        
        # Copy critical files
        critical_paths = [
            "/opt/sentinair/config/",
            "/opt/sentinair/data/sentinair.db",
            "/opt/sentinair/signatures/",
            "/opt/sentinair/main.py"
        ]
        
        os.makedirs(backup_dir, exist_ok=True)
        
        for path in critical_paths:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.copytree(path, os.path.join(backup_dir, os.path.basename(path)))
                else:
                    shutil.copy2(path, backup_dir)
                    
        return backup_dir

# Automated update application
def apply_pending_updates():
    """Apply any pending updates"""
    checker = UpdateChecker()
    updates = checker.check_for_updates()
    
    if updates['updates_available']:
        for update in updates['available_updates']:
            if update['auto_apply']:
                try:
                    checker.apply_update(update['file_path'])
                    print(f"Successfully applied update: {update['version']}")
                except Exception as e:
                    print(f"Failed to apply update {update['version']}: {e}")
```

## 📊 Health Monitoring

### Automated Health Monitoring
```python
# maintenance/health_monitor.py
import psutil
import sqlite3
import time
import json
import smtplib
from email.mime.text import MIMEText

class HealthMonitor:
    def __init__(self):
        self.thresholds = {
            'cpu_usage': 80,
            'memory_usage': 85,
            'disk_usage': 90,
            'response_time': 5.0,
            'error_rate': 0.1
        }
        
        self.health_history = []
        
    def check_system_health(self):
        """Comprehensive system health check"""
        health_status = {
            'timestamp': time.time(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # System resource checks
        health_status['checks']['cpu'] = self._check_cpu_usage()
        health_status['checks']['memory'] = self._check_memory_usage()
        health_status['checks']['disk'] = self._check_disk_usage()
        
        # Application health checks
        health_status['checks']['process'] = self._check_sentinair_process()
        health_status['checks']['database'] = self._check_database_health()
        health_status['checks']['response_time'] = self._check_response_time()
        
        # Service health checks
        health_status['checks']['monitoring'] = self._check_monitoring_services()
        health_status['checks']['log_rotation'] = self._check_log_rotation()
        
        # Determine overall status
        failed_checks = [
            check for check, result in health_status['checks'].items()
            if result['status'] != 'ok'
        ]
        
        if failed_checks:
            if any(health_status['checks'][check]['severity'] == 'critical' for check in failed_checks):
                health_status['overall_status'] = 'critical'
            else:
                health_status['overall_status'] = 'warning'
                
        # Store health history
        self.health_history.append(health_status)
        if len(self.health_history) > 100:  # Keep last 100 checks
            self.health_history.pop(0)
            
        return health_status
        
    def _check_sentinair_process(self):
        """Check if Sentinair process is running properly"""
        try:
            # Find Sentinair process
            sentinair_processes = [
                p for p in psutil.process_iter(['pid', 'name', 'cmdline'])
                if any('main.py' in str(cmd) for cmd in p.info['cmdline'])
            ]
            
            if not sentinair_processes:
                return {
                    'status': 'critical',
                    'message': 'Sentinair process not running',
                    'severity': 'critical'
                }
                
            process = psutil.Process(sentinair_processes[0].info['pid'])
            
            # Check process health
            cpu_percent = process.cpu_percent()
            memory_percent = process.memory_percent()
            
            if cpu_percent > 90:
                return {
                    'status': 'warning',
                    'message': f'High CPU usage: {cpu_percent:.1f}%',
                    'severity': 'warning'
                }
                
            if memory_percent > 50:
                return {
                    'status': 'warning',
                    'message': f'High memory usage: {memory_percent:.1f}%',
                    'severity': 'warning'
                }
                
            return {
                'status': 'ok',
                'message': 'Process running normally',
                'details': {
                    'pid': process.pid,
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error checking process: {e}',
                'severity': 'warning'
            }
            
    def generate_health_report(self):
        """Generate comprehensive health report"""
        current_health = self.check_system_health()
        
        report = []
        report.append("Sentinair Health Report")
        report.append("=" * 25)
        report.append(f"Timestamp: {datetime.datetime.now()}")
        report.append(f"Overall Status: {current_health['overall_status'].upper()}")
        report.append("")
        
        # Individual check results
        report.append("Health Check Results:")
        for check_name, result in current_health['checks'].items():
            status_icon = {
                'ok': '✅',
                'warning': '⚠️',
                'critical': '🚨',
                'error': '❌'
            }.get(result['status'], '❓')
            
            report.append(f"  {status_icon} {check_name.title()}: {result['message']}")
            
        # Historical trends
        if len(self.health_history) > 1:
            report.append("")
            report.append("Recent Trends:")
            recent_statuses = [h['overall_status'] for h in self.health_history[-10:]]
            healthy_count = recent_statuses.count('healthy')
            warning_count = recent_statuses.count('warning')
            critical_count = recent_statuses.count('critical')
            
            report.append(f"  Last 10 checks - Healthy: {healthy_count}, Warning: {warning_count}, Critical: {critical_count}")
            
        return "\n".join(report)

# Continuous health monitoring
def start_health_monitoring():
    """Start continuous health monitoring"""
    monitor = HealthMonitor()
    
    while True:
        try:
            health_status = monitor.check_system_health()
            
            # Log health status
            with open("/opt/sentinair/data/logs/health_monitor.log", "a") as f:
                f.write(f"{json.dumps(health_status)}\n")
                
            # Alert on critical issues
            if health_status['overall_status'] == 'critical':
                print("CRITICAL: Sentinair health issues detected!")
                # Could trigger alerts here
                
            time.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            print(f"Health monitoring error: {e}")
            time.sleep(60)  # Retry in 1 minute

if __name__ == "__main__":
    start_health_monitoring()
```

## 📋 Maintenance Checklist

### Daily Maintenance
- [ ] Check system status and uptime
- [ ] Review critical alerts
- [ ] Monitor resource usage
- [ ] Verify log rotation
- [ ] Check disk space
- [ ] Validate backup completion

### Weekly Maintenance
- [ ] Analyze performance trends
- [ ] Review alert accuracy
- [ ] Clean temporary files
- [ ] Update virus signatures
- [ ] Test backup restoration
- [ ] Review false positive rate

### Monthly Maintenance
- [ ] Full system audit
- [ ] Capacity planning analysis
- [ ] Security assessment
- [ ] Configuration review
- [ ] Update documentation
- [ ] Performance optimization

### Quarterly Maintenance
- [ ] Major system updates
- [ ] Hardware assessment
- [ ] Security policy review
- [ ] Disaster recovery testing
- [ ] Training updates
- [ ] Strategic planning review

## ⚠️ Maintenance Best Practices

### Preventive Measures
- **Regular Monitoring**: Continuously monitor system health
- **Automated Tasks**: Automate routine maintenance tasks
- **Documentation**: Keep maintenance logs and procedures
- **Testing**: Test all maintenance procedures regularly
- **Backup Verification**: Always verify backup integrity

### Corrective Actions
- **Issue Tracking**: Track and document all issues
- **Root Cause Analysis**: Investigate underlying causes
- **Preventive Measures**: Implement measures to prevent recurrence
- **Knowledge Base**: Maintain a knowledge base of solutions
- **Escalation Procedures**: Have clear escalation paths

---

**Next Steps:**
- [API Reference](16-api-reference.md) - API for maintenance automation
- [Configuration Reference](17-config-reference.md) - Maintenance configuration options
- [Troubleshooting](13-troubleshooting.md) - Maintenance troubleshooting guide
