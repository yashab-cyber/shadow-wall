#!/usr/bin/env python3
"""
ShadowWall AI - Main Application Entry Point
Advanced Cybersecurity Deception Platform with ML-based Threat Prediction

This is a simplified entry point for the ShadowWall AI platform.
For advanced features like setup, debugging, and configuration options,
use init.py instead.

Usage:
    python main.py          # Start with default settings
    sudo python main.py     # Recommended for network monitoring
"""

import asyncio
import signal
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.application import ShadowWallApplication
from src.utils.logger import setup_logging, get_logger
from src.config.settings import load_config_from_file as load_config

def display_simple_banner():
    """Display a simple banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                      ShadowWall AI                           ║
║              Quick Start - Cybersecurity Platform           ║
║                                                              ║
║  For advanced options, use: python init.py --help          ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def main():
    """Main application entry point"""
    display_simple_banner()
    
    # Setup logging with INFO level
    setup_logging()  # Use defaults
    logger = get_logger(__name__)
    
    # Check if running as root
    if os.geteuid() != 0:
        logger.warning("⚠️  Not running as root - network monitoring may be limited")
        logger.info("💡 Run with 'sudo python main.py' for full capabilities")
    
    try:
        # Load configuration
        config_path = "config/config.yaml"
        if not Path(config_path).exists():
            logger.error(f"❌ Configuration file not found: {config_path}")
            logger.info("💡 Run 'python init.py --setup' to create initial configuration")
            sys.exit(1)
        
        logger.info("📝 Loading configuration...")
        config = load_config(config_path)
        
        # Initialize ShadowWall AI
        logger.info("🚀 Initializing ShadowWall AI...")
        app = ShadowWallApplication(config)
        
        # Setup signal handlers for graceful shutdown
        shutdown_event = asyncio.Event()
        
        def signal_handler(signum, frame):
            logger.info(f"🔄 Received signal {signum}. Initiating graceful shutdown...")
            shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the application
        logger.info("⚡ Starting ShadowWall AI components...")
        await app.start()
        
        logger.info("✅ ShadowWall AI is now running!")
        logger.info(f"🌐 Dashboard: http://localhost:{config.get('dashboard', {}).get('port', 8080)}")
        logger.info("🛑 Press Ctrl+C to stop")
        
        # Keep running until shutdown signal
        await shutdown_event.wait()
        
    except KeyboardInterrupt:
        logger.info("⌨️  Keyboard interrupt received")
    except ModuleNotFoundError as e:
        logger.error(f"💥 Missing dependency: {e}")
        logger.info("💡 Run 'python init.py --check-dependencies' to see what's missing")
        logger.info("💡 Or run 'python init.py --setup' to set up everything")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        logger.info("💡 Run 'python init.py --setup' to initialize the project")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)
    finally:
        logger.info("🔄 Shutting down ShadowWall AI...")
        if 'app' in locals():
            await app.stop()
        logger.info("✅ ShadowWall AI stopped successfully")

if __name__ == "__main__":
    asyncio.run(main())
