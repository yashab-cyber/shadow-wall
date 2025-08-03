"""
Threat-related database models
Models for threat events, IOCs, and threat patterns
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime

from ..database.connection import Base

class ThreatEvent(Base):
    """Model for threat detection events"""
    __tablename__ = "threat_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    threat_type = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    source_ip = Column(String(45), index=True)  # IPv6 compatible
    target_ip = Column(String(45), index=True)
    source_port = Column(Integer)
    target_port = Column(Integer)
    protocol = Column(String(20))
    severity = Column(String(20), index=True)  # low, medium, high, critical
    description = Column(Text)
    indicators = Column(JSON)  # Dictionary of threat indicators
    recommended_actions = Column(JSON)  # List of recommended actions
    status = Column(String(20), default="active")  # active, resolved, false_positive
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IOC(Base):
    """Model for Indicators of Compromise"""
    __tablename__ = "iocs"
    
    id = Column(Integer, primary_key=True, index=True)
    ioc_type = Column(String(50), nullable=False, index=True)  # ip, domain, hash, etc.
    value = Column(String(500), nullable=False, index=True)
    confidence = Column(Float, default=0.5)
    source = Column(String(100))  # Source of the IOC
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    times_seen = Column(Integer, default=1)
    threat_types = Column(JSON)  # Associated threat types
    context = Column(JSON)  # Additional context information
    is_active = Column(Boolean, default=True)
    expiry_date = Column(DateTime)
    tags = Column(JSON)  # List of tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ThreatPattern(Base):
    """Model for threat patterns and signatures"""
    __tablename__ = "threat_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    pattern_type = Column(String(50), nullable=False)  # behavioral, network, temporal
    description = Column(Text)
    pattern_data = Column(JSON)  # Pattern definition and rules
    threshold_config = Column(JSON)  # Threshold configuration
    severity = Column(String(20), default="medium")
    is_enabled = Column(Boolean, default=True)
    detection_count = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)
    accuracy_score = Column(Float)
    last_triggered = Column(DateTime)
    created_by = Column(String(100))
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ThreatIntelligence(Base):
    """Model for threat intelligence feeds and data"""
    __tablename__ = "threat_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    feed_name = Column(String(100), nullable=False, index=True)
    feed_url = Column(String(500))
    intel_type = Column(String(50), nullable=False)  # ioc, campaign, actor, etc.
    data = Column(JSON)  # Intelligence data
    confidence = Column(Float)
    source_reliability = Column(String(20))  # A, B, C, D, E, F
    information_credibility = Column(String(20))  # 1, 2, 3, 4, 5, 6
    tlp_marking = Column(String(20))  # TLP:WHITE, TLP:GREEN, TLP:AMBER, TLP:RED
    published_date = Column(DateTime)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AttackCampaign(Base):
    """Model for tracking attack campaigns"""
    __tablename__ = "attack_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text)
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    threat_actors = Column(JSON)  # List of associated threat actors
    ttps = Column(JSON)  # Tactics, Techniques, and Procedures
    targets = Column(JSON)  # Target information
    iocs = Column(JSON)  # Associated IOCs
    severity = Column(String(20), default="medium")
    status = Column(String(20), default="active")  # active, dormant, concluded
    confidence = Column(Float, default=0.5)
    attribution = Column(JSON)  # Attribution information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
