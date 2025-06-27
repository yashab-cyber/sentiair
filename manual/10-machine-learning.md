# Machine Learning Guide

Complete guide to Sentinair's AI and machine learning capabilities for behavioral threat detection.

## 🧠 ML System Overview

### How Sentinair AI Works
Sentinair uses **unsupervised machine learning** to detect anomalous behavior patterns without requiring pre-labeled malicious examples. The system:

1. **Learns Normal Behavior**: Analyzes typical system activity patterns
2. **Detects Deviations**: Identifies activities that don't match learned patterns  
3. **Scores Risk**: Assigns risk scores to unusual activities
4. **Adapts Over Time**: Continuously improves with new data

### Key Advantages
- **Zero-Day Detection**: Catches unknown threats
- **No Signature Updates**: Works without internet connectivity
- **Environment Adaptive**: Learns your specific system patterns
- **Low False Positives**: Tailored to your environment

## 🤖 Supported ML Algorithms

### Isolation Forest (Default)
**Best for**: General anomaly detection, fast training
```yaml
ml:
  model_type: "isolation_forest"
  contamination: 0.1              # Expected anomaly ratio
  n_estimators: 100               # Number of trees
  max_samples: 256                # Samples per tree
  random_state: 42                # Reproducible results
```

**Pros**: Fast, memory efficient, good for high-dimensional data  
**Cons**: May struggle with complex patterns

### One-Class SVM
**Best for**: Complex boundary detection, small datasets
```yaml
ml:
  model_type: "one_class_svm"
  nu: 0.1                        # Anomaly fraction
  kernel: "rbf"                  # rbf, linear, poly
  gamma: "scale"                 # Kernel coefficient
```

**Pros**: Good for complex patterns, theoretical foundation  
**Cons**: Slower training, memory intensive

### Local Outlier Factor (LOF)
**Best for**: Local anomaly detection, variable density
```yaml
ml:
  model_type: "local_outlier_factor"
  n_neighbors: 20                # Neighbors to consider
  contamination: 0.1             # Expected anomalies
  novelty: true                  # For prediction mode
```

**Pros**: Handles varying densities well  
**Cons**: Sensitive to parameter tuning

### Autoencoder (Deep Learning)
**Best for**: Complex patterns, large datasets
```yaml
ml:
  model_type: "autoencoder"
  hidden_layers: [64, 32, 16, 32, 64]
  epochs: 100
  batch_size: 32
  learning_rate: 0.001
  threshold: 0.95                # Reconstruction threshold
```

**Pros**: Captures complex patterns, flexible architecture  
**Cons**: Requires more data, longer training time

### Ensemble Methods
**Best for**: Maximum accuracy, combining multiple algorithms
```yaml
ml:
  model_type: "ensemble"
  models:
    - "isolation_forest"
    - "one_class_svm"  
    - "local_outlier_factor"
  voting_method: "soft"          # soft, hard, weighted
  weights: [0.4, 0.3, 0.3]      # Model weights
```

## 📊 Feature Engineering

### Automatic Feature Extraction
Sentinair automatically extracts features from raw events:

#### Process Features
```python
# Automatically extracted from process events
features = {
    'process_name_hash': hash(process_name) % 1000,
    'process_path_length': len(process_path),
    'is_system_process': 1 if is_system else 0,
    'parent_process_hash': hash(parent_name) % 1000,
    'command_line_length': len(command_line),
    'user_elevation': 1 if user == 'root' else 0
}
```

#### File Access Features
```python
# File access pattern features
features = {
    'file_path_depth': path.count('/'),
    'file_extension_hash': hash(extension) % 100,
    'file_size_log': log10(file_size + 1),
    'access_type_encoded': access_type_mapping[access_type],
    'is_system_file': 1 if '/etc/' in path else 0,
    'is_temp_file': 1 if '/tmp/' in path else 0
}
```

#### Temporal Features
```python
# Time-based behavioral features
features = {
    'hour_of_day': datetime.hour,
    'day_of_week': datetime.weekday(),
    'is_weekend': 1 if datetime.weekday() >= 5 else 0,
    'is_business_hours': 1 if 9 <= datetime.hour <= 17 else 0,
    'month_of_year': datetime.month,
    'time_since_last_event': seconds_since_last
}
```

#### USB Device Features
```python
# USB device characteristics
features = {
    'vendor_id_hash': hash(vendor_id) % 1000,
    'product_id_hash': hash(product_id) % 1000,
    'device_class': device_class_mapping[device_class],
    'is_mass_storage': 1 if class == 'mass_storage' else 0,
    'serial_number_entropy': calculate_entropy(serial_number)
}
```

### Custom Feature Configuration
```yaml
ml:
  features:
    # Enable/disable feature categories
    time_based: true
    process_based: true  
    file_based: true
    user_based: true
    network_based: false
    
    # Custom feature extraction
    custom_features:
      - name: "suspicious_extensions"
        type: "categorical"
        values: [".exe", ".bat", ".scr", ".com"]
        
      - name: "system_directories"
        type: "path_match"
        patterns: ["/etc/*", "/sys/*", "/proc/*"]
        
      - name: "office_hours"
        type: "time_range"
        start: "09:00"
        end: "17:00"
```

