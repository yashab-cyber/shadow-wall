# System Logs Directory

This directory contains system logs and operational data from the ShadowWall AI platform.

## Purpose
- Application logs
- System operation logs
- Error and debug information
- Audit trails

## Log Types
- **Application Logs**: Core application events
- **Security Logs**: Security-related events
- **ML Logs**: Machine learning operations
- **Network Logs**: Network monitoring events
- **Honeypot Logs**: Honeypot system logs
- **API Logs**: REST API access logs

## File Structure
```
logs/
├── application/    # Main application logs
├── security/      # Security event logs
├── ml/            # ML model operation logs
├── network/       # Network monitoring logs
├── honeypots/     # Honeypot system logs
├── api/           # API access logs
└── audit/         # System audit logs
```

## File Formats
- `.log` - Standard log files
- `.json` - Structured JSON logs
- `.txt` - Plain text logs

## Log Rotation
- Logs are rotated daily
- Compressed logs are retained for 30 days
- Critical security logs are retained for 1 year
- Debug logs are cleaned up weekly

## Log Levels
- `DEBUG`: Detailed diagnostic information
- `INFO`: General operational messages
- `WARNING`: Warning conditions
- `ERROR`: Error conditions
- `CRITICAL`: Critical system failures

*Logs are automatically managed by the system logging framework.*
