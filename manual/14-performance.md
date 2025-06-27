# Performance Tuning Guide

This comprehensive guide covers optimizing Sentinair performance for different environments, hardware configurations, and workload requirements.

## 🎯 Performance Overview

### Performance Metrics
- **Throughput**: Events processed per second
- **Latency**: Time from event to detection
- **Resource Usage**: CPU, memory, and disk utilization
- **Detection Accuracy**: Balance between speed and accuracy
- **System Impact**: Effect on monitored system performance

### Performance Goals
```yaml
# Performance targets by environment
performance_targets:
  desktop:
    cpu_usage: "< 10%"
    memory_usage: "< 256MB"
    detection_latency: "< 1s"
    
  server:
    cpu_usage: "< 25%"
    memory_usage: "< 1GB"
    detection_latency: "< 500ms"
    throughput: "> 1000 events/sec"
    
  enterprise:
    cpu_usage: "< 15%"
    memory_usage: "< 2GB"
    detection_latency: "< 200ms"
    throughput: "> 5000 events/sec"
```

## 🔧 System-Level Optimization

### Operating System Tuning

#### Linux Performance Tuning
```bash
#!/bin/bash
# scripts/linux_performance_tuning.sh

# Kernel parameters for better performance
echo "# Sentinair performance tuning" >> /etc/sysctl.conf
echo "vm.swappiness=10" >> /etc/sysctl.conf
echo "vm.dirty_ratio=15" >> /etc/sysctl.conf
echo "vm.dirty_background_ratio=5" >> /etc/sysctl.conf
echo "kernel.sched_min_granularity_ns=10000000" >> /etc/sysctl.conf
echo "kernel.sched_wakeup_granularity_ns=15000000" >> /etc/sysctl.conf

# Apply settings
sysctl -p

# I/O scheduler optimization
echo noop > /sys/block/sda/queue/scheduler

# CPU governor for performance
echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# File system optimization
mount -o remount,noatime,nodiratime /

echo "Linux performance tuning completed"
```

#### Windows Performance Tuning
```powershell
# scripts/windows_performance_tuning.ps1

# Disable Windows Defender real-time protection for Sentinair files
Add-MpPreference -ExclusionPath "C:\Program Files\Sentinair"
Add-MpPreference -ExclusionProcess "python.exe"

# Set high performance power plan
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Optimize for background services
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl" -Name "Win32PrioritySeparation" -Value 24

# Increase system file cache
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" -Name "LargeSystemCache" -Value 1

Write-Host "Windows performance tuning completed"
```

### Hardware Optimization

#### Storage Optimization
```yaml
# config/storage_optimization.yaml
storage:
  database:
    location: "/fast_ssd/sentinair/"  # Use fastest storage
    journal_mode: "WAL"              # Write-Ahead Logging
    synchronous: "NORMAL"            # Balance safety/performance
    cache_size: 10000                # Pages in cache
    temp_store: "memory"             # Temp tables in memory
    
  logs:
    location: "/logs/sentinair/"
    compression: true                # Compress old logs
    rotation_size: "50MB"
    max_files: 10
    
  temp_files:
    location: "/tmp/sentinair/"
    cleanup_interval: "1h"
```

#### Memory Optimization
```yaml
# config/memory_optimization.yaml
memory:
  allocation:
    max_heap_size: "512MB"
    initial_heap_size: "128MB"
    buffer_pools: "64MB"
    
  caching:
    event_cache_size: 10000
    rule_cache_size: 1000
    ml_model_cache: true
    file_system_cache: true
    
  garbage_collection:
    threshold: 1000
    frequency: "5m"
    aggressive_cleanup: false
```

## ⚡ Application-Level Optimization

### Core Engine Optimization

