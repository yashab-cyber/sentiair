# GUI User Guide

Complete guide to using Sentinair's graphical user interface for desktop monitoring and management.

## 🖥️ Getting Started with GUI

### Launching GUI Mode
```bash
cd /opt/sentinair
python main.py --mode gui
```

### First Launch
When you first launch the GUI, you'll see:
1. **Main Dashboard** - System overview and status
2. **Setup Wizard** (first time only) - Basic configuration
3. **Training Data Prompt** - Generate initial training data if needed

## 📊 Main Dashboard

### Dashboard Layout
```
┌─────────────────┬─────────────────────────────────┐
│   Navigation    │         Main Content Area       │
│   Sidebar       │                                 │
│                 │  ┌─────────────┬─────────────┐   │
│ • Dashboard     │  │   Status    │   Alerts    │   │
│ • Alerts        │  │   Panel     │   Panel     │   │
│ • Monitoring    │  └─────────────┴─────────────┘   │
│ • Reports       │                                 │
│ • Settings      │  ┌─────────────────────────────┐ │
│ • Help          │  │     Real-time Charts        │ │
│                 │  └─────────────────────────────┘ │
└─────────────────┴─────────────────────────────────┘
```

### Status Panel
- **System Status**: Running/Stopped indicator
- **Monitoring Active**: Real-time monitoring status
- **Model Status**: AI model training state
- **Events Today**: Count of events processed
- **Alerts**: Active and recent alerts count
- **Last Update**: Timestamp of last system update

### Quick Actions
- **Start/Stop Monitoring**: Toggle system monitoring
- **Generate Report**: Create instant security report
- **Train Model**: Manually trigger AI training
- **View Logs**: Open log viewer
- **Emergency Stop**: Immediate system shutdown

## 🚨 Alerts Management

### Alerts Dashboard
Access via **Navigation → Alerts** or **Dashboard → Alerts Panel**

#### Alert List View
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 [Search/Filter] 📅 [Date Range] 🏷️ [Severity] [Clear]   │
├─────────────────────────────────────────────────────────────┤
│ 🔴 CRITICAL | 2025-06-27 10:15 | Suspicious Process      │▶│
│ 🟡 MEDIUM   | 2025-06-27 09:30 | File Access Anomaly    │▶│
│ 🟢 LOW      | 2025-06-27 08:45 | USB Device Connected   │▶│
└─────────────────────────────────────────────────────────────┘
```

#### Alert Details View
Click any alert to see:
- **Event Information**: Time, type, severity
- **Technical Details**: File paths, process names, IDs
- **Risk Assessment**: ML confidence score, indicators
- **Context**: Related events, user actions
- **Actions**: Acknowledge, whitelist, investigate

### Alert Actions
- **Acknowledge**: Mark alert as reviewed
- **Whitelist**: Add to whitelist to prevent future alerts
- **Block**: Block the detected entity (file, process, etc.)
- **Investigate**: Open detailed analysis view
- **Export**: Save alert details to file

### Alert Filters
- **Severity**: Critical, High, Medium, Low
- **Type**: Process, File, USB, Behavior, Custom
- **Status**: New, Acknowledged, Resolved
- **Date Range**: Last hour, day, week, month, custom
- **Source**: Specific monitoring modules

## 📈 Real-time Monitoring

### Monitoring Dashboard
Access via **Navigation → Monitoring**

#### Process Monitor View
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Process Activity (Last 1 Hour)                          │
├─────────────────────────────────────────────────────────────┤
│    ▁▁▂▃▅▅▇██▇▅▃▂▁▁    Process Starts                      │
│    ▁▁▁▂▃▄▅▆▇▇▆▅▄▃▂    Process Stops                       │
├─────────────────────────────────────────────────────────────┤
│ 🟢 firefox     | PID: 1234 | User: user    | Normal       │
│ 🟡 unknown.exe | PID: 5678 | User: root    | Suspicious   │
│ 🔴 malware.bin | PID: 9999 | User: admin   | BLOCKED      │
└─────────────────────────────────────────────────────────────┘
```

