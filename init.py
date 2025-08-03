"""
ShadowWall AI - Advanced Initialization Script
Complete setup and configuration system for the cybersecurity platform

This script provides comprehensive initialization with:
- Dependency checking and installation guidance
- Directory structure creation
- Configuration management
- Permission validation
- Multiple operational modes (debug, simulation, setup)
- Advanced logging and error handling
"""

import asyncio
import sys
import os
import argparse
import subprocess
import platform
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.config.settings import load_config_from_file
from src.core.application import ShadowWallApplication
from src.utils.logger import setup_logging, get_logger

# Alias for backward compatibility
def load_config(config_path: str):
    """Load configuration from file - compatibility wrapper"""
    return load_config_from_file(config_path)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="ShadowWall AI - Advanced Cybersecurity Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 Usage Examples:
  python init.py                          # Start with default configuration
  python init.py --config custom.yaml    # Use custom config file
  python init.py --debug                 # Enable debug logging
  python init.py --setup                 # Run initial setup only
  python init.py --simulate              # Run in simulation mode
  python init.py --check-dependencies    # Check system dependencies
  python init.py --sandbox               # Start with sandbox environment
  python init.py --validate-models       # Validate ML models
  
🔧 Advanced Options:
  sudo python init.py                    # Full network monitoring (recommended)
  python init.py --no-dashboard         # Run without web dashboard
  python init.py --port 9090            # Custom dashboard port
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/config.yaml',
        help='Configuration file path (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging with detailed output'
    )
    
    parser.add_argument(
        '--setup', '-s',
        action='store_true',
        help='Run initial setup only (create directories, check dependencies)'
    )
    
    parser.add_argument(
        '--check-dependencies',
        action='store_true',
        help='Check and install missing dependencies'
    )
    
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Run in simulation mode (no network capture, Docker optional)'
    )
    
    parser.add_argument(
        '--sandbox',
        action='store_true',
        help='Start with sandbox environment enabled'
    )
    
    parser.add_argument(
        '--no-dashboard',
        action='store_true',
        help='Disable web dashboard (headless mode)'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8080,
        help='Dashboard port (default: 8080)'
    )
    
    parser.add_argument(
        '--validate-models',
        action='store_true',
        help='Validate ML models and training data'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='ShadowWall AI v1.0.0 - Advanced Cybersecurity Platform'
    )
    
    return parser.parse_args()

def get_system_info():
    """Get system information for compatibility checks"""
    return {
        'platform': platform.system(),
        'architecture': platform.machine(),
        'python_version': platform.python_version(),
        'is_root': os.geteuid() == 0 if hasattr(os, 'geteuid') else False,
        'has_docker': subprocess.run(['which', 'docker'], capture_output=True).returncode == 0
    }

def check_dependencies():
    """Check for required dependencies"""
    logger = get_logger(__name__)
    
    # Core dependencies
    required_packages = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'ASGI server',
        'sqlalchemy': 'Database ORM',
        'scapy': 'Packet manipulation',
        'sklearn': 'Machine learning',  # Note: package name is sklearn, not scikit-learn
        'numpy': 'Numerical computing',
        'pandas': 'Data analysis',
        'redis': 'In-memory database',
        'psutil': 'System monitoring',
        'docker': 'Container management',
        'yaml': 'YAML configuration',  # Note: module name is yaml, package is pyyaml
        'websockets': 'WebSocket support',
        'aiofiles': 'Async file operations',
        'jinja2': 'Template engine',
        'cryptography': 'Cryptographic operations'
    }
    
    # Optional packages
    optional_packages = {
        'elasticsearch': 'Log aggregation',
        'prometheus_client': 'Metrics collection',
        'plotly': 'Advanced visualization',
        'tensorflow': 'Deep learning (optional)',
        'torch': 'PyTorch ML framework (optional)'
    }
    
    missing_packages = []
    optional_missing = []
    
    logger.info("🔍 Checking core dependencies...")
    for package, description in required_packages.items():
        try:
            # Handle special cases for package vs module names
            module_name = package.replace('-', '_')
            if package == 'yaml':
                module_name = 'yaml'  # pyyaml installs as yaml module
            elif package == 'sklearn':
                module_name = 'sklearn'  # scikit-learn installs as sklearn module
            
            __import__(module_name)
            logger.info(f"✅ {package} - {description}")
        except ImportError:
            logger.warning(f"❌ {package} - {description}")
            # Show the actual package name to install
            package_to_install = package
            if package == 'sklearn':
                package_to_install = 'scikit-learn'
            elif package == 'yaml':
                package_to_install = 'pyyaml'
            missing_packages.append(package_to_install)
    
    logger.info("🔍 Checking optional dependencies...")
    for package, description in optional_packages.items():
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} - {description}")
        except ImportError:
            logger.info(f"⚠️  {package} - {description} (optional)")
            optional_missing.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing required packages: {', '.join(missing_packages)}")
        logger.info("📦 Install with: pip install " + " ".join(missing_packages))
        return False
    
    if optional_missing:
        logger.info(f"📋 Optional packages not installed: {', '.join(optional_missing)}")
        logger.info("📦 Install optional features with: pip install " + " ".join(optional_missing))
    
    logger.info("✅ All required dependencies are available")
    return True

