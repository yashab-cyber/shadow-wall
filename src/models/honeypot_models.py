"""
Honeypot-related database models
Models for honeypot events and attacker profiles
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text, Boolean
from datetime import datetime

from ..database.connection import Base

class HoneypotEvent(Base):
    """Model for honeypot interaction events"""
    __tablename__ = "honeypot_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    honeypot_id = Column(String(100), nullable=False, index=True)
    honeypot_type = Column(String(50), nullable=False)  # ssh, http, ftp, etc.
    honeypot_port = Column(Integer, nullable=False)
    source_ip = Column(String(45), nullable=False, index=True)
    source_port = Column(Integer)
    interaction_type = Column(String(100))  # login_attempt, file_download, etc.
    duration = Column(Float)  # Interaction duration in seconds
    successful = Column(Boolean, default=False)
    commands = Column(JSON)  # List of commands executed
    payloads = Column(JSON)  # List of payloads/data sent
    user_agent = Column(String(500))
    session_data = Column(JSON)  # Additional session information
    geolocation = Column(JSON)  # Geographic information if available
    created_at = Column(DateTime, default=datetime.utcnow)

class AttackerProfile(Base):
    """Model for attacker behavioral profiles"""
    __tablename__ = "attacker_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String(45), nullable=False, unique=True, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    total_interactions = Column(Integer, default=0)
    successful_interactions = Column(Integer, default=0)
    targeted_services = Column(JSON)  # Services this attacker has targeted
    attack_patterns = Column(JSON)  # Behavioral patterns observed
    tools_used = Column(JSON)  # Tools and techniques identified
    persistence_score = Column(Float, default=0.0)  # How persistent is this attacker
    sophistication_score = Column(Float, default=0.0)  # Technical sophistication
    threat_level = Column(String(20), default="low")  # low, medium, high, critical
    is_bot = Column(Boolean, default=False)
    geolocation = Column(JSON)  # Geographic information
    isp_info = Column(JSON)  # ISP and network information
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HoneypotInstance(Base):
    """Model for honeypot instances"""
    __tablename__ = "honeypot_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(String(100), nullable=False, unique=True, index=True)
    service_type = Column(String(50), nullable=False)
    port = Column(Integer, nullable=False)
    ip_address = Column(String(45), nullable=False)
    status = Column(String(20), default="running")  # running, stopped, error
    configuration = Column(JSON)  # Honeypot configuration
    deployed_at = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime)
    total_interactions = Column(Integer, default=0)
    unique_attackers = Column(Integer, default=0)
    data_collected = Column(Integer, default=0)  # Amount of data collected in bytes
    effectiveness_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DeceptionEvent(Base):
    """Model for deception strategy events"""
    __tablename__ = "deception_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(50), nullable=False)  # deploy, modify, trigger, etc.
    target_ip = Column(String(45), index=True)
    deception_type = Column(String(100))  # fake_service, honeypot, breadcrumb, etc.
    strategy_id = Column(String(100))
    success = Column(Boolean, default=False)
    interaction_data = Column(JSON)
    effectiveness = Column(Float)  # How effective was this deception
    learning_data = Column(JSON)  # Data learned from this interaction
    created_at = Column(DateTime, default=datetime.utcnow)

class AttackSession(Base):
    """Model for tracking complete attack sessions"""
    __tablename__ = "attack_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    source_ip = Column(String(45), nullable=False, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration = Column(Float)  # Session duration in seconds
    total_events = Column(Integer, default=0)
    honeypots_interacted = Column(JSON)  # List of honeypots interacted with
    attack_progression = Column(JSON)  # Timeline of attack activities
    techniques_used = Column(JSON)  # MITRE ATT&CK techniques observed
    data_exfiltrated = Column(Integer, default=0)  # Bytes of data attempted to exfiltrate
    success_rate = Column(Float, default=0.0)  # Percentage of successful interactions
    risk_score = Column(Float, default=0.0)
    classification = Column(String(50))  # automated, manual, advanced_persistent, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
