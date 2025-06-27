# Custom Rules and Detection Signatures

This guide covers creating custom YARA rules, detection signatures, and behavioral patterns to enhance Sentinair's threat detection capabilities for your specific environment.

## 🎯 Overview

Custom rules allow you to:
- **Tailor Detection**: Customize threat detection for your specific environment
- **Reduce False Positives**: Fine-tune rules to minimize noise
- **Add New Threats**: Create detection for emerging or environment-specific threats
- **Enhance Coverage**: Add detection for industry-specific attack patterns
- **Behavioral Rules**: Define custom behavioral anomaly patterns

## 📝 YARA Rules

### YARA Rule Basics

#### Rule Structure
```yara
rule RuleName {
    meta:
        description = "Rule description"
        author = "Your Name"
        date = "2025-06-27"
        severity = "high"
        category = "malware"
        
    strings:
        $string1 = "suspicious string"
        $hex1 = { 4D 5A }  // PE header
        $regex1 = /evil.*pattern/i
        
    condition:
        $string1 or ($hex1 at 0 and $regex1)
}
```

#### Rule Categories
```yara
// signatures/categories/malware.yar
rule Malware_Generic_Dropper {
    meta:
        description = "Generic malware dropper pattern"
        category = "malware"
        severity = "critical"
        
    strings:
        $drop1 = "CreateFileA"
        $drop2 = "WriteFile"
        $drop3 = "CloseHandle"
        $url = /https?:\/\/[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/
        
    condition:
        all of ($drop*) and $url
}

// signatures/categories/persistence.yar
rule Persistence_Registry_Modification {
    meta:
        description = "Registry modification for persistence"
        category = "persistence"
        severity = "high"
        
    strings:
        $reg1 = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
        $reg2 = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        $reg3 = "RegSetValueEx"
        
    condition:
        any of ($reg*)
}
```

### File-Based Detection Rules

#### Executable Analysis Rules
```yara
// signatures/file_analysis.yar
rule Suspicious_Executable_Packed {
    meta:
        description = "Detects packed or obfuscated executables"
        severity = "medium"
        
    strings:
        $upx = "UPX"
        $packed1 = { 60 BE ?? ?? ?? ?? 8D BE ?? ?? ?? ?? }
        $packed2 = "This program cannot be run in DOS mode"
        
    condition:
        uint16(0) == 0x5A4D and  // PE header
        ($upx or $packed1 or $packed2) and
        filesize < 10MB
}

rule Suspicious_File_Extension_Mismatch {
    meta:
        description = "File extension doesn't match content"
        severity = "high"
        
    strings:
        $pe_header = { 4D 5A }
        $elf_header = { 7F 45 4C 46 }
        
    condition:
        // PE file with non-exe extension
        ($pe_header at 0 and filename matches /\.(txt|doc|pdf|jpg)$/i) or
        // ELF file with suspicious extension
        ($elf_header at 0 and filename matches /\.(txt|pdf|jpg)$/i)
}
```

#### Document-Based Rules
```yara
// signatures/document_threats.yar
rule Malicious_Office_Macro {
    meta:
        description = "Office document with suspicious macro"
        severity = "high"
        
    strings:
        $macro1 = "Auto_Open"
        $macro2 = "Document_Open"
        $macro3 = "Shell"
        $macro4 = "CreateObject"
        $vba = "VBA"
        
    condition:
        ($vba and any of ($macro*)) and
        filesize < 50MB
}

rule Suspicious_PDF_JavaScript {
    meta:
        description = "PDF with suspicious JavaScript"
        severity = "medium"
        
    strings:
        $pdf = "%PDF"
        $js1 = "/JavaScript"
        $js2 = "/JS"
        $suspicious1 = "eval("
        $suspicious2 = "unescape("
        
    condition:
        $pdf at 0 and
        ($js1 or $js2) and
        any of ($suspicious*)
}
```

### Network-Based Rules (for environments with network monitoring)

#### Network Traffic Patterns
```yara
// signatures/network_patterns.yar
rule Suspicious_HTTP_User_Agent {
    meta:
        description = "Suspicious HTTP User-Agent strings"
        severity = "medium"
        
    strings:
        $ua1 = "User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"
        $ua2 = "User-Agent: wget"
        $ua3 = "User-Agent: curl"
        $ua4 = "User-Agent: python-requests"
        
    condition:
        any of them
}

rule Data_Exfiltration_Pattern {
    meta:
        description = "Potential data exfiltration via HTTP POST"
        severity = "critical"
        
    strings:
        $post = "POST"
        $large_data = { [100-500] }  // Large data block
        $suspicious_headers = "Content-Length: 10"
        
    condition:
        $post and $large_data and
        filesize > 1MB
}
```

## 🔄 Behavioral Detection Rules

### User Behavior Rules

#### Custom Behavioral Patterns
```python
# behavioral/custom_patterns.py
class CustomBehaviorPattern:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.rules = []
        
    def add_rule(self, condition, threshold, timeframe):
        self.rules.append({
            'condition': condition,
            'threshold': threshold,
            'timeframe': timeframe
        })

# Example: Rapid file access pattern
rapid_file_access = CustomBehaviorPattern(
    "Rapid File Access",
    "Detects unusually rapid file access patterns"
)

rapid_file_access.add_rule(
    condition="file_access_count > threshold",
    threshold=100,
    timeframe="60s"
)

# Example: Unusual working hours
unusual_hours = CustomBehaviorPattern(
    "Unusual Working Hours",
    "Detects activity outside normal business hours"
)

unusual_hours.add_rule(
    condition="activity_time not in business_hours",
    threshold=1,
    timeframe="1h"
)
```

#### Advanced Behavioral Rules
```yaml
# config/behavioral_rules.yaml
behavioral_rules:
  file_access_patterns:
    mass_file_access:
      description: "Accessing many files quickly"
      threshold: 50
      timeframe: "2m"
      severity: "high"
      
    sensitive_file_enumeration:
      description: "Systematic access to sensitive files"
      patterns:
        - "/etc/*"
        - "C:\\Windows\\System32\\*"
        - "*.config"
      threshold: 10
      timeframe: "5m"
      severity: "critical"
      
  usb_patterns:
    rapid_usb_usage:
      description: "Multiple USB insertions/removals"
      threshold: 5
      timeframe: "10m"
      severity: "medium"
      
    large_usb_transfer:
      description: "Large data transfer to USB"
      size_threshold: "100MB"
      timeframe: "5m"
      severity: "high"
      
  process_patterns:
    process_injection:
      description: "Process injection techniques"
      indicators:
        - "CreateRemoteThread"
        - "WriteProcessMemory"
        - "VirtualAllocEx"
      threshold: 2
      timeframe: "1m"
      severity: "critical"
```

### System Behavior Rules

#### File System Behavior
```python
# behavioral/filesystem_rules.py
class FileSystemBehaviorRule:
    def __init__(self):
        self.patterns = {
            'mass_file_creation': {
                'threshold': 100,
                'timeframe': 300,  # 5 minutes
                'severity': 'high'
            },
            'system_file_modification': {
                'protected_paths': [
                    '/etc/',
                    '/bin/',
                    '/sbin/',
                    'C:\\Windows\\System32\\'
                ],
                'severity': 'critical'
            },
            'encryption_activity': {
                'patterns': ['.locked', '.encrypted', '.crypto'],
                'threshold': 10,
                'severity': 'critical'
            }
        }
        
    def evaluate_file_event(self, event):
        for rule_name, rule_config in self.patterns.items():
            if self.check_rule(rule_name, rule_config, event):
                return self.create_alert(rule_name, event)
```

## 🛠️ Rule Management

### Rule Development Process

#### 1. Rule Creation Template
```yara
// templates/rule_template.yar
rule Template_Rule_Name {
    meta:
        description = "Brief description of what this rule detects"
        author = "Rule author name"
        date = "YYYY-MM-DD"
        version = "1.0"
        severity = "low|medium|high|critical"
        category = "malware|persistence|exfiltration|reconnaissance"
        confidence = "low|medium|high"
        environment = "all|windows|linux|specific"
        
    strings:
        // Define your detection strings here
        $string1 = "example string"
        $hex1 = { 41 42 43 44 }
        $regex1 = /pattern.*match/i
        
    condition:
        // Define your detection logic here
        any of them
}
```

