"""
Network-related database models
Models for network events and connections
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text, Boolean
from datetime import datetime

from ..database.connection import Base

class NetworkEvent(Base):
    """Model for network events and traffic analysis"""
    __tablename__ = "network_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # packet, connection, anomaly
    source_ip = Column(String(45), nullable=False, index=True)
    destination_ip = Column(String(45), nullable=False, index=True)
    source_port = Column(Integer)
    destination_port = Column(Integer)
    protocol = Column(String(20), nullable=False)
    packet_size = Column(Integer)
    flags = Column(JSON)  # Protocol-specific flags
    payload_hash = Column(String(64))  # SHA256 hash of payload
    payload_size = Column(Integer)
    interface = Column(String(50))  # Network interface
    direction = Column(String(20))  # inbound, outbound, internal
    risk_score = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    is_suspicious = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConnectionEvent(Base):
    """Model for network connection tracking"""
    __tablename__ = "connection_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    connection_id = Column(String(100), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # establish, data_transfer, close
    source_ip = Column(String(45), nullable=False, index=True)
    destination_ip = Column(String(45), nullable=False, index=True)
    source_port = Column(Integer)
    destination_port = Column(Integer)
    protocol = Column(String(20), nullable=False)
    connection_state = Column(String(20))  # ESTABLISHED, CLOSED, etc.
    bytes_sent = Column(Integer, default=0)
    bytes_received = Column(Integer, default=0)
    packets_sent = Column(Integer, default=0)
    packets_received = Column(Integer, default=0)
    duration = Column(Float)  # Connection duration in seconds
    is_encrypted = Column(Boolean, default=False)
    application_protocol = Column(String(50))  # HTTP, HTTPS, SSH, etc.
    user_agent = Column(String(500))
    process_name = Column(String(200))
    process_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class TrafficStatistics(Base):
    """Model for aggregated traffic statistics"""
    __tablename__ = "traffic_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    time_window = Column(String(20), nullable=False)  # 1min, 5min, 1hour, 1day
    source_ip = Column(String(45), index=True)
    destination_ip = Column(String(45), index=True)
    protocol = Column(String(20))
    port = Column(Integer)
    packet_count = Column(Integer, default=0)
    byte_count = Column(Integer, default=0)
    connection_count = Column(Integer, default=0)
    unique_destinations = Column(Integer, default=0)
    unique_sources = Column(Integer, default=0)
    average_packet_size = Column(Float, default=0.0)
    peak_rate = Column(Float, default=0.0)  # Peak packets/bytes per second
    anomaly_score = Column(Float, default=0.0)
    baseline_deviation = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class BehavioralBaseline(Base):
    """Model for storing behavioral baselines"""
    __tablename__ = "behavioral_baselines"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(String(100), nullable=False, index=True)  # IP, user, etc.
    entity_type = Column(String(50), nullable=False)  # ip, user, network
    baseline_type = Column(String(50), nullable=False)  # traffic, timing, protocol
    time_period = Column(String(20), nullable=False)  # hourly, daily, weekly
    baseline_data = Column(JSON)  # Statistical baseline information
    confidence_level = Column(Float, default=0.0)
    sample_size = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    next_update = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NetworkAnomaly(Base):
    """Model for network anomalies detected by behavioral analysis"""
    __tablename__ = "network_anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    anomaly_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    severity = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    baseline_deviation = Column(Float)
    anomaly_features = Column(JSON)  # Features that triggered the anomaly
    baseline_comparison = Column(JSON)  # Comparison with baseline
    related_events = Column(JSON)  # Related network events
    context_data = Column(JSON)  # Additional context information
    is_confirmed = Column(Boolean, default=False)
    is_false_positive = Column(Boolean, default=False)
    investigation_notes = Column(Text)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