#### File Monitor View
```
┌─────────────────────────────────────────────────────────────┐
│ 📁 File Activity (Real-time)                               │
├─────────────────────────────────────────────────────────────┤
│ 📝 /home/user/document.txt     | READ  | user  | 10:15:30  │
│ 🔒 /etc/passwd                 | READ  | root  | 10:15:25  │
│ ⚠️  /tmp/suspicious.exe         | WRITE | admin | 10:15:20  │
└─────────────────────────────────────────────────────────────┘
```

#### USB Monitor View
```
┌─────────────────────────────────────────────────────────────┐
│ 🔌 USB Device Activity                                      │
├─────────────────────────────────────────────────────────────┤
│ 🟢 Kingston USB Drive    | Connected   | 10:10:15          │
│ 🟡 Unknown Device        | Connected   | 10:05:30          │
│ 🔴 Blocked Device        | Blocked     | 09:30:45          │
└─────────────────────────────────────────────────────────────┘
```

### Real-time Charts
- **Activity Timeline**: Events over time
- **Risk Score Trend**: ML risk assessment over time
- **Resource Usage**: CPU, memory, disk I/O
- **Network Activity**: Connections, traffic (future)

## 📋 Reports and Analytics

### Report Generator
Access via **Navigation → Reports**

#### Report Types
1. **Security Summary**: Overall security posture
2. **Threat Analysis**: Detailed threat breakdown
3. **Activity Report**: System activity summary
4. **Compliance Report**: Regulatory compliance status
5. **Custom Report**: User-defined parameters

#### Report Configuration
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Generate Security Report                                 │
├─────────────────────────────────────────────────────────────┤
│ Report Type: [Security Summary      ▼]                     │
│ Date Range:  [Last 7 Days          ▼]                     │
│ Format:      [PDF ▼] [CSV ▼] [JSON ▼]                     │
│ Include:     ☑ Charts  ☑ Details  ☑ Recommendations       │
│ Email To:    [admin@company.com                    ]       │
│                                                             │
│ [Generate Report] [Schedule Report] [Cancel]               │
└─────────────────────────────────────────────────────────────┘
```

### Analytics Dashboard
- **Trend Analysis**: Security trends over time
- **Pattern Recognition**: Recurring security patterns
- **Risk Metrics**: Risk scores and distributions
- **Performance Metrics**: System performance impact

## ⚙️ Settings and Configuration

### Settings Panel
Access via **Navigation → Settings** or **Dashboard → Settings**

#### General Settings
```
┌─────────────────────────────────────────────────────────────┐
│ ⚙️ General Settings                                         │
├─────────────────────────────────────────────────────────────┤
│ Monitoring:                                                 │
│   ☑ File Monitoring        Check Interval: [5     ] sec    │
│   ☑ Process Monitoring     ☑ Auto-start on boot           │
│   ☑ USB Monitoring         ☑ Hide in system tray          │
│                                                             │
│ Notifications:                                              │
│   ☑ Desktop notifications  ☑ Sound alerts                 │
│   ☑ Email notifications    ☑ System tray alerts           │
│                                                             │
│ [Save Settings] [Reset to Defaults] [Export Config]        │
└─────────────────────────────────────────────────────────────┘
```

#### Advanced Settings
- **ML Configuration**: Model parameters, training settings
- **Database Settings**: Storage limits, cleanup policies
- **Security Settings**: Encryption, access control
- **Performance Settings**: Resource usage optimization

### Configuration Import/Export
- **Export**: Save current configuration to file
- **Import**: Load configuration from file
- **Reset**: Restore default settings
- **Backup**: Create configuration backup

## 🤖 Machine Learning Management

### ML Dashboard
Access via **Settings → Machine Learning**

#### Model Status
```
┌─────────────────────────────────────────────────────────────┐
│ 🧠 Machine Learning Status                                  │
├─────────────────────────────────────────────────────────────┤
│ Model Type:      Isolation Forest                          │
│ Training Status: ✅ Trained                                 │
│ Last Training:   2025-06-27 08:00:00                       │
│ Training Data:   15,847 events                             │
│ Model Accuracy:  94.2%                                     │
│ False Positives: 2.1%                                      │
│                                                             │
│ [Retrain Model] [Download Model] [View Analytics]          │
└─────────────────────────────────────────────────────────────┘
```

#### Training Data Management
- **View Training Data**: Browse training dataset
- **Add Training Data**: Include custom training examples
- **Data Quality**: Check training data quality
- **Feature Analysis**: Understand model features

### Model Configuration
- **Algorithm Selection**: Choose ML algorithm
- **Hyperparameters**: Tune model parameters
- **Feature Selection**: Enable/disable features
- **Validation**: Cross-validation settings

## 🔒 Security Features

### Access Control
- **User Authentication**: Login/logout functionality
- **Session Management**: Automatic session timeout
- **Role-based Access**: Different permission levels
- **Audit Logging**: Track user actions

### Stealth Mode Control
```
┌─────────────────────────────────────────────────────────────┐
│ 🕵️ Stealth Mode Configuration                               │
├─────────────────────────────────────────────────────────────┤
│ Status: ⚫ Disabled                                         │
│ Secret Key: [********************************]              │
│ Hide Process: ☑ Yes                                        │
│ Fake Name: [system_update              ]                   │
│                                                             │
│ ⚠️ Warning: Stealth mode hides Sentinair from process      │
│    lists and task managers. Use responsibly.               │
│                                                             │
│ [Enable Stealth Mode] [Test Settings] [Cancel]             │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 System Tools