#### Event Processing Optimization
```python
# core/optimized_engine.py
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

class OptimizedSentinairEngine:
    def __init__(self):
        self.event_queue = queue.Queue(maxsize=10000)
        self.worker_pool = ThreadPoolExecutor(max_workers=4)
        self.batch_size = 100
        self.batch_timeout = 1.0  # seconds
        
    def start_optimized_processing(self):
        """Start optimized event processing"""
        # Start batch processor
        threading.Thread(
            target=self._batch_processor,
            daemon=True
        ).start()
        
        # Start worker threads
        for _ in range(4):
            threading.Thread(
                target=self._event_worker,
                daemon=True
            ).start()
            
    def _batch_processor(self):
        """Process events in batches for better performance"""
        batch = []
        last_process_time = time.time()
        
        while True:
            try:
                # Get event with timeout
                event = self.event_queue.get(timeout=0.1)
                batch.append(event)
                
                # Process batch if full or timeout reached
                if (len(batch) >= self.batch_size or
                    time.time() - last_process_time > self.batch_timeout):
                    
                    self._process_batch(batch)
                    batch = []
                    last_process_time = time.time()
                    
            except queue.Empty:
                # Process partial batch on timeout
                if batch and time.time() - last_process_time > self.batch_timeout:
                    self._process_batch(batch)
                    batch = []
                    last_process_time = time.time()
                    
    def _process_batch(self, events):
        """Process a batch of events efficiently"""
        # Group events by type for optimized processing
        grouped_events = self._group_events_by_type(events)
        
        # Process each group with type-specific optimizations
        for event_type, event_list in grouped_events.items():
            self._process_event_group(event_type, event_list)
```

#### Rule Engine Optimization
```python
# core/optimized_rules.py
class OptimizedRuleEngine:
    def __init__(self):
        self.compiled_rules = {}
        self.rule_cache = {}
        self.index_cache = {}
        
    def optimize_rules(self):
        """Pre-compile and optimize rules"""
        # Compile YARA rules once
        for rule_file in self.get_rule_files():
            self.compiled_rules[rule_file] = yara.compile(rule_file)
            
        # Create rule indices for faster matching
        self._create_rule_indices()
        
        # Pre-compute rule priorities
        self._compute_rule_priorities()
        
    def _create_rule_indices(self):
        """Create indices for faster rule matching"""
        # Index by file extension
        self.file_extension_rules = {}
        
        # Index by file size ranges
        self.file_size_rules = {
            'small': [],    # < 1MB
            'medium': [],   # 1MB - 10MB
            'large': []     # > 10MB
        }
        
        # Index by event type
        self.event_type_rules = {}
        
    def match_optimized(self, target, event_type):
        """Optimized rule matching with indexing"""
        relevant_rules = self._get_relevant_rules(target, event_type)
        
        # Use cache if available
        cache_key = self._generate_cache_key(target, event_type)
        if cache_key in self.rule_cache:
            return self.rule_cache[cache_key]
            
        # Match only relevant rules
        matches = []
        for rule in relevant_rules:
            if rule.match(target):
                matches.append(rule)
                
        # Cache result
        self.rule_cache[cache_key] = matches
        return matches
```

### Database Optimization

#### SQLite Performance Tuning
```python
# utils/optimized_database.py
class OptimizedDatabaseManager:
    def __init__(self):
        self.connection_pool = []
        self.pool_size = 5
        self.init_connection_pool()
        
    def init_connection_pool(self):
        """Initialize connection pool for better performance"""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None  # Autocommit mode
            )
            
            # Optimize SQLite settings
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=memory")
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            self.connection_pool.append(conn)
            
    def get_connection(self):
        """Get connection from pool"""
        if self.connection_pool:
            return self.connection_pool.pop()
        else:
            # Create new connection if pool is empty
            return self.create_optimized_connection()
            
    def return_connection(self, conn):
        """Return connection to pool"""
        if len(self.connection_pool) < self.pool_size:
            self.connection_pool.append(conn)
        else:
            conn.close()
            
    def batch_insert_events(self, events):
        """Optimized batch insert for events"""
        conn = self.get_connection()
        try:
            # Use executemany for better performance
            conn.executemany(
                "INSERT INTO events (timestamp, type, data) VALUES (?, ?, ?)",
                [(e.timestamp, e.type, e.data) for e in events]
            )
        finally:
            self.return_connection(conn)
```

#### Index Optimization
```sql
-- database/optimization_indices.sql

-- Optimize alert queries
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_composite ON alerts(severity, status, timestamp);

-- Optimize event queries
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
CREATE INDEX IF NOT EXISTS idx_events_composite ON events(type, timestamp);

-- Optimize ML feature queries
CREATE INDEX IF NOT EXISTS idx_features_timestamp ON ml_features(timestamp);
CREATE INDEX IF NOT EXISTS idx_features_user ON ml_features(user_id);

-- Optimize file monitoring queries
CREATE INDEX IF NOT EXISTS idx_file_events_path ON file_events(file_path);
CREATE INDEX IF NOT EXISTS idx_file_events_timestamp ON file_events(timestamp);
```

