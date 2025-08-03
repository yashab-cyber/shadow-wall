# Threat Intelligence Directory

This directory stores threat intelligence feeds and indicators of compromise (IOCs).

## Purpose
- External threat intelligence feeds
- Indicators of Compromise (IOCs)
- Threat actor profiles
- Attack pattern databases

## Intelligence Sources
- **Commercial Feeds**: Paid threat intelligence services
- **Open Source**: Public threat intelligence feeds
- **Government**: Official security bulletins
- **Industry**: Sector-specific threat data
- **Internal**: Organization-specific intelligence

## File Structure
```
threat_intel/
├── feeds/          # Raw intelligence feeds
├── iocs/          # Indicators of Compromise
├── signatures/    # Detection signatures
├── actors/        # Threat actor profiles
├── campaigns/     # Attack campaign data
└── processed/     # Processed intelligence data
```

## File Types
- `.json` - Structured intelligence data
- `.xml` - STIX/TAXII formatted data
- `.csv` - Tabular IOC data
- `.txt` - Plain text indicators
- `.yara` - YARA detection rules
- `.snort` - Snort IDS rules

## Data Formats
- **STIX 2.0**: Structured Threat Information eXpression
- **TAXII 2.0**: Trusted Automated eXchange of Intelligence Information
- **OpenIOC**: Open Indicators of Compromise
- **MISP**: Malware Information Sharing Platform format

## Update Schedule
- Feeds are updated every 15 minutes
- Critical intelligence is processed immediately
- Historical data is retained for trend analysis

*Intelligence data is automatically correlated with system events.*