def setup_directories():
    """Create necessary directories"""
    logger = get_logger(__name__)
    
    directories = [
        'logs',
        'data',
        'data/models',
        'data/honeypots',
        'data/captures',
        'data/reports',
        'data/threat_intel',
        'data/sandbox',
        'config',
        'temp',
        'backups',
        'exports'
    ]
    
    logger.info("📁 Creating directory structure...")
    created_count = 0
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created: {directory}")
            created_count += 1
        else:
            logger.debug(f"📁 Exists: {directory}")
    
    if created_count > 0:
        logger.info(f"📁 Created {created_count} new directories")
    else:
        logger.info("📁 All directories already exist")

def check_permissions():
    """Check for required permissions"""
    logger = get_logger(__name__)
    system_info = get_system_info()
    
    logger.info("🔐 Checking system permissions...")
    
    # Check root access (for packet capture)
    if not system_info['is_root']:
        logger.warning("⚠️  Not running as root - network monitoring will be limited")
        logger.info("💡 For full capabilities, run with: sudo python init.py")
        if system_info['platform'] != 'Windows':
            logger.info("🔧 Alternative: Configure capabilities with setcap")
        return False
    
    logger.info("✅ Running with root privileges")
    
    # Check write permissions for data directories
    test_dirs = ['logs', 'data', 'temp']
    for test_dir in test_dirs:
        dir_path = Path(test_dir)
        if dir_path.exists():
            if not os.access(dir_path, os.W_OK):
                logger.error(f"❌ No write permission for: {test_dir}")
                return False
    
    logger.info("✅ Directory permissions verified")
    return True

def validate_models():
    """Validate ML models and training data"""
    logger = get_logger(__name__)
    
    logger.info("🧠 Validating ML models...")
    
    model_files = [
        'data/models/threat_detector.pkl',
        'data/models/behavioral_analyzer.pkl',
        'data/models/network_classifier.pkl'
    ]
    
    models_exist = True
    for model_file in model_files:
        if not Path(model_file).exists():
            logger.warning(f"⚠️  Model not found: {model_file}")
            models_exist = False
        else:
            logger.info(f"✅ Found: {model_file}")
    
    if not models_exist:
        logger.info("🔄 Models will be trained on first run")
    else:
        logger.info("✅ All ML models are available")
    
    return True