## 🧠 Machine Learning Optimization

### Model Performance Tuning

#### Isolation Forest Optimization
```python
# ml/optimized_anomaly_detector.py
class OptimizedAnomalyDetector:
    def __init__(self):
        self.models = {}
        self.feature_cache = {}
        self.prediction_cache = {}
        
    def create_optimized_model(self, model_name):
        """Create optimized Isolation Forest model"""
        model = IsolationForest(
            n_estimators=100,        # Reduced for speed
            max_samples='auto',      # Auto-sizing
            contamination=0.1,       # Expected anomaly rate
            max_features=1.0,        # Use all features
            bootstrap=False,         # Faster training
            n_jobs=-1,              # Use all CPU cores
            random_state=42,
            verbose=0
        )
        
        self.models[model_name] = model
        return model
        
    def batch_predict(self, features_batch):
        """Batch prediction for better performance"""
        # Group similar features for batch processing
        grouped_features = self._group_similar_features(features_batch)
        
        predictions = []
        for group_key, group_features in grouped_features.items():
            model = self._get_model_for_group(group_key)
            group_predictions = model.predict(group_features)
            predictions.extend(group_predictions)
            
        return predictions
        
    def incremental_learning(self, new_features):
        """Incremental model updates"""
        # Use partial_fit for online learning where available
        for model_name, model in self.models.items():
            if hasattr(model, 'partial_fit'):
                model.partial_fit(new_features)
            else:
                # Retrain with recent data only
                recent_data = self._get_recent_training_data(model_name)
                combined_data = np.vstack([recent_data, new_features])
                model.fit(combined_data)
```

#### Feature Engineering Optimization
```python
# ml/optimized_features.py
class OptimizedFeatureExtractor:
    def __init__(self):
        self.feature_cache = {}
        self.computation_cache = {}
        
    def extract_features_optimized(self, events):
        """Optimized feature extraction"""
        # Use vectorized operations where possible
        features = {}
        
        # Time-based features (vectorized)
        timestamps = np.array([e.timestamp for e in events])
        features['hour_of_day'] = (timestamps % 86400) // 3600
        features['day_of_week'] = (timestamps // 86400) % 7
        
        # Count-based features (use collections.Counter)
        event_types = [e.type for e in events]
        type_counts = Counter(event_types)
        features['event_type_counts'] = type_counts
        
        # Statistical features (use numpy for speed)
        if 'file_size' in [e.type for e in events]:
            file_sizes = [e.data.get('size', 0) for e in events if e.type == 'file_size']
            if file_sizes:
                features['file_size_mean'] = np.mean(file_sizes)
                features['file_size_std'] = np.std(file_sizes)
                features['file_size_max'] = np.max(file_sizes)
        
        return features
        
    def cache_features(self, key, features):
        """Cache computed features"""
        self.feature_cache[key] = {
            'features': features,
            'timestamp': time.time()
        }
        
        # Clean old cache entries
        self._clean_feature_cache()
```

## 📊 Monitoring Optimization

### Event Processing Optimization

#### File Monitoring Optimization
```python
# core/monitors/optimized_file_monitor.py
class OptimizedFileMonitor:
    def __init__(self):
        self.batch_events = []
        self.batch_timeout = 1.0
        self.last_batch_time = time.time()
        
    def setup_optimized_monitoring(self):
        """Setup optimized file monitoring"""
        # Use recursive watching with filters
        self.observer = Observer()
        
        # Monitor only important directories
        important_dirs = [
            '/etc/',
            '/bin/',
            '/usr/bin/',
            '/home/',
            'C:\\Windows\\System32\\',
            'C:\\Users\\'
        ]
        
        for directory in important_dirs:
            if os.path.exists(directory):
                self.observer.schedule(
                    self._get_optimized_handler(),
                    directory,
                    recursive=True
                )
                
    def _get_optimized_handler(self):
        """Get optimized event handler"""
        class OptimizedHandler(FileSystemEventHandler):
            def __init__(self, parent):
                self.parent = parent
                self.filters = self._setup_filters()
                
            def on_any_event(self, event):
                # Apply filters first
                if not self._should_process(event):
                    return
                    
                # Batch events for processing
                self.parent._add_to_batch(event)
                
            def _should_process(self, event):
                """Filter events for performance"""
                # Skip temporary files
                if '.tmp' in event.src_path or '~' in event.src_path:
                    return False
                    
                # Skip system files that change frequently
                if '/.git/' in event.src_path or '\\.git\\' in event.src_path:
                    return False
                    
                return True
        
        return OptimizedHandler(self)
```

