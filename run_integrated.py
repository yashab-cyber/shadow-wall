#!/usr/bin/env python3
"""
ShadowWall AI Integrated Application Runner
Main entry point for the complete ShadowWall AI system with advanced dashboard
"""

import asyncio
import signal
import sys
import yaml
from pathlib import Path

from src.core.application import ShadowWallApplication
from src.utils.logger import get_logger

logger = get_logger(__name__)

def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        sys.exit(1)

async def main():
    """Main application entry point"""
    print("🚀 Starting ShadowWall AI Integrated System...")
    print("🛡️  Advanced Enterprise Cybersecurity Platform")
    print("🤖 AI-Powered Threat Detection & Response")
    print("📊 Next-Generation Dashboard & Analytics")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Initialize ShadowWall application
    app = ShadowWallApplication(config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(app.shutdown())
    
    signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
    
    try:
        # Start the application
        await app.start()
        
        print("✅ ShadowWall AI System Successfully Started!")
        print(f"📊 Dashboard: http://localhost:{config.get('dashboard', {}).get('port', 8081)}")
        print("🔄 All background services are active")
        print("🛡️  Real-time threat monitoring enabled")
        print("🤖 AI analytics engine running")
        print("=" * 60)
        
        # Keep running
        await app.run_forever()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise
    finally:
        await app.stop()
        print("🛑 ShadowWall AI System Stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 ShadowWall AI System Stopped by User")
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        sys.exit(1)
