#!/bin/bash
# Sentinair Installation Script for CentOS/RHEL/Fedora
# Usage: sudo ./install_centos.sh

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

# Detect distribution
detect_distro() {
    if [ -f /etc/redhat-release ]; then
        if grep -q "CentOS" /etc/redhat-release; then
            DISTRO="centos"
        elif grep -q "Red Hat" /etc/redhat-release; then
            DISTRO="rhel"
        elif grep -q "Fedora" /etc/redhat-release; then
            DISTRO="fedora"
        else
            DISTRO="unknown"
        fi
        print_status "Detected distribution: $DISTRO"
    else
        print_error "This script is for CentOS/RHEL/Fedora systems"
        exit 1
    fi
}

# Update system packages
update_system() {
    print_status "Updating system packages..."
    
    if [ "$DISTRO" = "fedora" ]; then
        dnf update -y
    else
        yum update -y
    fi
    
    print_success "System updated"
}

# Install EPEL repository for CentOS/RHEL
install_epel() {
    if [ "$DISTRO" = "centos" ] || [ "$DISTRO" = "rhel" ]; then
        print_status "Installing EPEL repository..."
        
        if [ "$DISTRO" = "centos" ]; then
            yum install -y epel-release
        else
            # RHEL
            yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
        fi
        
        print_success "EPEL repository installed"
    fi
}

# Install Python and dependencies
install_python() {
    print_status "Installing Python 3.8+ and pip..."
    
    if [ "$DISTRO" = "fedora" ]; then
        dnf install -y python3 python3-pip python3-devel python3-virtualenv
        dnf install -y python3-qt5 python3-qt5-devel
    else
        # CentOS/RHEL
        yum install -y python38 python38-pip python38-devel python38-virtualenv
        yum install -y python3-qt5 python3-qt5-devel
    fi
    
    print_success "Python installation completed"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if [ "$DISTRO" = "fedora" ]; then
        dnf groupinstall -y "Development Tools"
        dnf install -y \
            sqlite sqlite-devel \
            libudev-devel \
            libusb1-devel \
            pkgconfig \
            git \
            curl \
            wget \
            unzip \
            openssl-devel \
            libffi-devel
    else
        # CentOS/RHEL
        yum groupinstall -y "Development Tools"
        yum install -y \
            sqlite sqlite-devel \
            libudev-devel \
            libusbx-devel \
            pkgconfig \
            git \
            curl \
            wget \
            unzip \
            openssl-devel \
            libffi-devel
    fi
    
    # Install monitoring tools
    if [ "$DISTRO" = "fedora" ]; then
        dnf install -y psmisc lsof strace inotify-tools
    else
        yum install -y psmisc lsof strace inotify-tools
    fi
    
    print_success "System dependencies installed"
}

# Create sentinair user
create_user() {
    print_status "Creating sentinair user..."
    
    if ! id "sentinair" &>/dev/null; then
        useradd -r -m -s /bin/bash sentinair
        usermod -a -G wheel sentinair
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
    
    # Copy files
    cp -r ../* "$INSTALL_DIR/" 2>/dev/null || {
        print_error "Please run this script from the sentinair/install directory"
        exit 1
    }
    
    # Set ownership
    chown -R sentinair:sentinair "$INSTALL_DIR"
    
    # Create virtual environment
    if [ "$DISTRO" = "fedora" ]; then
        sudo -u sentinair python3 -m venv "$INSTALL_DIR/venv"
    else
        sudo -u sentinair python3.8 -m venv "$INSTALL_DIR/venv"
    fi
    
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

# Configure SELinux
configure_selinux() {
    print_status "Configuring SELinux..."
    
    if command -v getenforce &> /dev/null; then
        if [ "$(getenforce)" = "Enforcing" ]; then
            # Set SELinux context for Sentinair
            semanage fcontext -a -t bin_t "/opt/sentinair/venv/bin/python" 2>/dev/null || true
            restorecon -R /opt/sentinair/ 2>/dev/null || true
            
            # Allow Sentinair to bind to ports (if needed)
            setsebool -P httpd_can_network_connect 1 2>/dev/null || true
            
            print_success "SELinux configured"
        else
            print_warning "SELinux is not enforcing"
        fi
    else
        print_warning "SELinux not detected"
    fi
}

# Configure firewall
configure_firewall() {
    print_status "Configuring firewall..."
    
    if systemctl is-active --quiet firewalld; then
        # FirewallD is running
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --reload
        print_success "Firewall configured"
    else
        print_warning "Firewall not running. Consider enabling firewalld"
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
    echo "Sentinair Installation Script for CentOS/RHEL/Fedora"
    echo "====================================================="
    
    check_root
    detect_distro
    update_system
    install_epel
    install_python
    install_system_deps
    create_user
    install_sentinair
    create_service
    configure_selinux
    configure_firewall
    create_desktop_shortcut
    run_setup
    print_instructions
}

# Run main function
main "$@"