## 🎯 Model Training

### Training Process
```bash
# Start training via CLI
sentinair> train
🧠 Starting ML model training...
📊 Loading training data: 15,847 events
🔄 Training Isolation Forest model...
📈 Extracting features from events...
⏳ Training in progress... [████████░░] 80%
✅ Training completed in 2m 34s
📈 Model accuracy: 94.2%
💾 Model saved to data/models/isolation_forest_20250627.pkl
```

### Training Data Requirements
```yaml
# Minimum data requirements
training_requirements:
  minimum_events: 1000           # Absolute minimum
  recommended_events: 5000       # For good performance
  optimal_events: 10000+         # For best results
  
  # Data distribution
  normal_events: 90%             # Majority should be normal
  anomalous_events: 10%          # Small percentage of anomalies
  
  # Time coverage
  minimum_days: 7                # At least one week
  recommended_days: 30           # One month preferred
```

### Advanced Training Options
```bash
# Training with custom parameters
sentinair> train --contamination 0.05 --estimators 200
sentinair> train --data-file custom_training_data.json
sentinair> train --validation-split 0.2
sentinair> train --cross-validation 5

# Training specific models
sentinair> train --model isolation_forest
sentinair> train --model autoencoder --epochs 200
sentinair> train --model ensemble

# Training with feature selection
sentinair> train --feature-selection variance_threshold
sentinair> train --features process,file,time
```

### Training Data Quality
```bash
# Check training data quality
sentinair> model analyze-data
📊 TRAINING DATA ANALYSIS
════════════════════════════════════════
Total Events: 15,847
├─ Normal Events: 14,262 (90.0%)
├─ Anomalous Events: 1,585 (10.0%)

Event Types:
├─ File Access: 8,932 (56.4%)
├─ Process Start: 4,421 (27.9%)
├─ USB Events: 234 (1.5%)
└─ Behavior: 2,260 (14.3%)

Data Quality Score: 94.2/100
✅ Sufficient data volume
✅ Good normal/anomaly ratio
⚠️ Limited USB event coverage
✅ Good temporal distribution
```

## 📈 Model Performance and Evaluation

### Performance Metrics
```bash
# View model performance
sentinair> model evaluate
🎯 MODEL PERFORMANCE METRICS
════════════════════════════════════════
Overall Accuracy: 94.2%
Precision: 91.8%
Recall: 96.5%
F1-Score: 94.1%

Confusion Matrix:
                Predicted
Actual      Normal  Anomaly
Normal        1420      23    (98.4% correct)
Anomaly         31     126    (80.3% correct)

False Positive Rate: 1.6%
False Negative Rate: 19.7%
```

### Cross-Validation Results
```bash
# Run cross-validation
sentinair> model cross-validate --folds 5
🔄 5-FOLD CROSS VALIDATION
════════════════════════════════════════
Fold 1: Accuracy 93.1%, F1: 92.8%
Fold 2: Accuracy 94.7%, F1: 94.2%
Fold 3: Accuracy 95.2%, F1: 95.0%
Fold 4: Accuracy 93.8%, F1: 93.5%
Fold 5: Accuracy 94.9%, F1: 94.6%

Mean Accuracy: 94.3% ± 0.8%
Mean F1-Score: 94.0% ± 0.9%
```

### Feature Importance Analysis
```bash
# Analyze feature importance
sentinair> model feature-importance
📊 FEATURE IMPORTANCE ANALYSIS
════════════════════════════════════════
Top 10 Most Important Features:
1. process_path_length        (12.3%)
2. hour_of_day               (11.7%)
3. file_extension_hash       (10.2%)
4. is_system_process          (9.8%)
5. file_path_depth            (8.9%)
6. day_of_week                (8.1%)
7. user_elevation             (7.4%)
8. command_line_length        (6.9%)
9. file_size_log              (6.2%)
10. time_since_last_event     (5.8%)

Feature Categories:
├─ Process Features: 42.1%
├─ Time Features: 28.7%
├─ File Features: 23.9%
└─ User Features: 5.3%
```

## 🔧 Model Optimization

### Hyperparameter Tuning
```bash
# Automatic hyperparameter optimization
sentinair> model optimize
🔧 HYPERPARAMETER OPTIMIZATION
════════════════════════════════════════
Optimizing Isolation Forest parameters...
Testing 50 parameter combinations...

Best Parameters Found:
├─ contamination: 0.08
├─ n_estimators: 150
├─ max_samples: 512
└─ max_features: 0.8

Improvement: 94.2% → 96.1% accuracy
```

### Manual Parameter Tuning
```yaml
# Fine-tune model parameters
ml:
  isolation_forest:
    contamination: 0.08          # Reduced from 0.1
    n_estimators: 150            # Increased from 100
    max_samples: 512             # Increased from 256
    max_features: 0.8            # Feature subsampling
    bootstrap: false             # Sampling method
    warm_start: false            # Incremental training
```