### Log Viewer
- **Real-time Logs**: Live log streaming
- **Log Filtering**: Filter by level, module, time
- **Log Search**: Search log content
- **Log Export**: Export logs to file

### Database Management
- **Database Statistics**: Size, events, performance
- **Data Cleanup**: Remove old data
- **Database Backup**: Create/restore backups
- **Database Repair**: Fix corruption issues

### System Information
- **System Status**: Overall health check
- **Resource Usage**: CPU, memory, disk usage
- **Version Information**: Software versions
- **License Information**: License status

## 🎨 Customization

### Theme Selection
- **Dark Theme**: Low-light environments
- **Light Theme**: Standard desktop use
- **High Contrast**: Accessibility mode
- **Custom Theme**: User-defined colors

### Dashboard Layout
- **Widget Arrangement**: Drag-and-drop layout
- **Panel Sizes**: Resize dashboard panels
- **Chart Types**: Select preferred chart styles
- **Update Frequency**: Customize refresh rates

### Keyboard Shortcuts
- **Ctrl+M**: Start/Stop monitoring
- **Ctrl+A**: View all alerts
- **Ctrl+R**: Generate report
- **Ctrl+S**: Open settings
- **F5**: Refresh dashboard
- **Esc**: Close current dialog

## 🆘 Help and Support

### Built-in Help
- **Help Menu**: Comprehensive help system
- **Tooltips**: Hover help for all controls
- **Getting Started**: Interactive tutorials
- **Video Guides**: Built-in video tutorials

### Troubleshooting
- **System Diagnostics**: Automated health checks
- **Error Reporting**: Send error reports
- **Log Analysis**: Automatic log analysis
- **Support Information**: Contact and support details

### Updates and Maintenance
- **Update Checker**: Check for new versions
- **Automatic Updates**: Enable/disable auto-updates
- **Maintenance Mode**: System maintenance tools
- **Performance Monitor**: Track system performance

---

**Previous**: [Configuration](03-configuration.md) | **Next**: [CLI User Guide](05-cli-guide.md)
