# Network Captures Directory

This directory stores captured network traffic and packet data for analysis.

## Purpose
- Raw packet captures (PCAP files)
- Network traffic analysis data
- Suspicious activity captures
- Evidence collection for security incidents

## File Types
- `.pcap` - Packet capture files
- `.pcapng` - Next generation packet captures
- `.cap` - Network capture files
- `.log` - Traffic analysis logs

## Organization
```
captures/
├── suspicious/     # Suspicious traffic captures
├── incidents/      # Security incident evidence
├── daily/         # Daily traffic samples
└── alerts/        # Alert-triggered captures
```

## Retention
- Captures are retained for 30 days by default
- Critical incident captures are preserved longer
- Automatic cleanup removes old files

*Files are automatically organized by date and threat level.*
