#!/bin/bash
# Sentinair Installation Script for Kali Linux
# Usage: sudo ./install_kali.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run this script as root (use sudo)"
        exit 1
    fi
}

# Verify Kali Linux
verify_kali() {
    if [ ! -f /etc/debian_version ] || ! grep -q "kali" /etc/os-release; then
        print_error "This script is specifically for Kali Linux"
        exit 1
    fi
    
    print_status "Verified Kali Linux installation"
}

# Update system packages
update_system() {
    print_status "Updating Kali Linux packages..."
    
    # Update package lists
    apt-get update
    
    # Upgrade system (non-interactive)
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
    
    print_success "System updated"
}

# Install Python and development tools
install_python() {
    print_status "Installing Python 3.8+ and development tools..."
    
    # Install Python and pip
    apt-get install -y \
        python3 \
        python3-pip \
        python3-dev \
        python3-venv \
        python3-setuptools \
        python3-wheel
    
    # Install PyQt5 for GUI
    apt-get install -y \
        python3-pyqt5 \
        python3-pyqt5.qtwidgets \
        python3-pyqt5.qtcore \
        python3-pyqt5.qtgui
    
    # Install build essentials
    apt-get install -y \
        build-essential \
        gcc \
        g++ \
        make \
        cmake \
        pkg-config
    
    print_success "Python and development tools installed"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Core system libraries
    apt-get install -y \
        sqlite3 \
        libsqlite3-dev \
        libudev-dev \
        libusb-1.0-0-dev \
        libssl-dev \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev
    
    # Monitoring and security tools
    apt-get install -y \
        psmisc \
        lsof \
        strace \
        ltrace \
        inotify-tools \
        netstat-nat \
        tcpdump \
        nmap \
        wireshark-common
    
    # Utilities
    apt-get install -y \
        git \
        curl \
        wget \
        unzip \
        zip \
        vim \
        nano \
        htop \
        tree
    
    print_success "System dependencies installed"
}

# Install additional security tools integration
install_security_tools() {
    print_status "Installing additional security tools..."
    
    # YARA for malware detection
    apt-get install -y yara
    
    # ClamAV for antivirus scanning
    apt-get install -y clamav clamav-daemon
    
    # Update ClamAV database
    freshclam || print_warning "ClamAV database update failed (will retry later)"
    
    # Volatility for memory analysis
    apt-get install -y volatility3
    
    print_success "Security tools installed"
}

# Create sentinair user with appropriate permissions
create_user() {
    print_status "Creating sentinair user..."
    
    if ! id "sentinair" &>/dev/null; then
        # Create user with home directory
        useradd -r -m -s /bin/bash -d /home/sentinair sentinair
        
        # Add to relevant groups for monitoring capabilities
        usermod -a -G adm,sys,audio,video,plugdev sentinair
        
        # Set up sudo access for specific commands
        echo "sentinair ALL=(ALL) NOPASSWD: /usr/bin/systemctl status sentinair, /usr/bin/systemctl start sentinair, /usr/bin/systemctl stop sentinair, /usr/bin/journalctl -u sentinair" > /etc/sudoers.d/sentinair
        
        print_success "User 'sentinair' created with appropriate permissions"
    else
        print_warning "User 'sentinair' already exists"
    fi
}

