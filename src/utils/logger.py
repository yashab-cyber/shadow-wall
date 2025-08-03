"""
Logging utilities for ShadowWall AI
Provides structured logging with different output formats
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from pathlib import Path
import structlog

def setup_logging(config: dict = None):
    """Setup structured logging for ShadowWall AI"""
    if config is None:
        config = {
            'level': 'INFO',
            'format': 'json',
            'file': 'logs/shadowwall.log',
            'max_file_size': '100MB',
            'backup_count': 5
        }
    
    # Create logs directory
    log_file = Path(config['file'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if config['format'] == 'json' else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Setup standard logging
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config['level'].upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if config['format'] == 'json':
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config['file'],
        maxBytes=_parse_size(config['max_file_size']),
        backupCount=config['backup_count']
    )
    
    if config['format'] == 'json':
        file_handler.setFormatter(JSONFormatter())
    else:
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
    logger.addHandler(file_handler)

def _parse_size(size_str: str) -> int:
    """Parse size string like '100MB' to bytes"""
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
    
    size_str = size_str.upper().strip()
    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                number_part = size_str[:-len(unit)].strip()
                return int(number_part) * multiplier
            except ValueError:
                # If parsing fails, return default 10MB
                return 10 * 1024 * 1024
    
    try:
        return int(size_str)  # Assume bytes if no unit
    except ValueError:
        return 10 * 1024 * 1024  # Default to 10MB

class JSONFormatter(logging.Formatter):
    """JSON formatter for log records"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'exc_info', 
                          'exc_text', 'stack_info', 'lineno', 'funcName', 
                          'created', 'msecs', 'relativeCreated', 'thread', 
                          'threadName', 'processName', 'process']:
                log_entry[key] = value
        
        return json.dumps(log_entry)

def get_logger(name: str):
    """Get a structured logger instance"""
    return structlog.get_logger(name)
