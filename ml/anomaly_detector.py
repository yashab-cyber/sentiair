"""
Machine Learning Anomaly Detection Module
Implements unsupervised learning for behavioral anomaly detection
"""

import os
import pickle
import logging
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

class AnomalyDetector:
    """Anomaly detection using Isolation Forest and other ML techniques"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # ML configuration
        ml_config = config.get('ml', {})
        self.model_type = ml_config.get('model_type', 'isolation_forest')
        self.contamination_rate = ml_config.get('contamination_rate', 0.1)
        self.n_estimators = ml_config.get('n_estimators', 100)
        self.random_state = ml_config.get('random_state', 42)
        
        # Model components
        self.model = None
        self.scaler = None
        self.is_trained_flag = False
        
        # Model persistence
        self.model_dir = 'data/models'
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Training history
        self.training_history = []
        
    def train(self, features: List[List[float]]) -> bool:
        """Train the anomaly detection model"""
        try:
            self.logger.info(f"Training {self.model_type} model with {len(features)} samples")
            
            if len(features) < 10:
                self.logger.warning("Insufficient training data")
                return False
                
            # Convert to numpy array
            X = np.array(features)
            
            # Handle NaN values
            X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
            
            # Feature scaling
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Initialize and train model
            if self.model_type == 'isolation_forest':
                self.model = IsolationForest(
                    contamination=self.contamination_rate,
                    n_estimators=self.n_estimators,
                    random_state=self.random_state,
                    n_jobs=-1
                )
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
                
            # Train the model
            self.model.fit(X_scaled)
            self.is_trained_flag = True
            
            # Record training info
            training_info = {
                'timestamp': datetime.now(),
                'model_type': self.model_type,
                'n_samples': len(features),
                'n_features': len(features[0]) if features else 0,
                'contamination_rate': self.contamination_rate
            }
            self.training_history.append(training_info)
            
            self.logger.info("Model training completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return False
            
    def predict(self, features: List[float]) -> Tuple[bool, float]:
        """Predict if given features represent an anomaly"""
        try:
            if not self.is_trained():
                self.logger.warning("Model not trained, cannot make predictions")
                return False, 0.0
                
            # Convert to numpy array and reshape
            X = np.array(features).reshape(1, -1)
            
            # Handle NaN values
            X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            prediction = self.model.predict(X_scaled)[0]
            
            # Get anomaly score (confidence)
            anomaly_score = self.model.decision_function(X_scaled)[0]
            
            # Convert to interpretable format
            is_anomaly = prediction == -1
            confidence = self._convert_anomaly_score(anomaly_score)
            
            return is_anomaly, confidence
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            return False, 0.0
            
    def _convert_anomaly_score(self, score: float) -> float:
        """Convert anomaly score to confidence value between 0 and 1"""
        # Isolation Forest scores are typically between -1 and 1
        # More negative scores indicate higher anomaly likelihood
        # Convert to 0-1 scale where 1 is most anomalous
        normalized_score = np.clip(-score, -1, 1)  # Invert so negative becomes positive
        confidence = (normalized_score + 1) / 2  # Scale to 0-1
        return float(confidence)
        
    def save_model(self) -> bool:
        """Save trained model to disk"""
        try:
            if not self.is_trained():
                self.logger.warning("No trained model to save")
                return False
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save model
            model_path = os.path.join(self.model_dir, f"anomaly_model_{timestamp}.pkl")
            joblib.dump(self.model, model_path)
            
            # Save scaler
            scaler_path = os.path.join(self.model_dir, f"scaler_{timestamp}.pkl")
            joblib.dump(self.scaler, scaler_path)
            
            # Save metadata
            metadata = {
                'model_type': self.model_type,
                'training_timestamp': timestamp,
                'contamination_rate': self.contamination_rate,
                'n_estimators': self.n_estimators,
                'training_history': self.training_history
            }
            
            metadata_path = os.path.join(self.model_dir, f"metadata_{timestamp}.pkl")
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
                
            # Create symlinks to latest model
            latest_model_path = os.path.join(self.model_dir, "latest_model.pkl")
            latest_scaler_path = os.path.join(self.model_dir, "latest_scaler.pkl")
            latest_metadata_path = os.path.join(self.model_dir, "latest_metadata.pkl")
            
            # Remove existing symlinks
            for path in [latest_model_path, latest_scaler_path, latest_metadata_path]:
                if os.path.exists(path):
                    os.remove(path)
                    
            # Create new symlinks (or copies on Windows)
            try:
                os.symlink(model_path, latest_model_path)
                os.symlink(scaler_path, latest_scaler_path)
                os.symlink(metadata_path, latest_metadata_path)
            except OSError:
                # Fallback to copying on Windows
                import shutil
                shutil.copy2(model_path, latest_model_path)
                shutil.copy2(scaler_path, latest_scaler_path)
                shutil.copy2(metadata_path, latest_metadata_path)
            
            self.logger.info(f"Model saved to {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            return False
            
    def load_model(self) -> bool:
        """Load the latest trained model from disk"""
        try:
            latest_model_path = os.path.join(self.model_dir, "latest_model.pkl")
            latest_scaler_path = os.path.join(self.model_dir, "latest_scaler.pkl")
            latest_metadata_path = os.path.join(self.model_dir, "latest_metadata.pkl")
            
            if not all(os.path.exists(path) for path in [latest_model_path, latest_scaler_path]):
                self.logger.info("No saved model found")
                return False
                
            # Load model and scaler
            self.model = joblib.load(latest_model_path)
            self.scaler = joblib.load(latest_scaler_path)
            
            # Load metadata if available
            if os.path.exists(latest_metadata_path):
                with open(latest_metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    self.training_history = metadata.get('training_history', [])
                    
            self.is_trained_flag = True
            self.logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False
            
    def is_trained(self) -> bool:
        """Check if model is trained and ready for predictions"""
        return self.is_trained_flag and self.model is not None and self.scaler is not None
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        info = {
            'is_trained': self.is_trained(),
            'model_type': self.model_type,
            'contamination_rate': self.contamination_rate,
            'n_estimators': self.n_estimators
        }
        
        if self.training_history:
            latest_training = self.training_history[-1]
            info.update({
                'last_trained': latest_training['timestamp'],
                'training_samples': latest_training['n_samples'],
                'training_features': latest_training['n_features']
            })
            
        return info
        
    def evaluate_model(self, test_features: List[List[float]], test_labels: List[bool] = None) -> Dict[str, float]:
        """Evaluate model performance (if ground truth labels are available)"""
        try:
            if not self.is_trained():
                return {'error': 'Model not trained'}
                
            predictions = []
            confidences = []
            
            for features in test_features:
                is_anomaly, confidence = self.predict(features)
                predictions.append(is_anomaly)
                confidences.append(confidence)
                
            evaluation = {
                'total_predictions': len(predictions),
                'anomaly_predictions': sum(predictions),
                'average_confidence': np.mean(confidences),
                'confidence_std': np.std(confidences)
            }
            
            # If ground truth labels are provided, calculate metrics
            if test_labels is not None:
                from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
                
                evaluation.update({
                    'accuracy': accuracy_score(test_labels, predictions),
                    'precision': precision_score(test_labels, predictions, zero_division=0),
                    'recall': recall_score(test_labels, predictions, zero_division=0),
                    'f1_score': f1_score(test_labels, predictions, zero_division=0)
                })
                
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {'error': str(e)}
            
    def retrain_with_feedback(self, features: List[List[float]], labels: List[bool]) -> bool:
        """Retrain model with feedback from user corrections"""
        try:
            self.logger.info(f"Retraining model with {len(features)} feedback samples")
            
            # For unsupervised models like Isolation Forest, we can't directly use labels
            # But we can filter out false positives from training data
            normal_features = [f for f, l in zip(features, labels) if not l]
            
            if normal_features:
                return self.train(normal_features)
            else:
                self.logger.warning("No normal samples in feedback data")
                return False
                
        except Exception as e:
            self.logger.error(f"Error retraining with feedback: {e}")
            return False
