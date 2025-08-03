#!/bin/bash
# ShadowWall AI Production Deployment Script

echo "🚀 ShadowWall AI Production Deployment"
echo "======================================="

# Create necessary directories if they don't exist
echo "📁 Creating directory structure..."
mkdir -p data/captures/{suspicious,incidents,daily,alerts}
mkdir -p data/honeypots/{ssh,http,ftp,smtp,database,samples}
mkdir -p data/models/{threat_detection,anomaly_detection,network_analysis,behavioral,datasets,metrics}
mkdir -p data/reports/{daily,weekly,monthly,incidents,compliance,custom}
mkdir -p data/sandbox/{samples,reports,logs,network,memory,artifacts}
mkdir -p data/threat_intel/{feeds,iocs,signatures,actors,campaigns,processed}
mkdir -p logs/{application,security,ml,network,honeypots,api,audit}
mkdir -p exports/{reports,data}
mkdir -p backups/{configs,databases,system}
mkdir -p temp

# Set appropriate permissions
echo "🔐 Setting directory permissions..."
chmod 755 data/ logs/ exports/ backups/ temp/
chmod 700 data/sandbox/samples/  # Restrict access to malware samples
chmod 750 data/honeypots/
chmod 750 data/threat_intel/

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Initialize configuration
echo "⚙️ Setting up configuration..."
if [ ! -f config/config.yaml ]; then
    echo "❌ Error: config/config.yaml not found!"
    echo "Please copy config.example.yaml to config.yaml and configure it for your environment."
    exit 1
fi

# Check for required environment variables
echo "🔍 Checking environment..."
REQUIRED_VARS=("SHADOWWALL_SECRET_KEY" "SHADOWWALL_DB_PATH")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️ Warning: Environment variable $var is not set"
    fi
done

# Initialize database
echo "🗄️ Initializing database..."
python -c "
from src.database.connection import DatabaseManager
import asyncio

async def init_db():
    db = DatabaseManager('data/shadowwall.db')
    await db.initialize()
    print('Database initialized successfully')

asyncio.run(init_db())
"

# Run system checks
echo "🔧 Running system checks..."
python -c "
import sys
import importlib

required_modules = [
    'fastapi', 'uvicorn', 'sqlalchemy', 'scikit-learn',
    'numpy', 'pandas', 'psutil', 'scapy', 'pyyaml'
]

missing_modules = []
for module in required_modules:
    try:
        importlib.import_module(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f'❌ Missing required modules: {missing_modules}')
    sys.exit(1)
else:
    print('✅ All required modules are installed')
"

echo ""
echo "✅ ShadowWall AI deployment completed successfully!"
echo ""
echo "🔄 To start the system:"
echo "   python run_integrated.py"
echo ""
echo "📊 Dashboard will be available at:"
echo "   http://localhost:8081"
echo ""
echo "📚 For more information, see:"
echo "   - README.md"
echo "   - STARTUP.md"
echo "   - DASHBOARD_GUIDE.md"
echo ""
echo "🛡️ Happy threat hunting! 🛡️"