#### 2. Rule Testing Framework
```python
# testing/rule_tester.py
class YaraRuleTester:
    def __init__(self):
        self.test_cases = []
        self.false_positives = []
        
    def add_test_case(self, file_path, should_match=True):
        self.test_cases.append({
            'file': file_path,
            'expected': should_match
        })
        
    def test_rule(self, rule_path):
        results = {
            'passed': 0,
            'failed': 0,
            'false_positives': 0,
            'false_negatives': 0
        }
        
        # Load rule
        rule = yara.compile(filepath=rule_path)
        
        for test_case in self.test_cases:
            matches = rule.match(test_case['file'])
            
            if bool(matches) == test_case['expected']:
                results['passed'] += 1
            else:
                results['failed'] += 1
                if matches and not test_case['expected']:
                    results['false_positives'] += 1
                elif not matches and test_case['expected']:
                    results['false_negatives'] += 1
                    
        return results

# Usage example
tester = YaraRuleTester()
tester.add_test_case('samples/malware.exe', True)
tester.add_test_case('samples/clean.exe', False)
results = tester.test_rule('signatures/my_rule.yar')
```

### Rule Validation and Testing

#### Automated Rule Testing
```bash
#!/bin/bash
# scripts/test_rules.sh

echo "Testing YARA Rules..."

# Test all rules against clean files (should not match)
for rule in signatures/*.yar; do
    echo "Testing $rule against clean samples..."
    yara "$rule" samples/clean/* 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "WARNING: $rule matched clean files"
    fi
done

# Test rules against malware samples (should match)
for rule in signatures/*.yar; do
    echo "Testing $rule against malware samples..."
    matches=$(yara "$rule" samples/malware/* 2>/dev/null | wc -l)
    echo "$rule: $matches matches"
done

echo "Rule testing completed"
```

#### Rule Performance Testing
```python
# testing/performance_test.py
import time
import yara

def test_rule_performance(rule_path, test_files):
    rule = yara.compile(filepath=rule_path)
    
    start_time = time.time()
    total_matches = 0
    
    for file_path in test_files:
        matches = rule.match(file_path)
        total_matches += len(matches)
    
    end_time = time.time()
    
    return {
        'execution_time': end_time - start_time,
        'files_processed': len(test_files),
        'total_matches': total_matches,
        'files_per_second': len(test_files) / (end_time - start_time)
    }
```

## 📊 Rule Management Interface

### Rule Configuration GUI
```python
# gui/rule_manager.py
class RuleManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Rule list
        self.rule_list = QListWidget()
        self.load_rules()
        
        # Rule editor
        self.rule_editor = QTextEdit()
        self.rule_editor.setFont(QFont("Courier"))
        
        # Buttons
        button_layout = QHBoxLayout()
        self.new_button = QPushButton("New Rule")
        self.save_button = QPushButton("Save Rule")
        self.test_button = QPushButton("Test Rule")
        self.delete_button = QPushButton("Delete Rule")
        
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.test_button)
        button_layout.addWidget(self.delete_button)
        
        # Connect signals
        self.new_button.clicked.connect(self.new_rule)
        self.save_button.clicked.connect(self.save_rule)
        self.test_button.clicked.connect(self.test_rule)
        
        layout.addWidget(self.rule_list)
        layout.addWidget(self.rule_editor)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
```

### CLI Rule Management
```bash
# Rule management commands
python main.py --rule-manager

# List all rules
python main.py --list-rules

# Add new rule
python main.py --add-rule --file my_rule.yar

# Test rule
python main.py --test-rule --rule my_rule.yar --samples /path/to/samples/

# Enable/disable rule
python main.py --enable-rule my_rule
python main.py --disable-rule my_rule

# Update rule
python main.py --update-rule --rule my_rule.yar --file updated_rule.yar
```

## 🔧 Advanced Rule Techniques

### Multi-Stage Rules
```yara
// Advanced multi-stage detection
rule Advanced_APT_Chain {
    meta:
        description = "Multi-stage APT attack chain"
        severity = "critical"
        
    strings:
        // Stage 1: Initial infection
        $stage1_a = "wininet.dll"
        $stage1_b = "InternetOpenA"
        
        // Stage 2: Persistence
        $stage2_a = "RegSetValueEx"
        $stage2_b = "HKEY_LOCAL_MACHINE"
        
        // Stage 3: Data collection
        $stage3_a = "FindFirstFileA"
        $stage3_b = "CryptEncrypt"
        
        // Stage 4: Exfiltration
        $stage4_a = "send"
        $stage4_b = "HttpSendRequest"
        
    condition:
        // Must have elements from at least 3 stages
        (($stage1_a and $stage1_b) and
         ($stage2_a and $stage2_b) and
         ($stage3_a and $stage3_b)) or
        (($stage1_a and $stage1_b) and
         ($stage3_a and $stage3_b) and
         ($stage4_a and $stage4_b))
}
```

