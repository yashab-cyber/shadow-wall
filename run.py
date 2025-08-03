#!/usr/bin/env python3
"""
ShadowWall AI - Universal Launcher
Smart launcher that detects the best way to start ShadowWall AI

This script automatically:
- Detects if this is the first run
- Checks system requirements
- Chooses the appropriate startup method
- Provides helpful guidance
"""

import sys
import os
from pathlib import Path

def display_launcher_banner():
    """Display launcher banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                  ShadowWall AI Launcher                      ║
║                                                              ║
║              🚀 Smart Startup Detection                     ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_first_run():
    """Check if this is the first run"""
    config_exists = Path("config/config.yaml").exists()
    data_dir_exists = Path("data").exists() and any(Path("data").iterdir())
    
    return not (config_exists and data_dir_exists)

def main():
    """Main launcher function"""
    display_launcher_banner()
    
    # Check if this is the first run
    if check_first_run():
        print("🔍 First run detected!")
        print("🚀 Running initial setup...")
        print()
        os.system("python init.py --setup")
        print()
        print("✅ Setup complete! Starting ShadowWall AI...")
        print()
        os.system("python init.py")
    else:
        print("✅ ShadowWall AI is configured")
        
        # Check if running as root
        if hasattr(os, 'geteuid') and os.geteuid() != 0:
            print("⚠️  Not running as root - starting with limited capabilities")
            print("💡 For full network monitoring, run: sudo python run.py")
        else:
            print("🔐 Running with full privileges")
        
        print("🚀 Starting ShadowWall AI...")
        print()
        
        # Start with appropriate method based on arguments
        if len(sys.argv) > 1:
            # Pass through arguments to init.py
            args = " ".join(sys.argv[1:])
            os.system(f"python init.py {args}")
        else:
            # Use simple launcher for basic usage
            os.system("python main.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Startup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Launcher error: {e}")
        print("💡 Try running directly: python init.py --setup")
        sys.exit(1)
