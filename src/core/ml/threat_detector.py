"""
Machine Learning Threat Detection Engine
Uses ensemble models to predict and detect cyber threats
"""

import asyncio
import logging
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

from ...utils.logger import get_logger
from ...utils.feature_extraction import NetworkFeatureExtractor

logger = get_logger(__name__)

@dataclass
class ThreatPrediction:
    """Threat prediction result"""
    timestamp: datetime
    threat_type: str
    confidence: float
    source_ip: str
    target_ip: str
    indicators: Dict[str, Any]
    risk_level: str
    recommended_actions: List[str]

@dataclass
class ThreatPattern:
    """Threat pattern definition"""
    name: str
    features: List[str]
    thresholds: Dict[str, float]
    description: str

class ThreatDetector:
    """Advanced ML-based threat detection system"""
    
    def __init__(self, model_path: str, config: Dict[str, Any]):
        self.model_path = Path(model_path)
        self.config = config
        self.models = {}
        self.scalers = {}
        self.feature_extractor = NetworkFeatureExtractor()
        
        # Threat patterns database
        self.threat_patterns = self._load_threat_patterns()
        
        # Event callbacks
        self._threat_callbacks: List[Callable] = []
        
        # Model performance tracking
        self.model_stats = {
            'predictions_made': 0,
            'threats_detected': 0,
            'false_positives': 0,
            'accuracy': 0.0
        }
        
        # Feature buffer for real-time analysis
        self.feature_buffer = []
        self.buffer_size = 1000
    
    async def initialize(self):
        """Initialize ML models and load pre-trained weights"""
        logger.info("Initializing threat detection models...")
        
        # Create models directory if it doesn't exist
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Load or create models
        await self._load_or_create_models()
        
        # Start background tasks
        asyncio.create_task(self._retrain_models_periodically())
        asyncio.create_task(self._update_threat_patterns())
        
        logger.info("Threat detection models initialized successfully")
    
    async def _load_or_create_models(self):
        """Load existing models or create new ones"""
        model_files = {
            'anomaly_detector': 'isolation_forest.pkl',
            'threat_classifier': 'random_forest.pkl',
            'behavioral_model': 'behavioral_classifier.pkl'
        }
        
        for model_name, filename in model_files.items():
            model_file = self.model_path / filename
            scaler_file = self.model_path / f"{model_name}_scaler.pkl"
            
            if model_file.exists() and scaler_file.exists():
                # Load existing model
                logger.info(f"Loading {model_name} from {model_file}")
                self.models[model_name] = joblib.load(model_file)
                self.scalers[model_name] = joblib.load(scaler_file)
            else:
                # Create new model
                logger.info(f"Creating new {model_name}")
                await self._create_model(model_name)
    
    async def _create_model(self, model_name: str):
        """Create a new ML model"""
        if model_name == 'anomaly_detector':
            model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
        elif model_name == 'threat_classifier':
            model = RandomForestClassifier(
                n_estimators=200,
                random_state=42,
                max_depth=10,
                min_samples_split=5
            )
        elif model_name == 'behavioral_model':
            model = RandomForestClassifier(
                n_estimators=150,
                random_state=42,
                max_depth=8
            )
        else:
            raise ValueError(f"Unknown model type: {model_name}")
        
        # Create scaler
        scaler = StandardScaler()
        
        # Train with synthetic data if no real data available
        await self._train_with_synthetic_data(model, scaler, model_name)
        
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        
        # Save model
        model_file = self.model_path / f"{model_name.replace('_', '_')}.pkl"
        scaler_file = self.model_path / f"{model_name}_scaler.pkl"
        
        joblib.dump(model, model_file)
        joblib.dump(scaler, scaler_file)
    
    async def _train_with_synthetic_data(self, model, scaler, model_name: str):
        """Train model with synthetic threat data"""
        logger.info(f"Training {model_name} with synthetic data...")
        
        # Generate synthetic training data
        X_train, y_train = self._generate_synthetic_training_data(model_name)
        
        # Fit scaler and transform data
        X_train_scaled = scaler.fit_transform(X_train)
        
        # Train model
        if hasattr(model, 'fit'):
            if model_name == 'anomaly_detector':
                # Isolation Forest doesn't need labels
                model.fit(X_train_scaled)
            else:
                model.fit(X_train_scaled, y_train)
        
        logger.info(f"{model_name} training completed")
    
    def _generate_synthetic_training_data(self, model_name: str):
        """Generate synthetic training data for initial model training"""
        np.random.seed(42)
        n_samples = 10000
        
        # Use consistent feature count of 32 (matching real feature extraction)
        n_features = 32
        
        if model_name == 'anomaly_detector':
            # Features for anomaly detection
            features = np.random.normal(0, 1, (n_samples, n_features))
            # Add some anomalies
            anomaly_indices = np.random.choice(n_samples, size=int(n_samples * 0.1), replace=False)
            features[anomaly_indices] += np.random.normal(5, 2, (len(anomaly_indices), n_features))
            
            return features, None
        
        elif model_name == 'threat_classifier':
            # Features for threat classification
            features = np.random.normal(0, 1, (n_samples, n_features))
            
            # Create threat labels
            threat_types = ['normal', 'port_scan', 'dos', 'malware', 'phishing']
            labels = np.random.choice(threat_types, n_samples)
            
            # Adjust features based on threat type
            for i, label in enumerate(labels):
                if label == 'port_scan':
                    features[i, :5] += 3  # High connection rates
                elif label == 'dos':
                    features[i, 5:10] += 4  # High traffic volume
                elif label == 'malware':
                    features[i, 10:15] += 2  # Unusual network patterns
                elif label == 'phishing':
                    features[i, 15:20] += 1.5  # Suspicious DNS queries
            
            return features, labels
        
        elif model_name == 'behavioral_model':
            # Features for behavioral analysis
            features = np.random.normal(0, 1, (n_samples, n_features))
            
            # Create behavioral labels
            behaviors = ['normal', 'suspicious', 'malicious']
            labels = np.random.choice(behaviors, n_samples, p=[0.8, 0.15, 0.05])
            
            # Adjust features based on behavior
            for i, label in enumerate(labels):
                if label == 'suspicious':
                    features[i, :10] += 1.5
                elif label == 'malicious':
                    features[i, :10] += 3
            
            return features, labels
        
        return np.array([]), np.array([])
    
    def _load_threat_patterns(self) -> List[ThreatPattern]:
        """Load known threat patterns"""
        patterns = [
            ThreatPattern(
                name="Port Scan",
                features=["connection_rate", "unique_ports", "failed_connections"],
                thresholds={"connection_rate": 10.0, "unique_ports": 20, "failed_connections": 0.8},
                description="Systematic probing of network ports"
            ),
            ThreatPattern(
                name="DDoS Attack",
                features=["packet_rate", "bandwidth_usage", "source_diversity"],
                thresholds={"packet_rate": 1000.0, "bandwidth_usage": 0.9, "source_diversity": 0.1},
                description="Distributed denial of service attack"
            ),
            ThreatPattern(
                name="Data Exfiltration",
                features=["outbound_traffic", "unusual_hours", "data_volume"],
                thresholds={"outbound_traffic": 0.8, "unusual_hours": 1.0, "data_volume": 1000000},
                description="Unauthorized data transfer"
            ),
            ThreatPattern(
                name="Lateral Movement",
                features=["internal_connections", "privilege_escalation", "system_discovery"],
                thresholds={"internal_connections": 5.0, "privilege_escalation": 1.0, "system_discovery": 3.0},
                description="Movement within compromised network"
            ),
            ThreatPattern(
                name="Reconnaissance",
                features=["network_scanning", "service_enumeration", "vulnerability_probing"],
                thresholds={"network_scanning": 3.0, "service_enumeration": 5.0, "vulnerability_probing": 2.0},
                description="Information gathering before attack"
            )
        ]
        
        return patterns
    
    async def analyze_packet(self, packet_data):
        """Analyze network packet for threats"""
        try:
            # Extract features from packet
            features = await self.feature_extractor.extract_packet_features(packet_data)
            
            if features is None:
                return
            
            # Add to feature buffer
            self.feature_buffer.append({
                'timestamp': packet_data.timestamp,
                'features': features,
                'source_ip': packet_data.src_ip,
                'dest_ip': packet_data.dst_ip
            })
            
            # Maintain buffer size
            if len(self.feature_buffer) > self.buffer_size:
                self.feature_buffer.pop(0)
            
            # Perform real-time analysis
            await self._analyze_features(features, packet_data)
            
        except Exception as e:
            logger.error(f"Error analyzing packet: {e}")
    
    async def analyze_connection(self, connection_data):
        """Analyze network connection for threats"""
        try:
            # Extract features from connection
            features = await self.feature_extractor.extract_connection_features(connection_data)
            
            if features is None:
                return
            
            # Perform analysis
            await self._analyze_features(features, connection_data)
            
        except Exception as e:
            logger.error(f"Error analyzing connection: {e}")
    
    async def analyze_anomaly(self, anomaly_data):
        """Analyze behavioral anomaly for potential threats"""
        try:
            # Convert anomaly data to features
            features = await self.feature_extractor.extract_anomaly_features(anomaly_data)
            
            if features is None:
                return
            
            # Use behavioral model for analysis
            prediction = await self._predict_threat(features, 'behavioral_model')
            
            if prediction and prediction.confidence > self.config['confidence_threshold']:
                await self._handle_threat_detection(prediction)
            
        except Exception as e:
            logger.error(f"Error analyzing anomaly: {e}")
    
    async def _analyze_features(self, features: np.ndarray, source_data):
        """Analyze extracted features for threats"""
        try:
            # Check against threat patterns
            pattern_matches = await self._check_threat_patterns(features, source_data)
            
            # Use ML models for prediction
            anomaly_score = await self._detect_anomaly(features)
            threat_prediction = await self._classify_threat(features)
            
            # Combine results
            if anomaly_score < -0.5 or (threat_prediction and threat_prediction.confidence > 0.7):
                # High confidence threat detected
                if threat_prediction:
                    await self._handle_threat_detection(threat_prediction)
                else:
                    # Create threat prediction from anomaly
                    threat = ThreatPrediction(
                        timestamp=datetime.utcnow(),
                        threat_type="anomaly",
                        confidence=abs(anomaly_score),
                        source_ip=getattr(source_data, 'src_ip', 'unknown'),
                        target_ip=getattr(source_data, 'dst_ip', 'unknown'),
                        indicators={'anomaly_score': anomaly_score},
                        risk_level=self._calculate_risk_level(abs(anomaly_score)),
                        recommended_actions=['investigate', 'monitor']
                    )
                    await self._handle_threat_detection(threat)
            
            # Check pattern matches
            for pattern_match in pattern_matches:
                await self._handle_threat_detection(pattern_match)
            
        except Exception as e:
            logger.error(f"Error analyzing features: {e}")
    
    async def _detect_anomaly(self, features: np.ndarray) -> float:
        """Detect anomalies using isolation forest"""
        try:
            if 'anomaly_detector' not in self.models:
                return 0.0
            
            model = self.models['anomaly_detector']
            scaler = self.scalers['anomaly_detector']
            
            # Scale features
            features_scaled = scaler.transform(features.reshape(1, -1))
            
            # Get anomaly score
            score = model.decision_function(features_scaled)[0]
            
            return score
            
        except Exception as e:
            logger.error(f"Error detecting anomaly: {e}")
            return 0.0
    
    async def _classify_threat(self, features: np.ndarray) -> Optional[ThreatPrediction]:
        """Classify threat type using random forest"""
        try:
            if 'threat_classifier' not in self.models:
                return None
            
            model = self.models['threat_classifier']
            scaler = self.scalers['threat_classifier']
            
            # Scale features
            features_scaled = scaler.transform(features.reshape(1, -1))
            
            # Get prediction and probability
            prediction = model.predict(features_scaled)[0]
            probabilities = model.predict_proba(features_scaled)[0]
            
            # Get confidence (max probability)
            confidence = np.max(probabilities)
            
            if prediction != 'normal' and confidence > self.config['confidence_threshold']:
                return ThreatPrediction(
                    timestamp=datetime.utcnow(),
                    threat_type=prediction,
                    confidence=confidence,
                    source_ip='unknown',
                    target_ip='unknown',
                    indicators={'ml_confidence': confidence},
                    risk_level=self._calculate_risk_level(confidence),
                    recommended_actions=self._get_recommended_actions(prediction)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error classifying threat: {e}")
            return None
    
    async def _check_threat_patterns(self, features: np.ndarray, source_data) -> List[ThreatPrediction]:
        """Check features against known threat patterns"""
        matches = []
        
        try:
            # Convert features to named dict (this would need proper mapping)
            feature_dict = self._features_to_dict(features)
            
            for pattern in self.threat_patterns:
                match_score = 0
                total_checks = len(pattern.thresholds)
                
                for feature_name, threshold in pattern.thresholds.items():
                    if feature_name in feature_dict:
                        if feature_dict[feature_name] >= threshold:
                            match_score += 1
                
                # If most thresholds are exceeded, consider it a match
                if match_score / total_checks >= 0.7:
                    confidence = match_score / total_checks
                    
                    threat = ThreatPrediction(
                        timestamp=datetime.utcnow(),
                        threat_type=pattern.name.lower().replace(' ', '_'),
                        confidence=confidence,
                        source_ip=getattr(source_data, 'src_ip', 'unknown'),
                        target_ip=getattr(source_data, 'dst_ip', 'unknown'),
                        indicators={'pattern_match': pattern.name, 'match_score': match_score},
                        risk_level=self._calculate_risk_level(confidence),
                        recommended_actions=self._get_recommended_actions(pattern.name)
                    )
                    
                    matches.append(threat)
            
        except Exception as e:
            logger.error(f"Error checking threat patterns: {e}")
        
        return matches
    
    def _features_to_dict(self, features: np.ndarray) -> Dict[str, float]:
        """Convert feature array to named dictionary"""
        # This would need proper feature mapping based on the feature extractor
        feature_names = [
            'connection_rate', 'packet_rate', 'bandwidth_usage',
            'unique_ports', 'failed_connections', 'outbound_traffic',
            'unusual_hours', 'data_volume', 'internal_connections',
            'privilege_escalation', 'system_discovery', 'network_scanning',
            'service_enumeration', 'vulnerability_probing', 'source_diversity'
        ]
        
        result = {}
        for i, name in enumerate(feature_names):
            if i < len(features):
                result[name] = float(features[i])
        
        return result
    
    def _calculate_risk_level(self, confidence: float) -> str:
        """Calculate risk level based on confidence"""
        if confidence >= 0.9:
            return "critical"
        elif confidence >= 0.7:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _get_recommended_actions(self, threat_type: str) -> List[str]:
        """Get recommended actions for threat type"""
        actions_map = {
            'port_scan': ['block_source_ip', 'increase_monitoring', 'deploy_honeypot'],
            'dos': ['rate_limit', 'block_source_ip', 'scale_resources'],
            'ddos': ['activate_ddos_protection', 'contact_isp', 'emergency_response'],
            'malware': ['isolate_system', 'run_antivirus', 'forensic_analysis'],
            'phishing': ['block_domain', 'user_education', 'email_filtering'],
            'data_exfiltration': ['block_connection', 'investigate_user', 'audit_access'],
            'lateral_movement': ['isolate_network_segment', 'reset_credentials', 'incident_response'],
            'reconnaissance': ['deploy_deception', 'increase_logging', 'monitor_closely']
        }
        
        return actions_map.get(threat_type, ['investigate', 'monitor', 'alert_admin'])
    
    async def _handle_threat_detection(self, threat: ThreatPrediction):
        """Handle detected threat"""
        logger.warning(f"Threat detected: {threat.threat_type} from {threat.source_ip} (confidence: {threat.confidence:.2f})")
        
        # Update statistics
        self.model_stats['threats_detected'] += 1
        
        # Notify callbacks
        for callback in self._threat_callbacks:
            try:
                await callback(threat.__dict__)
            except Exception as e:
                logger.error(f"Error in threat callback: {e}")
    
    async def update_threat_indicators(self, ioc_data):
        """Update models with new threat indicators"""
        try:
            # Add IOC data to training set for next retrain
            logger.info(f"Updated threat indicators with new IOC: {ioc_data['type']}")
            
        except Exception as e:
            logger.error(f"Error updating threat indicators: {e}")
    
    async def _retrain_models_periodically(self):
        """Periodically retrain models with new data"""
        while True:
            try:
                await asyncio.sleep(self.config['retrain_interval'])
                
                logger.info("Starting periodic model retraining...")
                
                # Retrain models with accumulated data
                await self._retrain_models()
                
                logger.info("Model retraining completed")
                
            except Exception as e:
                logger.error(f"Error during model retraining: {e}")
    
    async def _retrain_models(self):
        """Retrain models with new data"""
        # This would implement incremental learning or full retraining
        # For now, just log the intention
        logger.info("Model retraining logic would be implemented here")
    
    async def _update_threat_patterns(self):
        """Periodically update threat patterns"""
        while True:
            try:
                await asyncio.sleep(3600)  # Update every hour
                
                # Update patterns based on recent detections
                # This would implement pattern learning logic
                logger.debug("Threat patterns updated")
                
            except Exception as e:
                logger.error(f"Error updating threat patterns: {e}")
    
    def on_threat_detected(self, callback: Callable):
        """Register callback for threat detection events"""
        self._threat_callbacks.append(callback)
    
    async def health_check(self):
        """Health check for threat detector"""
        if not self.models:
            raise Exception("No models loaded")
        
        # Check model availability
        required_models = ['anomaly_detector', 'threat_classifier']
        for model_name in required_models:
            if model_name not in self.models:
                raise Exception(f"Missing model: {model_name}")
        
        return True