### Environment-Specific Rules
```yara
// signatures/environment_specific.yar
rule Banking_Environment_Threat {
    meta:
        description = "Banking environment specific threats"
        environment = "banking"
        severity = "critical"
        
    strings:
        $banking1 = "swift"
        $banking2 = "ach"
        $banking3 = "wire transfer"
        $financial1 = "account balance"
        $financial2 = "transaction"
        
    condition:
        any of ($banking*) and any of ($financial*)
}

rule Industrial_Control_Threat {
    meta:
        description = "Industrial control system threats"
        environment = "industrial"
        severity = "critical"
        
    strings:
        $scada1 = "modbus"
        $scada2 = "dnp3"
        $scada3 = "profinet"
        $plc1 = "ladder logic"
        $plc2 = "function block"
        
    condition:
        any of them
}
```

## 📈 Rule Analytics and Optimization

### Rule Performance Metrics
```python
# analytics/rule_analytics.py
class RuleAnalytics:
    def __init__(self):
        self.metrics = {}
        
    def track_rule_performance(self, rule_name, execution_time, matches):
        if rule_name not in self.metrics:
            self.metrics[rule_name] = {
                'total_executions': 0,
                'total_time': 0,
                'total_matches': 0,
                'false_positives': 0
            }
            
        self.metrics[rule_name]['total_executions'] += 1
        self.metrics[rule_name]['total_time'] += execution_time
        self.metrics[rule_name]['total_matches'] += matches
        
    def get_slow_rules(self, threshold=0.1):
        slow_rules = []
        for rule_name, metrics in self.metrics.items():
            avg_time = metrics['total_time'] / metrics['total_executions']
            if avg_time > threshold:
                slow_rules.append((rule_name, avg_time))
        return sorted(slow_rules, key=lambda x: x[1], reverse=True)
        
    def get_noisy_rules(self, threshold=0.1):
        noisy_rules = []
        for rule_name, metrics in self.metrics.items():
            fp_rate = metrics['false_positives'] / max(1, metrics['total_matches'])
            if fp_rate > threshold:
                noisy_rules.append((rule_name, fp_rate))
        return sorted(noisy_rules, key=lambda x: x[1], reverse=True)
```

## 📋 Rule Management Checklist

### Rule Development
- [ ] Define clear detection objective
- [ ] Research attack patterns and indicators
- [ ] Create initial rule with metadata
- [ ] Test against known samples
- [ ] Validate against clean files
- [ ] Optimize for performance
- [ ] Document rule behavior

### Rule Deployment
- [ ] Test in isolated environment
- [ ] Validate with security team
- [ ] Deploy to staging environment
- [ ] Monitor for false positives
- [ ] Gradually roll out to production
- [ ] Monitor performance impact

### Rule Maintenance
- [ ] Regular performance review
- [ ] False positive analysis
- [ ] Update for new threat variants
- [ ] Remove obsolete rules
- [ ] Document changes and versions

## ⚠️ Best Practices

### Rule Writing Guidelines
1. **Be Specific**: Avoid overly broad patterns
2. **Test Thoroughly**: Always test against clean and malicious samples
3. **Document Everything**: Include comprehensive metadata
4. **Consider Performance**: Optimize for speed and efficiency
5. **Version Control**: Track rule changes and versions
6. **Environment Awareness**: Consider your specific environment
7. **Regular Updates**: Keep rules current with threat landscape

### Common Pitfalls
- **False Positives**: Overly broad detection patterns
- **Performance Impact**: Complex rules that slow down scanning
- **Maintenance Burden**: Too many specific rules
- **Environment Mismatch**: Rules not suited for your environment
- **Outdated Rules**: Rules targeting obsolete threats

---

**Next Steps:**
- [Integration](12-integration.md) - API and system integration
- [Performance Tuning](14-performance.md) - Optimizing rule performance
- [API Reference](16-api-reference.md) - Custom rule API documentation
