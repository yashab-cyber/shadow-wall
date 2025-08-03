"""
Feature extraction utilities for machine learning models
Converts network data into numerical features for ML analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import ipaddress
from collections import defaultdict
import re

from ..utils.logger import get_logger

logger = get_logger(__name__)

class NetworkFeatureExtractor:
    """Extract features from network data for ML analysis"""
    
    def __init__(self):
        self.port_categories = self._initialize_port_categories()
        self.protocol_weights = self._initialize_protocol_weights()
        self.feature_cache = {}
        
    def _initialize_port_categories(self) -> Dict[str, List[int]]:
        """Initialize port categories for feature extraction"""
        return {
            'web': [80, 443, 8080, 8443, 8000, 8001],
            'mail': [25, 110, 143, 993, 995, 587],
            'file_transfer': [21, 22, 989, 990],
            'database': [1433, 1521, 3306, 5432, 6379, 27017],
            'remote_access': [22, 23, 3389, 5900, 5901],
            'dns': [53],
            'dhcp': [67, 68],
            'snmp': [161, 162],
            'system': [1, 7, 9, 13, 17, 19, 37],
            'high_ports': list(range(49152, 65536))
        }
    
    def _initialize_protocol_weights(self) -> Dict[str, float]:
        """Initialize protocol weights for anomaly detection"""
        return {
            'TCP': 1.0,
            'UDP': 0.8,
            'ICMP': 0.6,
            'ARP': 0.4,
            'IGMP': 0.3
        }
    
    async def extract_packet_features(self, packet_data) -> Optional[np.ndarray]:
        """Extract features from a network packet"""
        try:
            features = []
            
            # Basic packet features
            features.extend(self._extract_basic_packet_features(packet_data))
            
            # IP address features
            features.extend(self._extract_ip_features(packet_data))
            
            # Port features
            features.extend(self._extract_port_features(packet_data))
            
            # Protocol features
            features.extend(self._extract_protocol_features(packet_data))
            
            # Timing features
            features.extend(self._extract_timing_features(packet_data))
            
            # Payload features
            features.extend(self._extract_payload_features(packet_data))
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Error extracting packet features: {e}")
            return None
    
    async def extract_connection_features(self, connection_data) -> Optional[np.ndarray]:
        """Extract features from connection data"""
        try:
            features = []
            
            # Connection duration
            features.append(getattr(connection_data, 'connection_duration', 0.0))
            
            # Bytes transferred
            features.append(float(connection_data.bytes_transferred))
            
            # Port analysis
            if hasattr(connection_data, 'dst_port') and connection_data.dst_port:
                features.extend(self._analyze_port(connection_data.dst_port))
            else:
                features.extend([0.0] * 5)  # Add zeros for missing port features
            
            # Protocol features
            protocol_features = self._get_protocol_features(connection_data.protocol)
            features.extend(protocol_features)
            
            # Timing features
            hour = connection_data.timestamp.hour
            features.extend([
                float(hour),
                1.0 if 9 <= hour <= 17 else 0.0,  # Business hours
                1.0 if hour < 6 or hour > 22 else 0.0,  # Night time
                float(connection_data.timestamp.weekday()),
            ])
            
            # IP address features
            src_ip_features = self._extract_single_ip_features(connection_data.src_ip)
            dst_ip_features = self._extract_single_ip_features(connection_data.dst_ip)
            features.extend(src_ip_features)
            features.extend(dst_ip_features)
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Error extracting connection features: {e}")
            return None
    
    async def extract_anomaly_features(self, anomaly_data) -> Optional[np.ndarray]:
        """Extract features from anomaly data"""
        try:
            features = []
            
            # Anomaly severity
            features.append(anomaly_data.get('severity', 0.0))
            
            # Anomaly type encoding
            anomaly_types = ['behavioral', 'network', 'temporal', 'volume', 'pattern']
            anomaly_type = anomaly_data.get('type', 'unknown')
            features.extend([1.0 if anomaly_type == t else 0.0 for t in anomaly_types])
            
            # Confidence score
            features.append(anomaly_data.get('confidence', 0.0))
            
            # Baseline deviation
            features.append(anomaly_data.get('baseline_deviation', 0.0))
            
            # Entity features
            entity_type = anomaly_data.get('entity_type', 'unknown')
            entity_types = ['ip', 'user', 'network', 'service']
            features.extend([1.0 if entity_type == t else 0.0 for t in entity_types])
            
            # Time-based features
            timestamp = anomaly_data.get('timestamp', datetime.utcnow())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            features.extend([
                float(timestamp.hour),
                float(timestamp.weekday()),
                1.0 if timestamp.hour < 6 or timestamp.hour > 22 else 0.0
            ])
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Error extracting anomaly features: {e}")
            return None
    
    def _extract_basic_packet_features(self, packet_data) -> List[float]:
        """Extract basic packet features"""
        features = []
        
        # Packet size
        features.append(float(packet_data.size))
        
        # Size categories
        features.append(1.0 if packet_data.size < 64 else 0.0)    # Tiny packet
        features.append(1.0 if 64 <= packet_data.size < 512 else 0.0)  # Small packet
        features.append(1.0 if 512 <= packet_data.size < 1500 else 0.0)  # Medium packet
        features.append(1.0 if packet_data.size >= 1500 else 0.0)  # Large packet
        
        return features
    
    def _extract_ip_features(self, packet_data) -> List[float]:
        """Extract IP address-based features"""
        features = []
        
        # Source IP features
        src_features = self._extract_single_ip_features(packet_data.src_ip)
        features.extend(src_features)
        
        # Destination IP features
        dst_features = self._extract_single_ip_features(packet_data.dst_ip)
        features.extend(dst_features)
        
        # IP relationship features
        features.append(1.0 if packet_data.src_ip == packet_data.dst_ip else 0.0)  # Loopback
        features.append(self._calculate_ip_distance(packet_data.src_ip, packet_data.dst_ip))
        
        return features
    
    def _extract_single_ip_features(self, ip_str: str) -> List[float]:
        """Extract features from a single IP address"""
        features = []
        
        try:
            ip = ipaddress.ip_address(ip_str)
            
            # IP type features
            features.append(1.0 if ip.is_private else 0.0)
            features.append(1.0 if ip.is_loopback else 0.0)
            features.append(1.0 if ip.is_multicast else 0.0)
            features.append(1.0 if ip.is_reserved else 0.0)
            
            # IP octets (for IPv4) or normalized segments (for IPv6)
            if ip.version == 4:
                octets = [int(x) for x in ip_str.split('.')]
                features.extend([float(x) / 255.0 for x in octets])
            else:
                # For IPv6, use hash-based features
                ip_hash = int(hashlib.md5(ip_str.encode()).hexdigest()[:8], 16)
                features.extend([
                    float((ip_hash >> 24) & 0xFF) / 255.0,
                    float((ip_hash >> 16) & 0xFF) / 255.0,
                    float((ip_hash >> 8) & 0xFF) / 255.0,
                    float(ip_hash & 0xFF) / 255.0
                ])
            
        except ValueError:
            # Invalid IP address
            features.extend([0.0] * 8)  # 4 type features + 4 octet features
        
        return features
    
    def _extract_port_features(self, packet_data) -> List[float]:
        """Extract port-based features"""
        features = []
        
        # Source port features
        if hasattr(packet_data, 'src_port') and packet_data.src_port:
            features.extend(self._analyze_port(packet_data.src_port))
        else:
            features.extend([0.0] * 5)
        
        # Destination port features
        if hasattr(packet_data, 'dst_port') and packet_data.dst_port:
            features.extend(self._analyze_port(packet_data.dst_port))
        else:
            features.extend([0.0] * 5)
        
        return features
    
    def _analyze_port(self, port: int) -> List[float]:
        """Analyze port characteristics"""
        features = []
        
        # Port number normalized
        features.append(float(port) / 65535.0)
        
        # Port categories
        is_well_known = 1.0 if port < 1024 else 0.0
        is_registered = 1.0 if 1024 <= port < 49152 else 0.0
        is_dynamic = 1.0 if port >= 49152 else 0.0
        
        features.extend([is_well_known, is_registered, is_dynamic])
        
        # Service category (simplified)
        service_category = 0.0
        for category, ports in self.port_categories.items():
            if port in ports:
                service_category = hash(category) % 100 / 100.0
                break
        
        features.append(service_category)
        
        return features
    
    def _extract_protocol_features(self, packet_data) -> List[float]:
        """Extract protocol-based features"""
        features = []
        
        protocol = packet_data.protocol
        
        # One-hot encoding for common protocols
        common_protocols = ['TCP', 'UDP', 'ICMP', 'ARP']
        for proto in common_protocols:
            features.append(1.0 if protocol == proto else 0.0)
        
        # Protocol weight
        weight = self.protocol_weights.get(protocol, 0.1)
        features.append(weight)
        
        # TCP flags (if applicable)
        if protocol == 'TCP' and hasattr(packet_data, 'flags'):
            tcp_flags = ['syn', 'ack', 'fin', 'rst', 'psh', 'urg']
            for flag in tcp_flags:
                features.append(1.0 if packet_data.flags.get(flag, False) else 0.0)
        else:
            features.extend([0.0] * 6)
        
        return features
    
    def _extract_timing_features(self, packet_data) -> List[float]:
        """Extract timing-based features"""
        features = []
        
        timestamp = packet_data.timestamp
        
        # Time of day features
        hour = timestamp.hour
        minute = timestamp.minute
        
        features.extend([
            float(hour) / 24.0,
            float(minute) / 60.0,
            float(timestamp.weekday()) / 7.0,
        ])
        
        # Time category features
        features.append(1.0 if 9 <= hour <= 17 else 0.0)  # Business hours
        features.append(1.0 if hour < 6 or hour > 22 else 0.0)  # Night time
        features.append(1.0 if timestamp.weekday() >= 5 else 0.0)  # Weekend
        
        return features
    
    def _extract_payload_features(self, packet_data) -> List[float]:
        """Extract payload-based features"""
        features = []
        
        payload = packet_data.payload_preview
        
        if payload:
            # Payload entropy
            entropy = self._calculate_entropy(payload)
            features.append(entropy)
            
            # Character distribution features
            hex_chars = len([c for c in payload if c in '0123456789abcdefABCDEF'])
            features.append(float(hex_chars) / max(len(payload), 1))
            
            # Common patterns
            patterns = [
                r'[0-9a-fA-F]{32}',  # MD5-like hashes
                r'[0-9a-fA-F]{40}',  # SHA1-like hashes
                r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?',  # Base64
            ]
            
            for pattern in patterns:
                matches = len(re.findall(pattern, payload))
                features.append(float(matches))
            
        else:
            features.extend([0.0] * 5)  # No payload features
        
        return features
    
    def _get_protocol_features(self, protocol: str) -> List[float]:
        """Get protocol-specific features"""
        features = []
        
        # Protocol encoding
        protocols = ['TCP', 'UDP', 'ICMP', 'ARP', 'IGMP']
        for proto in protocols:
            features.append(1.0 if protocol == proto else 0.0)
        
        return features
    
    def _calculate_ip_distance(self, ip1: str, ip2: str) -> float:
        """Calculate normalized distance between IP addresses"""
        try:
            addr1 = ipaddress.ip_address(ip1)
            addr2 = ipaddress.ip_address(ip2)
            
            if addr1.version != addr2.version:
                return 1.0  # Maximum distance for different IP versions
            
            # Simple distance calculation
            if addr1.version == 4:
                int1 = int(addr1)
                int2 = int(addr2)
                max_distance = 2**32 - 1
                distance = abs(int1 - int2) / max_distance
            else:
                # For IPv6, use a simplified hash-based distance
                hash1 = int(hashlib.md5(ip1.encode()).hexdigest()[:8], 16)
                hash2 = int(hashlib.md5(ip2.encode()).hexdigest()[:8], 16)
                distance = abs(hash1 - hash2) / (2**32 - 1)
            
            return min(distance, 1.0)
            
        except:
            return 1.0  # Maximum distance on error
    
    def _calculate_entropy(self, data: str) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0
        
        # Count character frequencies
        char_counts = defaultdict(int)
        for char in data:
            char_counts[char] += 1
        
        # Calculate entropy
        entropy = 0.0
        length = len(data)
        
        for count in char_counts.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy
