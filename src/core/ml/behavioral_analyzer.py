"""
Behavioral Analysis Engine
Uses machine learning to detect anomalous user and network behavior
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque

from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from ...utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class BehavioralAnomaly:
    """Behavioral anomaly detection result"""
    timestamp: datetime
    entity_id: str  # IP address, user ID, etc.
    entity_type: str  # 'ip', 'user', 'network'
    anomaly_type: str
    severity: float
    features: Dict[str, float]
    description: str
    baseline_deviation: float

@dataclass
class EntityProfile:
    """Profile for a network entity (IP, user, etc.)"""
    entity_id: str
    entity_type: str
    first_seen: datetime
    last_seen: datetime
    activity_patterns: Dict[str, Any]
    baseline_features: Dict[str, float]
    anomaly_history: List[BehavioralAnomaly]

class BehavioralAnalyzer:
    """Advanced behavioral analysis using machine learning"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.window_size = config['window_size']
        self.anomaly_threshold = config['anomaly_threshold']
        
        # Entity profiles and tracking
        self.entity_profiles: Dict[str, EntityProfile] = {}
        self.activity_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.window_size))
        
        # ML models for behavioral analysis
        self.anomaly_detectors = {}
        self.scalers = {}
        
        # Feature extractors
        self.feature_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Event callbacks
        self._anomaly_callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            'entities_tracked': 0,
            'anomalies_detected': 0,
            'patterns_learned': 0
        }
    
    async def initialize(self):
        """Initialize behavioral analysis models"""
        logger.info("Initializing behavioral analysis engine...")
        
        # Initialize anomaly detectors for different entity types
        await self._initialize_anomaly_detectors()
        
        # Start background tasks
        asyncio.create_task(self._update_baselines_periodically())
        asyncio.create_task(self._cleanup_old_data())
        
        logger.info("Behavioral analysis engine initialized")
    
    async def _initialize_anomaly_detectors(self):
        """Initialize anomaly detection models for different entity types"""
        entity_types = ['ip', 'user', 'network']
        
        for entity_type in entity_types:
            # Create isolation forest for anomaly detection
            detector = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            
            # Create scaler for feature normalization
            scaler = StandardScaler()
            
            self.anomaly_detectors[entity_type] = detector
            self.scalers[entity_type] = scaler
            
            logger.info(f"Initialized anomaly detector for {entity_type}")
    
    async def process_packet(self, packet_data):
        """Process network packet for behavioral analysis"""
        try:
            # Extract entity information
            src_entity = packet_data.src_ip
            dst_entity = packet_data.dst_ip
            
            # Update entity profiles
            await self._update_entity_profile(src_entity, 'ip', packet_data)
            await self._update_entity_profile(dst_entity, 'ip', packet_data)
            
            # Extract behavioral features
            src_features = await self._extract_ip_features(src_entity, packet_data)
            dst_features = await self._extract_ip_features(dst_entity, packet_data)
            
            # Analyze for anomalies
            if src_features:
                await self._analyze_entity_behavior(src_entity, 'ip', src_features)
            
            if dst_features:
                await self._analyze_entity_behavior(dst_entity, 'ip', dst_features)
            
        except Exception as e:
            logger.error(f"Error processing packet for behavioral analysis: {e}")
    
    async def process_connection(self, connection_data):
        """Process network connection for behavioral analysis"""
        try:
            # Extract connection features
            features = await self._extract_connection_features(connection_data)
            
            if features:
                # Analyze connection behavior
                connection_id = f"{connection_data.src_ip}:{connection_data.src_port}-{connection_data.dst_ip}:{connection_data.dst_port}"
                await self._analyze_entity_behavior(connection_id, 'connection', features)
            
        except Exception as e:
            logger.error(f"Error processing connection for behavioral analysis: {e}")
    
    async def learn_from_interaction(self, interaction_data):
        """Learn from honeypot interactions"""
        try:
            attacker_ip = interaction_data['source_ip']
            
            # Create attacker profile
            await self._update_entity_profile(attacker_ip, 'attacker', interaction_data)
            
            # Extract attacker behavioral features
            features = await self._extract_attacker_features(interaction_data)
            
            if features:
                await self._analyze_entity_behavior(attacker_ip, 'attacker', features)
                
                # Update attack pattern models
                await self._learn_attack_patterns(attacker_ip, features)
            
        except Exception as e:
            logger.error(f"Error learning from interaction: {e}")
    
    async def _update_entity_profile(self, entity_id: str, entity_type: str, data):
        """Update or create entity profile"""
        current_time = datetime.utcnow()
        
        if entity_id not in self.entity_profiles:
            # Create new profile
            self.entity_profiles[entity_id] = EntityProfile(
                entity_id=entity_id,
                entity_type=entity_type,
                first_seen=current_time,
                last_seen=current_time,
                activity_patterns={},
                baseline_features={},
                anomaly_history=[]
            )
            self.stats['entities_tracked'] += 1
        else:
            # Update existing profile
            self.entity_profiles[entity_id].last_seen = current_time
        
        # Add activity to window
        self.activity_windows[entity_id].append({
            'timestamp': current_time,
            'data': data
        })
    
    async def _extract_ip_features(self, ip_address: str, packet_data) -> Optional[Dict[str, float]]:
        """Extract behavioral features for an IP address"""
        try:
            features = {}
            
            # Get recent activity for this IP
            recent_activity = list(self.activity_windows[ip_address])
            
            if len(recent_activity) < 2:
                return None
            
            # Time-based features
            current_time = datetime.utcnow()
            time_since_last = (current_time - recent_activity[-2]['timestamp']).total_seconds()
            features['time_since_last_packet'] = time_since_last
            
            # Packet rate features
            if len(recent_activity) >= 10:
                timestamps = [activity['timestamp'] for activity in recent_activity[-10:]]
                time_diffs = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                             for i in range(1, len(timestamps))]
                features['avg_packet_interval'] = np.mean(time_diffs)
                features['packet_rate_variance'] = np.var(time_diffs)
            
            # Protocol distribution
            protocols = [activity['data'].protocol for activity in recent_activity[-50:]]
            unique_protocols = len(set(protocols))
            features['protocol_diversity'] = unique_protocols
            
            # Port usage patterns
            if hasattr(packet_data, 'dst_port') and packet_data.dst_port:
                dst_ports = [activity['data'].dst_port for activity in recent_activity[-50:] 
                           if hasattr(activity['data'], 'dst_port') and activity['data'].dst_port]
                unique_ports = len(set(dst_ports))
                features['port_diversity'] = unique_ports
                
                # Check for port scanning behavior
                if unique_ports > 10 and len(dst_ports) > 20:
                    features['potential_port_scan'] = unique_ports / len(dst_ports)
                else:
                    features['potential_port_scan'] = 0.0
            
            # Packet size patterns
            packet_sizes = [activity['data'].size for activity in recent_activity[-20:]]
            features['avg_packet_size'] = np.mean(packet_sizes)
            features['packet_size_variance'] = np.var(packet_sizes)
            
            # Timing patterns (check for regular intervals)
            if len(recent_activity) >= 5:
                intervals = [(recent_activity[i]['timestamp'] - recent_activity[i-1]['timestamp']).total_seconds()
                           for i in range(1, min(len(recent_activity), 20))]
                features['timing_regularity'] = 1.0 / (1.0 + np.var(intervals))
            
            # Geographic/network features (simplified)
            features['ip_entropy'] = self._calculate_ip_entropy(ip_address)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting IP features: {e}")
            return None
    
    async def _extract_connection_features(self, connection_data) -> Optional[Dict[str, float]]:
        """Extract features from connection data"""
        try:
            features = {}
            
            # Connection duration
            if hasattr(connection_data, 'connection_duration') and connection_data.connection_duration:
                features['connection_duration'] = connection_data.connection_duration
            
            # Data transfer patterns
            features['bytes_transferred'] = connection_data.bytes_transferred
            
            # Port analysis
            if connection_data.dst_port:
                features['dst_port'] = connection_data.dst_port
                features['is_common_port'] = 1.0 if connection_data.dst_port in [80, 443, 22, 21, 25, 53] else 0.0
                features['is_high_port'] = 1.0 if connection_data.dst_port > 1024 else 0.0
            
            # Protocol features
            features['is_tcp'] = 1.0 if connection_data.protocol == 'TCP' else 0.0
            features['is_udp'] = 1.0 if connection_data.protocol == 'UDP' else 0.0
            
            # Timing features
            hour = connection_data.timestamp.hour
            features['hour_of_day'] = hour
            features['is_business_hours'] = 1.0 if 9 <= hour <= 17 else 0.0
            features['is_night_time'] = 1.0 if hour < 6 or hour > 22 else 0.0
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting connection features: {e}")
            return None
    
    async def _extract_attacker_features(self, interaction_data) -> Optional[Dict[str, float]]:
        """Extract behavioral features from attacker interactions"""
        try:
            features = {}
            
            # Service interaction patterns
            features['service_type'] = hash(interaction_data['service']) % 1000
            features['interaction_duration'] = interaction_data.get('duration', 0.0)
            
            # Command patterns (if available)
            if 'commands' in interaction_data:
                commands = interaction_data['commands']
                features['num_commands'] = len(commands)
                features['unique_commands'] = len(set(commands))
                features['command_diversity'] = len(set(commands)) / max(len(commands), 1)
            
            # Time-based features
            hour = interaction_data['timestamp'].hour
            features['hour_of_day'] = hour
            features['is_night_attack'] = 1.0 if hour < 6 or hour > 22 else 0.0
            
            # Persistence indicators
            attacker_ip = interaction_data['source_ip']
            if attacker_ip in self.entity_profiles:
                profile = self.entity_profiles[attacker_ip]
                features['previous_interactions'] = len(profile.anomaly_history)
                features['time_since_first_seen'] = (datetime.utcnow() - profile.first_seen).total_seconds()
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting attacker features: {e}")
            return None
    
    async def _analyze_entity_behavior(self, entity_id: str, entity_type: str, features: Dict[str, float]):
        """Analyze entity behavior for anomalies"""
        try:
            # Convert features to array
            feature_array = np.array(list(features.values())).reshape(1, -1)
            
            # Get or train model for this entity type
            if entity_type not in self.anomaly_detectors:
                await self._initialize_anomaly_detectors()
            
            detector = self.anomaly_detectors[entity_type]
            scaler = self.scalers[entity_type]
            
            # Update feature history
            self.feature_history[f"{entity_type}_{entity_id}"].append(features)
            
            # Check if we have enough data for analysis
            feature_history = list(self.feature_history[f"{entity_type}_{entity_id}"])
            if len(feature_history) < 10:
                return  # Not enough data for reliable analysis
            
            # Prepare training data from recent history
            training_features = []
            for hist_features in feature_history[-100:]:  # Use last 100 observations
                training_features.append(list(hist_features.values()))
            
            training_array = np.array(training_features)
            
            # Fit scaler and detector if not already done or if retraining
            if not hasattr(detector, 'estimators_') or len(feature_history) % 50 == 0:
                # Retrain periodically
                training_scaled = scaler.fit_transform(training_array)
                detector.fit(training_scaled)
            
            # Scale current features
            try:
                feature_scaled = scaler.transform(feature_array)
            except:
                # If scaling fails, skip this analysis
                return
            
            # Detect anomaly
            anomaly_score = detector.decision_function(feature_scaled)[0]
            is_anomaly = detector.predict(feature_scaled)[0] == -1
            
            # Calculate baseline deviation
            if len(feature_history) > 1:
                recent_features = np.array([list(f.values()) for f in feature_history[-20:]])
                baseline_mean = np.mean(recent_features, axis=0)
                current_features = np.array(list(features.values()))
                deviation = np.linalg.norm(current_features - baseline_mean)
            else:
                deviation = 0.0
            
            # Check if anomaly exceeds threshold
            if is_anomaly and abs(anomaly_score) > self.anomaly_threshold:
                await self._handle_anomaly_detection(
                    entity_id, entity_type, anomaly_score, features, deviation
                )
            
        except Exception as e:
            logger.error(f"Error analyzing entity behavior: {e}")
    
    async def _handle_anomaly_detection(self, entity_id: str, entity_type: str, 
                                      anomaly_score: float, features: Dict[str, float], 
                                      deviation: float):
        """Handle detected behavioral anomaly"""
        try:
            # Determine anomaly type based on features
            anomaly_type = self._classify_anomaly_type(features)
            
            # Calculate severity
            severity = min(abs(anomaly_score) / 2.0, 1.0)
            
            # Create anomaly object
            anomaly = BehavioralAnomaly(
                timestamp=datetime.utcnow(),
                entity_id=entity_id,
                entity_type=entity_type,
                anomaly_type=anomaly_type,
                severity=severity,
                features=features,
                description=f"{anomaly_type} detected for {entity_type} {entity_id}",
                baseline_deviation=deviation
            )
            
            # Update entity profile
            if entity_id in self.entity_profiles:
                self.entity_profiles[entity_id].anomaly_history.append(anomaly)
            
            # Update statistics
            self.stats['anomalies_detected'] += 1
            
            logger.warning(f"Behavioral anomaly detected: {anomaly.description} (severity: {severity:.2f})")
            
            # Notify callbacks
            for callback in self._anomaly_callbacks:
                try:
                    await callback(anomaly.__dict__)
                except Exception as e:
                    logger.error(f"Error in anomaly callback: {e}")
            
        except Exception as e:
            logger.error(f"Error handling anomaly detection: {e}")
    
    def _classify_anomaly_type(self, features: Dict[str, float]) -> str:
        """Classify the type of anomaly based on features"""
        # Simple rule-based classification
        if features.get('potential_port_scan', 0) > 0.1:
            return "port_scanning"
        elif features.get('packet_rate_variance', 0) > 10:
            return "irregular_traffic_pattern"
        elif features.get('is_night_attack', 0) == 1.0:
            return "off_hours_activity"
        elif features.get('protocol_diversity', 0) > 5:
            return "protocol_anomaly"
        elif features.get('timing_regularity', 0) > 0.9:
            return "automated_behavior"
        else:
            return "general_anomaly"
    
    def _calculate_ip_entropy(self, ip_address: str) -> float:
        """Calculate entropy of IP address (simple heuristic)"""
        octets = ip_address.split('.')
        try:
            # Simple entropy calculation based on octet values
            values = [int(octet) for octet in octets]
            entropy = -sum(v/255 * np.log2(v/255 + 1e-10) for v in values if v > 0)
            return entropy
        except:
            return 0.0
    
    async def _learn_attack_patterns(self, attacker_ip: str, features: Dict[str, float]):
        """Learn from attack patterns for better detection"""
        try:
            # Update attack pattern models
            # This would implement more sophisticated pattern learning
            self.stats['patterns_learned'] += 1
            
            logger.debug(f"Learning attack patterns from {attacker_ip}")
            
        except Exception as e:
            logger.error(f"Error learning attack patterns: {e}")
    
    async def _update_baselines_periodically(self):
        """Periodically update behavioral baselines"""
        while True:
            try:
                await asyncio.sleep(3600)  # Update every hour
                
                logger.debug("Updating behavioral baselines...")
                
                # Update baselines for all tracked entities
                for entity_id, profile in self.entity_profiles.items():
                    await self._update_entity_baseline(entity_id, profile)
                
                logger.debug("Behavioral baselines updated")
                
            except Exception as e:
                logger.error(f"Error updating baselines: {e}")
    
    async def _update_entity_baseline(self, entity_id: str, profile: EntityProfile):
        """Update baseline features for an entity"""
        try:
            # Get recent feature history
            feature_key = f"{profile.entity_type}_{entity_id}"
            if feature_key in self.feature_history:
                recent_features = list(self.feature_history[feature_key])[-50:]
                
                if len(recent_features) > 10:
                    # Calculate new baseline
                    feature_arrays = [list(f.values()) for f in recent_features]
                    baseline = np.mean(feature_arrays, axis=0)
                    
                    # Update profile baseline
                    feature_names = list(recent_features[0].keys())
                    profile.baseline_features = {
                        name: value for name, value in zip(feature_names, baseline)
                    }
            
        except Exception as e:
            logger.error(f"Error updating entity baseline: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old data to prevent memory leaks"""
        while True:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=7)
                
                # Clean up old entity profiles
                entities_to_remove = []
                for entity_id, profile in self.entity_profiles.items():
                    if profile.last_seen < cutoff_time:
                        entities_to_remove.append(entity_id)
                
                for entity_id in entities_to_remove:
                    del self.entity_profiles[entity_id]
                    if entity_id in self.activity_windows:
                        del self.activity_windows[entity_id]
                
                logger.debug(f"Cleaned up {len(entities_to_remove)} old entity profiles")
                
            except Exception as e:
                logger.error(f"Error during data cleanup: {e}")
    
    def on_anomaly_detected(self, callback: Callable):
        """Register callback for anomaly detection events"""
        self._anomaly_callbacks.append(callback)
    
    async def health_check(self):
        """Health check for behavioral analyzer"""
        if not self.anomaly_detectors:
            raise Exception("No anomaly detectors initialized")
        
        return True
