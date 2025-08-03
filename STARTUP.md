# 🚀 ShadowWall AI - Startup Guide

## 📋 Quick Start Options

ShadowWall AI provides multiple entry points depending on your needs:

### 🎯 **Option 1: Smart Launcher (Recommended for New Users)**
```bash
python run.py                    # Auto-detects first run and sets up everything
sudo python run.py               # Recommended for full capabilities
```

### ⚡ **Option 2: Simple Start (Quick & Easy)**
```bash
python main.py                   # Basic startup with default settings
sudo python main.py              # With network monitoring privileges
```

### 🔧 **Option 3: Advanced Setup (Full Control)**
```bash
python init.py --setup           # Initial setup only
python init.py                   # Full-featured startup
python init.py --debug           # Debug mode
python init.py --help            # See all options
```

## 🎛️ **Startup Scripts Explained**

| Script | Purpose | Best For | Features |
|--------|---------|----------|----------|
| `run.py` | Smart launcher | New users | Auto-setup, intelligent detection |
| `main.py` | Simple entry point | Quick testing | Minimal config, fast startup |
| `init.py` | Advanced initialization | Production use | Full features, comprehensive setup |

## 🔐 **Permission Requirements**

### **Full Network Monitoring (Recommended)**
```bash
sudo python run.py               # Complete feature set
sudo python init.py              # All capabilities enabled
```

### **Limited Mode (No Root Required)**
```bash
python run.py                    # Simulation mode
python init.py --simulate        # No network capture
```

## 🛠️ **First Time Setup**

1. **Automatic Setup (Easiest)**
   ```bash
   python run.py                 # Handles everything automatically
   ```

2. **Manual Setup**
   ```bash
   python init.py --setup        # Check dependencies and create structure
   python init.py                # Start the application
   ```

3. **Docker Setup**
   ```bash
   docker-compose up -d          # Container-based deployment
   ```

## 🎯 **Common Use Cases**

### **🔬 Security Research**
```bash
python init.py --sandbox --debug
```

### **🏢 Production Deployment**
```bash
sudo python init.py --config production.yaml
```

### **💻 Development & Testing**
```bash
python init.py --simulate --debug
```

### **🎯 Red Team Exercises**
```bash
sudo python init.py --sandbox
```

## 🚨 **Troubleshooting**

### **Dependencies Missing**
```bash
python init.py --check-dependencies    # Check what's missing
pip install -r requirements.txt        # Install dependencies
```

### **Permission Issues**
```bash
sudo python init.py                    # Run with root privileges
# OR
python init.py --simulate              # Run without network capture
```

### **Configuration Problems**
```bash
python init.py --setup                 # Recreate configuration
cp config/config.example.yaml config/config.yaml  # Reset config
```

### **Port Conflicts**
```bash
python init.py --port 9090             # Use different port
```

## 📊 **Dashboard Access**

After startup, access the dashboard at:
- **Default:** http://localhost:8080
- **Custom port:** http://localhost:YOUR_PORT
- **Debug info:** Available in terminal output

## 🔄 **Stopping ShadowWall AI**

- Press `Ctrl+C` for graceful shutdown
- All components will stop cleanly
- Data will be saved automatically

## 💡 **Pro Tips**

1. **Always use `sudo`** for full network monitoring capabilities
2. **Start with `run.py`** if you're new to ShadowWall AI
3. **Use `--debug`** flag for detailed logging during development
4. **Check logs** in the `logs/` directory for troubleshooting
5. **Backup your configuration** before making changes

## 📞 **Need Help?**

- Run `python init.py --help` for all options
- Check the main README.md for detailed documentation
- Create an issue on GitHub for bug reports
- Contact: yashabalam707@gmail.com