# Install Sentinair application
install_sentinair() {
    print_status "Installing Sentinair application..."
    
    # Set installation directory
    INSTALL_DIR="/opt/sentinair"
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    
    # Copy application files
    cp -r ../* "$INSTALL_DIR/" 2>/dev/null || {
        print_error "Please run this script from the sentinair/install directory"
        exit 1
    }
    
    # Set ownership and permissions
    chown -R sentinair:sentinair "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    # Create data directories
    mkdir -p "$INSTALL_DIR"/{data,logs,reports}
    chown sentinair:sentinair "$INSTALL_DIR"/{data,logs,reports}
    
    # Create virtual environment
    sudo -u sentinair python3 -m venv "$INSTALL_DIR/venv"
    
    # Upgrade pip in virtual environment
    sudo -u sentinair "$INSTALL_DIR/venv/bin/pip" install --upgrade pip setuptools wheel
    
    # Install Python dependencies
    sudo -u sentinair "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    
    print_success "Sentinair installed to $INSTALL_DIR"
}

# Create systemd service for Kali
create_service() {
    print_status "Creating systemd service..."
    
    cat > /etc/systemd/system/sentinair.service << 'EOF'
[Unit]
Description=Sentinair Advanced Threat Detection System
Documentation=file:///opt/sentinair/README.md
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=sentinair
Group=sentinair
WorkingDirectory=/opt/sentinair
Environment=PATH=/opt/sentinair/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/opt/sentinair
ExecStartPre=/opt/sentinair/venv/bin/python -c "import sys; print('Python:', sys.executable)"
ExecStart=/opt/sentinair/venv/bin/python main.py --mode stealth --stealth-key CHANGE_THIS_PASSWORD
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal
SyslogIdentifier=sentinair

# Security settings for Kali
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/sentinair/data /opt/sentinair/logs /opt/sentinair/reports
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_RAW CAP_SYS_PTRACE CAP_DAC_READ_SEARCH

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    print_success "Systemd service created"
}

# Configure Kali-specific security settings
configure_kali_security() {
    print_status "Configuring Kali security settings..."
    
    # Configure AppArmor if available
    if command -v aa-status &> /dev/null; then
        systemctl enable apparmor
        print_success "AppArmor enabled"
    fi
    
    # Configure fail2ban for additional security
    if command -v fail2ban-server &> /dev/null; then
        systemctl enable fail2ban
        systemctl start fail2ban
        print_success "Fail2ban configured"
    else
        apt-get install -y fail2ban
        systemctl enable fail2ban
        systemctl start fail2ban
    fi
    
    # Set up log rotation
    cat > /etc/logrotate.d/sentinair << 'EOF'
/opt/sentinair/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 sentinair sentinair
    postrotate
        systemctl reload sentinair
    endscript
}
EOF
    
    print_success "Security settings configured"
}

# Create Kali-specific tools integration
create_kali_integration() {
    print_status "Creating Kali tools integration..."
    
    # Create wrapper scripts for common operations
    cat > /usr/local/bin/sentinair-gui << 'EOF'
#!/bin/bash
# Sentinair GUI launcher for Kali
export DISPLAY=${DISPLAY:-:0}
cd /opt/sentinair
sudo -u sentinair ./venv/bin/python main.py --mode gui "$@"
EOF
    
    cat > /usr/local/bin/sentinair-cli << 'EOF'
#!/bin/bash
# Sentinair CLI launcher for Kali
cd /opt/sentinair
sudo -u sentinair ./venv/bin/python main.py --mode cli "$@"
EOF
    
    cat > /usr/local/bin/sentinair-scan << 'EOF'
#!/bin/bash
# Sentinair with YARA scan integration
cd /opt/sentinair
sudo -u sentinair ./venv/bin/python -c "
from reports.report_generator import ReportGenerator
from utils.config import Config
config = Config('config/default.yaml')
generator = ReportGenerator(config, None)
print('Generating security scan report...')
"
EOF
    
    # Make scripts executable
    chmod +x /usr/local/bin/sentinair-*
    
    # Create desktop entries for Kali menu
    mkdir -p /usr/share/applications
    
    cat > /usr/share/applications/sentinair.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Sentinair Threat Detection
Comment=Advanced AI-Powered Behavioral Threat Detection System
Exec=sentinair-gui
Icon=/opt/sentinair/gui/icon.png
Terminal=false
Categories=05-Defensive;Security;System;
StartupNotify=true
EOF
    
    cat > /usr/share/applications/sentinair-cli.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Sentinair CLI
Comment=Sentinair Command Line Interface
Exec=x-terminal-emulator -e sentinair-cli
Icon=/opt/sentinair/gui/icon.png
Terminal=true
Categories=05-Defensive;Security;System;
StartupNotify=true
EOF
    
    print_success "Kali tools integration created"
}

# Run initial setup
run_setup() {
    print_status "Running initial Sentinair setup..."
    
    cd /opt/sentinair
    
    # Run setup as sentinair user
    sudo -u sentinair ./venv/bin/python setup.py
    
    # Create initial YARA rules for Kali environment
    cat >> /opt/sentinair/signatures/kali_specific.yar << 'EOF'
/*
    Kali Linux specific YARA rules for Sentinair
*/

rule KaliToolExecution
{
    meta:
        description = "Detects execution of Kali penetration testing tools"
        author = "Sentinair-Kali"
        
    strings:
        $tool1 = "metasploit"
        $tool2 = "nmap"
        $tool3 = "wireshark"
        $tool4 = "burpsuite"
        $tool5 = "sqlmap"
        
    condition:
        any of them
}

rule SuspiciousNetworkActivity
{
    meta:
        description = "Detects suspicious network scanning activity"
        
    strings:
        $scan1 = "-sS"
        $scan2 = "-sT"
        $scan3 = "--script"
        $scan4 = "nikto"
        
    condition:
        2 of them
}
EOF
    
    chown sentinair:sentinair /opt/sentinair/signatures/kali_specific.yar
    
    print_success "Initial setup completed"
}

# Print Kali-specific instructions
print_instructions() {
    echo ""
    echo "=================================================="
    echo "Sentinair Installation Completed for Kali Linux!"
    echo "=================================================="
    echo ""
    echo "Installation Details:"
    echo "- Install Directory: /opt/sentinair"
    echo "- User: sentinair"
    echo "- Service: sentinair.service"
    echo "- Kali Menu: Applications > 05-Defensive > Sentinair"
    echo ""
    echo "Quick Launch Commands:"
    echo "- GUI Mode: sentinair-gui"
    echo "- CLI Mode: sentinair-cli"
    echo "- Security Scan: sentinair-scan"
    echo ""
    echo "Service Management:"
    echo "- Start: sudo systemctl start sentinair"
    echo "- Stop: sudo systemctl stop sentinair"
    echo "- Enable auto-start: sudo systemctl enable sentinair"
    echo "- View logs: sudo journalctl -u sentinair -f"
    echo ""
    echo "Kali Integration:"
    echo "- YARA rules: /opt/sentinair/signatures/"
    echo "- ClamAV integration: Available"
    echo "- Volatility support: Available"
    echo "- Network monitoring: Enhanced for Kali tools"
    echo ""
    echo "SECURITY NOTES:"
    echo "- Change default password in /etc/systemd/system/sentinair.service"
    echo "- Configure admin password via setup script"
    echo "- Review Kali-specific YARA rules in signatures/kali_specific.yar"
    echo "- Fail2ban is enabled for additional protection"
    echo ""
    echo "=================================================="
}

# Main installation function
main() {
    echo "Sentinair Installation Script for Kali Linux"
    echo "============================================="
    
    check_root
    verify_kali
    update_system
    install_python
    install_system_deps
    install_security_tools
    create_user
    install_sentinair
    create_service
    configure_kali_security
    create_kali_integration
    run_setup
    print_instructions
}

# Run main function
main "$@"
