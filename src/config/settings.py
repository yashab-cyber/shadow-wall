"""
Configuration management for ShadowWall AI
Handles loading and validation of configuration settings
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator
import logging

logger = logging.getLogger(__name__)

class ShadowWallSettings(BaseSettings):
    """ShadowWall AI configuration settings"""
    
    # Application settings
    app_name: str = "ShadowWall AI"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4
    
    # Network monitoring
    network_interfaces: list = ["eth0"]
    capture_buffer_size: int = 65536
    packet_timeout: float = 1.0
    promiscuous_mode: bool = True
    
    # Machine Learning
    models_path: str = "models/"
    ml_confidence_threshold: float = 0.75
    ml_update_interval: int = 3600
    ml_retrain_interval: int = 86400
    
    # Behavioral analysis
    behavioral_window_size: int = 300
    behavioral_anomaly_threshold: float = 2.5
    behavioral_learning_rate: float = 0.001
    
    # Honeypots
    honeypots_enabled: bool = True
    honeypots_auto_deploy: bool = True
    honeypots_max_instances: int = 10
    honeypots_services: list = ["ssh", "http", "ftp", "telnet", "smtp"]
    
    # Database
    database_url: str = "sqlite:///data/shadowwall.db"
    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    
    # Elasticsearch
    elasticsearch_hosts: list = ["localhost:9200"]
    elasticsearch_index_prefix: str = "shadowwall"
    elasticsearch_retention_days: int = 30
    
    # Security
    api_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Dashboard
    dashboard_enabled: bool = True
    dashboard_refresh_interval: int = 5
    dashboard_max_events: int = 1000
    
    # Alerts
    alerts_enabled: bool = True
    
    # Sandbox
    sandbox_enabled: bool = True
    sandbox_isolation_level: str = "container"
    sandbox_max_sessions: int = 5
    sandbox_session_timeout: int = 3600
    
    # Performance
    max_memory_usage: str = "1GB"
    cpu_limit: int = 80
    disk_cache_size: str = "500MB"
    
    class Config:
        env_prefix = "SHADOWWALL_"
        case_sensitive = False

def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {}
    
    try:
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from {config_path}")
        return config_data or {}
        
    except Exception as e:
        logger.error(f"Error loading config file {config_path}: {e}")
        return {}

def flatten_config(config: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten nested configuration dictionary"""
    flattened = {}
    
    for key, value in config.items():
        new_key = f"{prefix}_{key}" if prefix else key
        
        if isinstance(value, dict):
            flattened.update(flatten_config(value, new_key))
        else:
            flattened[new_key] = value
    
    return flattened

def substitute_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Substitute environment variables in configuration values"""
    def substitute_value(value):
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.getenv(env_var, value)
        elif isinstance(value, dict):
            return {k: substitute_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [substitute_value(item) for item in value]
        else:
            return value
    
    return {key: substitute_value(value) for key, value in config.items()}

def get_settings() -> Dict[str, Any]:
    """Get ShadowWall configuration settings"""
    
    # Load configuration file
    config_path = os.getenv('SHADOWWALL_CONFIG', 'config/config.yaml')
    file_config = load_config_from_file(config_path)
    
    # Substitute environment variables
    file_config = substitute_env_vars(file_config)
    
    # Flatten the configuration
    flat_config = flatten_config(file_config)
    
    # Create Pydantic settings object with overrides
    try:
        settings = ShadowWallSettings(**flat_config)
    except Exception as e:
        logger.error(f"Error creating settings: {e}")
        settings = ShadowWallSettings()
    
    # Convert back to dictionary format expected by components
    config_dict = {
        'app': {
            'name': settings.app_name,
            'version': settings.app_version,
            'debug': settings.debug,
            'host': settings.host,
            'port': settings.port,
            'workers': settings.workers
        },
        'network': {
            'interfaces': settings.network_interfaces,
            'capture_buffer_size': settings.capture_buffer_size,
            'packet_timeout': settings.packet_timeout,
            'promiscuous_mode': settings.promiscuous_mode
        },
        'ml': {
            'models_path': settings.models_path,
            'threat_detection': {
                'confidence_threshold': settings.ml_confidence_threshold,
                'update_interval': settings.ml_update_interval,
                'retrain_interval': settings.ml_retrain_interval
            },
            'behavioral_analysis': {
                'window_size': settings.behavioral_window_size,
                'anomaly_threshold': settings.behavioral_anomaly_threshold,
                'learning_rate': settings.behavioral_learning_rate
            }
        },
        'honeypots': {
            'enabled': settings.honeypots_enabled,
            'auto_deploy': settings.honeypots_auto_deploy,
            'max_instances': settings.honeypots_max_instances,
            'services': settings.honeypots_services,
            'adaptive': {
                'enabled': True,
                'learning_window': 3600,
                'update_frequency': 300
            }
        },
        'database': {
            'url': settings.database_url,
            'echo': settings.database_echo,
            'pool_size': settings.database_pool_size,
            'max_overflow': settings.database_max_overflow
        },
        'redis': {
            'host': settings.redis_host,
            'port': settings.redis_port,
            'db': settings.redis_db,
            'password': settings.redis_password,
            'ssl': settings.redis_ssl
        },
        'elasticsearch': {
            'hosts': settings.elasticsearch_hosts,
            'index_prefix': settings.elasticsearch_index_prefix,
            'retention_days': settings.elasticsearch_retention_days
        },
        'security': {
            'api_key': settings.api_key,
            'jwt_secret': settings.jwt_secret,
            'cors_origins': settings.cors_origins
        },
        'dashboard': {
            'enabled': settings.dashboard_enabled,
            'refresh_interval': settings.dashboard_refresh_interval,
            'max_events_displayed': settings.dashboard_max_events
        },
        'alerts': {
            'enabled': settings.alerts_enabled
        },
        'sandbox': {
            'enabled': settings.sandbox_enabled,
            'isolation_level': settings.sandbox_isolation_level,
            'max_concurrent_sessions': settings.sandbox_max_sessions,
            'session_timeout': settings.sandbox_session_timeout
        },
        'performance': {
            'max_memory_usage': settings.max_memory_usage,
            'cpu_limit': settings.cpu_limit,
            'disk_cache_size': settings.disk_cache_size
        }
    }
    
    return config_dict

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration settings"""
    try:
        # Check required settings
        required_sections = ['app', 'network', 'ml', 'honeypots']
        for section in required_sections:
            if section not in config:
                logger.error(f"Missing required configuration section: {section}")
                return False
        
        # Validate port ranges
        if not (1 <= config['app']['port'] <= 65535):
            logger.error(f"Invalid port number: {config['app']['port']}")
            return False
        
        # Validate file paths
        models_path = Path(config['ml']['models_path'])
        models_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Configuration validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False
