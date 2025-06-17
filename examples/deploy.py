#!/usr/bin/env python3
"""
Deployment script for Sentinair
Helps with installation and configuration on target systems
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check OS
    os_name = platform.system()
    print(f"Operating System: {os_name}")
    
    if os_name not in ['Windows', 'Linux']:
        print("⚠️  Warning: This OS may not be fully supported")
    
    # Check available disk space
    try:
        disk_usage = shutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        print(f"Available disk space: {free_gb:.1f} GB")
        
        if free_gb < 1:
            print("⚠️  Warning: Less than 1GB free space available")
    except:
        print("Could not check disk space")
    
    # Check memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        print(f"Memory: {available_gb:.1f}GB available / {total_gb:.1f}GB total")
        
        if available_gb < 2:
            print("⚠️  Warning: Less than 2GB RAM available")
    except ImportError:
        print("Could not check memory (psutil not installed)")
    
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file, "--user"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_service_files():
    """Create system service files for auto-start"""
    print("🔧 Creating service files...")
    
    system_name = platform.system()
    
    if system_name == "Linux":
        create_systemd_service()
    elif system_name == "Windows":
        create_windows_service()
    else:
        print("⚠️  Service creation not supported on this OS")

def create_systemd_service():
    """Create systemd service file for Linux"""
    service_content = f"""[Unit]
Description=Sentinair Threat Detection System
After=network.target

[Service]
Type=simple
User=sentinair
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} main.py --mode stealth
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "/tmp/sentinair.service"
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"✅ Service file created: {service_file}")
        print("To install the service:")
        print(f"  sudo cp {service_file} /etc/systemd/system/")
        print("  sudo systemctl daemon-reload")
        print("  sudo systemctl enable sentinair")
        print("  sudo systemctl start sentinair")
        
    except Exception as e:
        print(f"❌ Failed to create service file: {e}")

def create_windows_service():
    """Create Windows service configuration"""
    print("Windows service creation requires additional tools like NSSM or sc.exe")
    print("Manual installation steps:")
    print("1. Download NSSM (Non-Sucking Service Manager)")
    print("2. Run: nssm install Sentinair")
    print(f"3. Set application path: {sys.executable}")
    print(f"4. Set arguments: {os.getcwd()}\\main.py --mode stealth")
    print(f"5. Set startup directory: {os.getcwd()}")

def create_deployment_script():
    """Create deployment script for easy installation"""
    if platform.system() == "Windows":
        script_name = "deploy.bat"
        script_content = f"""@echo off
echo Installing Sentinair...
python -m pip install -r requirements.txt --user
python setup.py
echo.
echo Installation complete!
echo Run with: python main.py
pause
"""
    else:
        script_name = "deploy.sh"
        script_content = f"""#!/bin/bash
echo "Installing Sentinair..."
python3 -m pip install -r requirements.txt --user
python3 setup.py
echo
echo "Installation complete!"
echo "Run with: python3 main.py"
"""
    
    try:
        with open(script_name, 'w') as f:
            f.write(script_content)
        
        if platform.system() != "Windows":
            os.chmod(script_name, 0o755)
        
        print(f"✅ Deployment script created: {script_name}")
        
    except Exception as e:
        print(f"❌ Failed to create deployment script: {e}")

def create_uninstall_script():
    """Create uninstall script"""
    if platform.system() == "Windows":
        script_name = "uninstall.bat"
        script_content = """@echo off
echo Uninstalling Sentinair...
rmdir /s /q data
rmdir /s /q __pycache__
del /q *.log
echo Uninstall complete!
pause
"""
    else:
        script_name = "uninstall.sh"
        script_content = """#!/bin/bash
echo "Uninstalling Sentinair..."
rm -rf data/
rm -rf __pycache__/
rm -f *.log
echo "Uninstall complete!"
"""
    
    try:
        with open(script_name, 'w') as f:
            f.write(script_content)
        
        if platform.system() != "Windows":
            os.chmod(script_name, 0o755)
        
        print(f"✅ Uninstall script created: {script_name}")
        
    except Exception as e:
        print(f"❌ Failed to create uninstall script: {e}")

def setup_logging_directory():
    """Set up logging directory with proper permissions"""
    log_dir = "logs"
    try:
        os.makedirs(log_dir, exist_ok=True)
        print(f"✅ Logging directory created: {log_dir}")
        
        # Set permissions on Unix-like systems
        if platform.system() != "Windows":
            os.chmod(log_dir, 0o755)
            
    except Exception as e:
        print(f"❌ Failed to create logging directory: {e}")

def main():
    """Main deployment function"""
    print("=" * 60)
    print("         SENTINAIR DEPLOYMENT SCRIPT")
    print("=" * 60)
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_system_requirements():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Deployment failed due to dependency installation error")
        sys.exit(1)
    
    # Create directories and files
    setup_logging_directory()
    create_service_files()
    create_deployment_script()
    create_uninstall_script()
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: python setup.py")
    print("2. Run: python main.py --mode gui")
    print()
    print("For help: python main.py --help")
    print("=" * 60)

if __name__ == "__main__":
    main()