#### Process Monitoring Optimization
```python
# core/monitors/optimized_process_monitor.py
class OptimizedProcessMonitor:
    def __init__(self):
        self.process_cache = {}
        self.monitoring_interval = 1.0  # seconds
        self.blacklist_cache = set()
        
    def start_optimized_monitoring(self):
        """Start optimized process monitoring"""
        # Use psutil for efficient process monitoring
        threading.Thread(
            target=self._monitor_processes_optimized,
            daemon=True
        ).start()
        
    def _monitor_processes_optimized(self):
        """Optimized process monitoring loop"""
        while True:
            start_time = time.time()
            
            try:
                # Get all processes efficiently
                current_processes = {p.pid: p for p in psutil.process_iter()}
                
                # Compare with cache to find new processes
                new_processes = set(current_processes.keys()) - set(self.process_cache.keys())
                
                # Process only new processes
                for pid in new_processes:
                    try:
                        process = current_processes[pid]
                        self._analyze_process_optimized(process)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                # Update cache
                self.process_cache = current_processes
                
            except Exception as e:
                self.logger.error(f"Process monitoring error: {e}")
                
            # Sleep for remaining interval time
            elapsed = time.time() - start_time
            sleep_time = max(0, self.monitoring_interval - elapsed)
            time.sleep(sleep_time)
            
    def _analyze_process_optimized(self, process):
        """Optimized process analysis"""
        try:
            # Get process info efficiently
            with process.oneshot():
                cmdline = process.cmdline()
                exe_path = process.exe()
                pid = process.pid
                
            # Quick blacklist check
            if self._is_blacklisted(exe_path):
                self._create_alert(process, "blacklisted_process")
                return
                
            # Cache negative results to avoid repeated checks
            if exe_path in self.blacklist_cache:
                return
                
            # Perform analysis
            if self._is_suspicious_process(process, cmdline, exe_path):
                self._create_alert(process, "suspicious_process")
            else:
                # Cache as non-suspicious
                self.blacklist_cache.add(exe_path)
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
```

## 🔋 Resource Management

### Memory Management

#### Memory Pool Implementation
```python
# utils/memory_pool.py
class MemoryPool:
    def __init__(self, pool_size=1000):
        self.pool = queue.Queue(maxsize=pool_size)
        self.pool_size = pool_size
        self.allocated_objects = set()
        
        # Pre-allocate objects
        for _ in range(pool_size):
            self.pool.put(self._create_object())
            
    def get_object(self):
        """Get object from pool"""
        try:
            obj = self.pool.get_nowait()
            self.allocated_objects.add(id(obj))
            return obj
        except queue.Empty:
            # Create new object if pool is empty
            obj = self._create_object()
            self.allocated_objects.add(id(obj))
            return obj
            
    def return_object(self, obj):
        """Return object to pool"""
        if id(obj) in self.allocated_objects:
            self.allocated_objects.remove(id(obj))
            
            # Reset object state
            self._reset_object(obj)
            
            # Return to pool if not full
            try:
                self.pool.put_nowait(obj)
            except queue.Full:
                # Pool is full, let object be garbage collected
                pass
                
    def _create_object(self):
        """Create new object for pool"""
        return {}  # Or whatever object type you need
        
    def _reset_object(self, obj):
        """Reset object state for reuse"""
        if isinstance(obj, dict):
            obj.clear()
```

### CPU Optimization

