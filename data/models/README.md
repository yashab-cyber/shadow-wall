# ML Models Data Directory

This directory stores machine learning model data and training datasets.

## Purpose
- Trained ML model files
- Training datasets
- Model performance metrics
- Feature engineering data

## Model Types
- **Threat Detection Models**: Malware and attack classification
- **Anomaly Detection Models**: Behavioral anomaly identification
- **Network Analysis Models**: Traffic pattern analysis
- **Honeypot Intelligence Models**: Attack pattern recognition

## File Structure
```
models/
├── threat_detection/     # Threat classification models
├── anomaly_detection/    # Anomaly detection models
├── network_analysis/     # Network traffic models
├── behavioral/           # Behavioral analysis models
├── datasets/            # Training datasets
└── metrics/             # Model performance data
```

## File Types
- `.pkl` - Serialized Python models (scikit-learn)
- `.h5` - Keras/TensorFlow models
- `.joblib` - Joblib serialized models
- `.json` - Model metadata and configurations
- `.csv` - Training datasets
- `.npy` - NumPy array data

*Models are automatically retrained periodically with new data.*
