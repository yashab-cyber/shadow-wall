# Honeypot Data Directory

This directory contains data and logs from deployed honeypots.

## Purpose
- Honeypot interaction logs
- Attack pattern data
- Malware samples collected
- Attacker behavioral analysis

## Honeypot Types
- **SSH Honeypots**: Brute force attempts and SSH attacks
- **HTTP/HTTPS Honeypots**: Web application attacks
- **FTP Honeypots**: File transfer protocol attacks  
- **Email Honeypots**: SMTP and email-based attacks
- **Database Honeypots**: SQL injection attempts

## Data Structure
```
honeypots/
├── ssh/           # SSH honeypot logs
├── http/          # HTTP honeypot data
├── ftp/           # FTP interaction logs
├── smtp/          # Email honeypot logs
├── database/      # Database honeypot data
└── samples/       # Collected malware samples
```

## File Formats
- `.log` - Interaction logs
- `.json` - Structured attack data
- `.bin` - Binary malware samples
- `.txt` - Plain text logs

*⚠️ Handle files with caution - may contain malicious content.*