#### Thread Pool Management
```python
# utils/thread_pool.py
class OptimizedThreadPool:
    def __init__(self, max_workers=None):
        if max_workers is None:
            max_workers = min(32, (os.cpu_count() or 1) + 4)
            
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = queue.PriorityQueue()
        self.active_tasks = {}
        
    def submit_priority_task(self, priority, func, *args, **kwargs):
        """Submit task with priority"""
        task_id = uuid.uuid4()
        future = self.executor.submit(func, *args, **kwargs)
        
        self.active_tasks[task_id] = {
            'future': future,
            'priority': priority,
            'submitted_at': time.time()
        }
        
        return task_id, future
        
    def optimize_workload(self):
        """Optimize thread pool workload"""
        # Monitor CPU usage and adjust accordingly
        cpu_usage = psutil.cpu_percent(interval=1)
        
        if cpu_usage > 80:
            # Reduce concurrent tasks
            self._reduce_concurrency()
        elif cpu_usage < 50:
            # Increase concurrent tasks
            self._increase_concurrency()
            
    def _reduce_concurrency(self):
        """Reduce concurrency when CPU is high"""
        # Implement backpressure
        time.sleep(0.1)
        
    def _increase_concurrency(self):
        """Increase concurrency when CPU is low"""
        # Process more tasks from queue
        pass
```

## 📈 Performance Monitoring

### Performance Metrics Collection

#### Real-time Performance Monitor
```python
# monitoring/performance_monitor.py
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
        self.collection_interval = 30  # seconds
        
    def start_monitoring(self):
        """Start performance monitoring"""
        threading.Thread(
            target=self._collect_metrics,
            daemon=True
        ).start()
        
    def _collect_metrics(self):
        """Collect performance metrics"""
        while True:
            try:
                metrics = {
                    'timestamp': time.time(),
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'process_count': len(psutil.pids()),
                    'thread_count': threading.active_count(),
                    'queue_sizes': self._get_queue_sizes(),
                    'cache_hit_rates': self._get_cache_hit_rates(),
                    'throughput': self._calculate_throughput()
                }
                
                self._store_metrics(metrics)
                self._check_performance_thresholds(metrics)
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                
            time.sleep(self.collection_interval)
            
    def _calculate_throughput(self):
        """Calculate events per second"""
        current_time = time.time()
        time_window = 60  # seconds
        
        recent_events = self._get_events_in_window(current_time - time_window, current_time)
        return len(recent_events) / time_window
        
    def get_performance_report(self):
        """Generate performance report"""
        return {
            'uptime': time.time() - self.start_time,
            'current_metrics': self.metrics,
            'averages': self._calculate_averages(),
            'trends': self._calculate_trends(),
            'bottlenecks': self._identify_bottlenecks()
        }
```

## 📋 Performance Tuning Checklist

### System Level
- [ ] Optimize OS kernel parameters
- [ ] Configure power management for performance
- [ ] Optimize file system settings
- [ ] Configure storage for performance
- [ ] Set appropriate process priorities

### Application Level
- [ ] Enable connection pooling
- [ ] Implement caching strategies
- [ ] Optimize batch processing
- [ ] Use efficient data structures
- [ ] Implement lazy loading

### Database Level
- [ ] Create appropriate indices
- [ ] Optimize query patterns
- [ ] Configure connection pooling
- [ ] Enable query caching
- [ ] Optimize schema design

### Monitoring Level
- [ ] Implement event filtering
- [ ] Use batch processing
- [ ] Optimize rule matching
- [ ] Configure appropriate timeouts
- [ ] Monitor resource usage

## ⚠️ Performance Best Practices

### Do's
- ✅ **Monitor Performance**: Continuously monitor key metrics
- ✅ **Batch Operations**: Process events in batches when possible
- ✅ **Cache Results**: Cache frequently accessed data
- ✅ **Use Indices**: Create database indices for common queries
- ✅ **Optimize Rules**: Write efficient detection rules
- ✅ **Limit Resources**: Set appropriate resource limits

### Don'ts
- ❌ **Over-optimize**: Don't optimize prematurely
- ❌ **Ignore Monitoring**: Don't run without performance monitoring
- ❌ **Complex Rules**: Avoid overly complex detection rules
- ❌ **Memory Leaks**: Watch for memory leaks in long-running processes
- ❌ **Blocking Operations**: Avoid blocking the main thread
- ❌ **Resource Exhaustion**: Don't let any component consume all resources

---

**Next Steps:**
- [Maintenance](15-maintenance.md) - System maintenance and updates
- [Troubleshooting](13-troubleshooting.md) - Performance troubleshooting
- [Configuration Reference](17-config-reference.md) - Performance configuration options
