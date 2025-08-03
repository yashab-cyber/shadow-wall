# Trained Models Directory

This directory stores the trained machine learning models used by the ShadowWall AI system.

## Purpose
- Serialized ML models ready for inference
- Model checkpoints and saved states
- Pre-trained model files

## Model Files
- **Threat Detection Models**: `threat_*.pkl`
- **Anomaly Detection Models**: `anomaly_*.pkl`
- **Behavioral Analysis Models**: `behavioral_*.pkl`
- **Network Analysis Models**: `network_*.pkl`

## Model Types
1. **Threat Classifier**: Identifies different types of cyber threats
2. **Anomaly Detector**: Detects unusual patterns in network traffic
3. **Behavioral Model**: Analyzes user and system behavior patterns

## File Naming Convention
```
{model_type}_{version}_{timestamp}.pkl
```

Examples:
- `threat_classifier_v1_20250803.pkl`
- `anomaly_detector_v2_20250803.pkl`
- `behavioral_model_v1_20250803.pkl`

## Model Management
- Models are automatically retrained with new data
- Old model versions are archived
- Model performance metrics are tracked
- Automatic fallback to previous versions if needed

## Loading Models
Models are automatically loaded by the ML components during system startup. Manual model loading is handled by the `ThreatDetector` and `BehavioralAnalyzer` classes.

*⚠️ Do not manually modify or delete model files while the system is running.*
