#!/bin/bash
# Sentinair Installation Script for Ubuntu/Debian
# Usage: sudo ./install_ubuntu.sh

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

# Detect Ubuntu/Debian version
detect_version() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        print_status "Detected: $OS $VER"
    else
        print_error "Cannot detect OS version"
        exit 1
    fi
}

# Update system packages
update_system() {
    print_status "Updating system packages..."
    apt-get update -y
    apt-get upgrade -y
    print_success "System updated"
}

# Install Python and dependencies
install_python() {
    print_status "Installing Python 3.8+ and pip..."
    
    # Install Python 3.8+ if not available
    if ! command -v python3.8 &> /dev/null; then
        if [[ "$VER" == "18.04" ]] || [[ "$VER" == "20.04" ]]; then
            add-apt-repository ppa:deadsnakes/ppa -y
            apt-get update -y
        fi
        apt-get install -y python3.8 python3.8-dev python3.8-venv
    fi
    
    # Install pip and development tools
    apt-get install -y python3-pip python3-dev python3-venv
    apt-get install -y build-essential libssl-dev libffi-dev
    
    # Install additional dependencies for GUI
    apt-get install -y python3-pyqt5 python3-pyqt5.qtwidgets
    
    print_success "Python installation completed"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Install required system packages
    apt-get install -y \
        sqlite3 \
        libsqlite3-dev \
        libudev-dev \
        libusb-1.0-0-dev \
        pkg-config \
        git \
        curl \
        wget \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    
    # Install monitoring tools
    apt-get install -y \
        psmisc \
        lsof \
        strace \
        inotify-tools
    
    print_success "System dependencies installed"
}

# Create sentinair user
create_user() {
    print_status "Creating sentinair user..."
    
    if ! id "sentinair" &>/dev/null; then
        useradd -r -m -s /bin/bash sentinair
        usermod -a -G adm,sys sentinair
        print_success "User 'sentinair' created"
    else
        print_warning "User 'sentinair' already exists"
    fi
}

# Install Sentinair
install_sentinair() {
    print_status "Installing Sentinair..."
    
    # Set installation directory
    INSTALL_DIR="/opt/sentinair"
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    
    # Copy files (assuming script is run from sentinair directory)
    cp -r ../* "$INSTALL_DIR/" 2>/dev/null || {
        print_error "Please run this script from the sentinair/install directory"
        exit 1
    }
    
    # Set ownership
    chown -R sentinair:sentinair "$INSTALL_DIR"
    
    # Create virtual environment
    sudo -u sentinair python3 -m venv "$INSTALL_DIR/venv"
    
    # Install Python dependencies
    sudo -u sentinair "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    sudo -u sentinair "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    
    print_success "Sentinair installed to $INSTALL_DIR"
}

# Create systemd service
create_service() {
    print_status "Creating systemd service..."
    
    cat > /etc/systemd/system/sentinair.service << 'EOF'
[Unit]
Description=Sentinair Threat Detection System
After=network.target
Wants=network.target

[Service]
Type=simple
User=sentinair
Group=sentinair
WorkingDirectory=/opt/sentinair
Environment=PATH=/opt/sentinair/venv/bin
ExecStart=/opt/sentinair/venv/bin/python main.py --mode stealth --stealth-key CHANGE_THIS_PASSWORD
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=sentinair

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/sentinair/data /opt/sentinair/logs

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    print_success "Systemd service created"
}

# Configure firewall
configure_firewall() {
    print_status "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        # UFW is available
        ufw --force enable
        print_success "UFW firewall enabled"
    elif command -v firewall-cmd &> /dev/null; then
        # FirewallD is available
        systemctl enable firewalld
        systemctl start firewalld
        print_success "FirewallD enabled"
    else
        print_warning "No firewall detected. Consider installing ufw or firewalld"
    fi
}

# Create desktop shortcut
create_desktop_shortcut() {
    print_status "Creating desktop shortcut..."
    
    cat > /usr/share/applications/sentinair.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Sentinair
Comment=Offline AI-Powered Behavioral Threat Detection System
Exec=/opt/sentinair/venv/bin/python /opt/sentinair/main.py --mode gui
Icon=/opt/sentinair/gui/icon.png
Terminal=false
Categories=Security;System;
StartupNotify=true
EOF
    
    print_success "Desktop shortcut created"
}

# Run initial setup
run_setup() {
    print_status "Running initial setup..."
    
    cd /opt/sentinair
    sudo -u sentinair ./venv/bin/python setup.py
    
    print_success "Initial setup completed"
}

# Print final instructions
print_instructions() {
    echo ""
    echo "=============================================="
    echo "Sentinair Installation Completed Successfully!"
    echo "=============================================="
    echo ""
    echo "Installation Details:"
    echo "- Install Directory: /opt/sentinair"
    echo "- User: sentinair"
    echo "- Service: sentinair.service"
    echo ""
    echo "Usage:"
    echo "- GUI Mode: sudo -u sentinair /opt/sentinair/venv/bin/python /opt/sentinair/main.py --mode gui"
    echo "- CLI Mode: sudo -u sentinair /opt/sentinair/venv/bin/python /opt/sentinair/main.py --mode cli"
    echo ""
    echo "Service Management:"
    echo "- Start: sudo systemctl start sentinair"
    echo "- Stop: sudo systemctl stop sentinair"
    echo "- Enable auto-start: sudo systemctl enable sentinair"
    echo "- View logs: sudo journalctl -u sentinair -f"
    echo ""
    echo "IMPORTANT: Change the default password in /etc/systemd/system/sentinair.service"
    echo "IMPORTANT: Run the setup script to configure admin password"
    echo ""
    echo "=============================================="
}

# Main installation function
main() {
    echo "Sentinair Installation Script for Ubuntu/Debian"
    echo "================================================="
    
    check_root
    detect_version
    update_system
    install_python
    install_system_deps
    create_user
    install_sentinair
    create_service
    configure_firewall
    create_desktop_shortcut
    run_setup
    print_instructions
}

# Run main function
main "$@"