def display_banner():
    """Display the ShadowWall banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                        ShadowWall AI                          ║
║                                                               ║
║    🛡️  Advanced Cybersecurity Platform with ML Integration   ║
║                                                               ║
║  🔍 Real-time Threat Detection      🧠 Machine Learning      ║
║  📊 Behavioral Analysis            🍯 Adaptive Honeypots     ║
║  🌐 Threat Intelligence            🏗️  Security Sandbox      ║
║  📈 Live Dashboard                 ⚡ Sub-100ms Response     ║
║                                                               ║
║              🚀 Predicting Tomorrow's Threats Today          ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    
    # Display system info
    system_info = get_system_info()
    print(f"🖥️  Platform: {system_info['platform']} ({system_info['architecture']})")
    print(f"🐍 Python: {system_info['python_version']}")
    print(f"🔐 Privileges: {'Root' if system_info['is_root'] else 'User'}")
    print(f"🐳 Docker: {'Available' if system_info['has_docker'] else 'Not found'}")
    print()

async def run_setup():
    """Run initial setup"""
    logger = get_logger(__name__)
    
    logger.info("🚀 Running ShadowWall AI setup...")
    
    # Create directories
    setup_directories()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check permissions
    perms_ok = check_permissions()
    
    # Validate models
    models_ok = validate_models()
    
    # Create default config if it doesn't exist
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        example_config = Path("config/config.example.yaml")
        if example_config.exists():
            import shutil
            shutil.copy(example_config, config_path)
            logger.info("✅ Created default configuration from example")
        else:
            logger.warning("⚠️  No example configuration found")
    
    setup_success = deps_ok and models_ok
    
    if setup_success:
        if perms_ok:
            logger.info("🎉 Setup completed successfully!")
            logger.info("🚀 Start ShadowWall AI with: python init.py")
        else:
            logger.info("✅ Setup completed with limited permissions")
            logger.info("🚀 Start with: sudo python init.py (recommended)")
    else:
        logger.warning("⚠️  Setup completed with issues - check messages above")
    
    return setup_success

async def main():
    """Main initialization function"""
    args = parse_arguments()
    
    # Display banner
    display_banner()
    
    # Setup logging
    log_level = 'DEBUG' if args.debug else 'INFO'
    setup_logging()  # Use defaults
    logger = get_logger(__name__)
    
    try:
        # Handle specific commands
        if args.setup:
            await run_setup()
            return
        
        if args.check_dependencies:
            success = check_dependencies()
            sys.exit(0 if success else 1)
        
        if args.validate_models:
            success = validate_models()
            sys.exit(0 if success else 1)
        
        # Load configuration
        logger.info(f"📝 Loading configuration from: {args.config}")
        if not Path(args.config).exists():
            logger.error(f"❌ Configuration file not found: {args.config}")
            logger.info("💡 Run 'python init.py --setup' to create initial configuration")
            sys.exit(1)
        
        config = load_config(args.config)
        
        # Apply command line overrides
        if args.simulate:
            config['network']['simulation_mode'] = True
            config['sandbox']['enabled'] = False
            logger.info("🔬 Running in simulation mode")
        
        if args.sandbox:
            config['sandbox']['enabled'] = True
            logger.info("🏗️  Sandbox environment enabled")
        
        if args.no_dashboard:
            config['dashboard']['enabled'] = False
            logger.info("📊 Dashboard disabled (headless mode)")
        
        if args.port != 8080:
            config['dashboard']['port'] = args.port
            logger.info(f"🌐 Custom dashboard port: {args.port}")
        
        if args.debug:
            config['logging']['level'] = 'DEBUG'
            logger.info("🔍 Debug logging enabled")
        
        # Run initial checks
        logger.info("🔍 Performing system checks...")
        setup_success = await run_setup()
        
        if not setup_success:
            logger.warning("⚠️  System checks failed - some features may not work correctly")
        
        # Initialize and start the application
        logger.info("🚀 Initializing ShadowWall AI...")
        app = ShadowWallApplication(config)
        
        # Setup signal handlers
        shutdown_event = asyncio.Event()
        
        def signal_handler(signum, frame):
            logger.info(f"🔄 Received signal {signum}. Initiating graceful shutdown...")
            shutdown_event.set()
        
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("⚡ Starting ShadowWall AI components...")
        await app.start()
        
        logger.info("🎉 ShadowWall AI is now running!")
        if config.get('dashboard', {}).get('enabled', True):
            port = config.get('app', {}).get('port', 8080)
            logger.info(f"🌐 Dashboard: http://localhost:{port}")
        logger.info("🛑 Press Ctrl+C to stop")
        
        # Keep running until shutdown signal
        await shutdown_event.wait()
        
    except KeyboardInterrupt:
        logger.info("⌨️  Keyboard interrupt received")
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        logger.info("💡 Run 'python init.py --setup' to initialize the project")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Failed to start ShadowWall AI: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)
    finally:
        logger.info("🔄 Stopping ShadowWall AI...")
        if 'app' in locals():
            await app.stop()
        logger.info("✅ ShadowWall AI stopped successfully")

if __name__ == "__main__":
    asyncio.run(main())