### Ensemble Optimization
```yaml
ml:
  ensemble:
    enabled: true
    models:
      - model: "isolation_forest"
        weight: 0.4
        params:
          contamination: 0.08
          n_estimators: 150
          
      - model: "one_class_svm"
        weight: 0.3  
        params:
          nu: 0.05
          gamma: "auto"
          
      - model: "local_outlier_factor"
        weight: 0.3
        params:
          n_neighbors: 25
          contamination: 0.08
    
    voting_method: "weighted"
    threshold_method: "adaptive"
```

## 🔄 Continuous Learning

### Automatic Model Retraining
```yaml
ml:
  auto_train: true
  retrain_interval: 168          # Hours (weekly)
  retrain_threshold: 1000        # New events before retrain
  performance_threshold: 0.90    # Retrain if accuracy drops below
  
  # Incremental learning
  incremental_learning:
    enabled: true
    batch_size: 100              # Events per update
    learning_rate: 0.01          # Adaptation rate
```

### Feedback Integration
```bash
# Provide feedback to improve model
sentinair> model feedback --event-id 12345 --correct-label normal
sentinair> model feedback --alert-id 67890 --false-positive

# Batch feedback from file
sentinair> model feedback --file feedback_labels.csv
```

### Model Versioning
```bash
# List model versions
sentinair> model versions
📋 MODEL VERSIONS
════════════════════════════════════════
* v1.3 - isolation_forest_20250627.pkl (active)
  │ Accuracy: 96.1%, Trained: 2025-06-27 08:00
  │ Training Data: 15,847 events
  
  v1.2 - isolation_forest_20250626.pkl
  │ Accuracy: 94.2%, Trained: 2025-06-26 08:00
  │ Training Data: 12,234 events
  
  v1.1 - isolation_forest_20250625.pkl
  │ Accuracy: 92.1%, Trained: 2025-06-25 08:00
  │ Training Data: 8,891 events

# Switch between versions
sentinair> model use v1.2
sentinair> model compare v1.2 v1.3
```

## 🎛️ Advanced ML Features

### Feature Engineering Pipeline
```python
# Custom feature engineering pipeline
from ml.feature_pipeline import FeaturePipeline

pipeline = FeaturePipeline([
    ('scaler', StandardScaler()),
    ('selector', VarianceThreshold(threshold=0.01)),
    ('pca', PCA(n_components=0.95)),
    ('anomaly_detector', IsolationForest())
])
```

### Custom Anomaly Detectors
```python
# Implement custom detector
class CustomAnomalyDetector:
    def __init__(self, config):
        self.threshold = config.get('threshold', 0.5)
        
    def fit(self, X):
        # Custom training logic
        pass
        
    def predict(self, X):
        # Custom prediction logic
        pass
        
    def decision_function(self, X):
        # Return anomaly scores
        pass
```

### Multi-Model Ensemble
```bash
# Train multiple models simultaneously
sentinair> model train-ensemble
🧠 TRAINING ENSEMBLE MODELS
════════════════════════════════════════
Training Isolation Forest... ✅ (96.1% accuracy)
Training One-Class SVM...    ✅ (94.7% accuracy)  
Training LOF...              ✅ (93.2% accuracy)
Training Autoencoder...      ✅ (95.8% accuracy)

Ensemble Performance: 97.3% accuracy
Best Single Model: Isolation Forest (96.1%)
Improvement: +1.2% from ensemble
```

## 📊 Model Monitoring and Maintenance

### Performance Monitoring
```bash
# Monitor model performance over time
sentinair> model monitor
📈 MODEL PERFORMANCE MONITORING
════════════════════════════════════════
Current Period (24h):
├─ Accuracy: 95.8% (↓ 0.3% from baseline)
├─ False Positives: 2.1% (↑ 0.2% from baseline)
├─ Detection Rate: 96.5% (↔ stable)
└─ Prediction Time: 0.23ms (↔ stable)

Trends (7 days):
├─ Accuracy Trend: ↘ -0.8%
├─ FP Rate Trend: ↗ +0.4%  
└─ Recommendation: Consider retraining
```

### Model Drift Detection
```bash
# Detect model drift
sentinair> model drift-analysis
🔍 MODEL DRIFT ANALYSIS
════════════════════════════════════════
Data Drift: ⚠️ MODERATE
├─ Feature Distribution Change: 15.2%
├─ Concept Drift Score: 0.23
└─ Recommendation: Monitor closely

Performance Drift: ✅ LOW
├─ Accuracy Change: -0.8%
├─ Stability Score: 0.91
└─ Status: Within acceptable range

Action Required: Consider retraining within 7 days
```

### Maintenance Schedule
```yaml
ml_maintenance:
  # Automated maintenance tasks
  daily:
    - performance_check
    - drift_detection
    - log_analysis
    
  weekly:
    - model_retraining
    - feature_importance_analysis
    - cross_validation
    
  monthly:
    - hyperparameter_optimization
    - model_comparison
    - architecture_review
```

---

**Previous**: [Custom Rules](11-custom-rules.md) | **Next**: [Integration](12-integration.md)
