#!/bin/bash
# Coalition Server Ubuntu Service Installation Script
# This script installs Coalition Server as a systemd service on Ubuntu systems

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="coalition-server"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
INSTALL_DIR="/opt/coalition-server"
USER="coalition"

echo "============================================================"
echo "Coalition Server Service Installation for Ubuntu"
echo "============================================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root"
   echo "Usage: sudo ./install_server_service_ubuntu.sh [PORT]"
   exit 1
fi

# Parse command line arguments
SERVER_PORT="${1:-19211}"

echo "Configuration:"
echo "  Service Name: ${SERVICE_NAME}"
echo "  Install Directory: ${INSTALL_DIR}"
echo "  Service User: ${USER}"
echo "  Server Port: ${SERVER_PORT}"
echo ""

# Check Ubuntu version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$ID" != "ubuntu" ]; then
        echo "Warning: This script is designed for Ubuntu, detected: $PRETTY_NAME"
        echo "Proceeding anyway..."
    else
        echo "✓ Ubuntu $VERSION detected"
    fi
else
    echo "Warning: Could not detect OS version, proceeding anyway..."
fi

# Check Python 3
echo "Checking Python 3..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required but not found"
    echo "Install with: apt update && apt install python3"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"

# Check for pip3
echo "Checking pip3..."
if ! command -v pip3 >/dev/null 2>&1; then
    echo "Error: pip3 is required but not found"
    echo "Install with: apt update && apt install python3-pip"
    exit 1
fi
echo "✓ pip3 found"

# Check for Twisted (required for server)
echo "Checking Twisted web framework..."
if ! python3 -c "import twisted" >/dev/null 2>&1; then
    echo "Error: Twisted web framework is required but not found"
    echo "Install with: pip3 install twisted"
    echo "Or using system packages: apt install python3-twisted"
    exit 1
fi
echo "✓ Twisted web framework found"

# Create service user
echo "Creating service user..."
if ! id "$USER" >/dev/null 2>&1; then
    useradd --system --home-dir "$INSTALL_DIR" --shell /bin/false "$USER"
    echo "✓ User '$USER' created"
else
    echo "✓ User '$USER' already exists"
fi

# Create installation directory
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
echo "✓ Directory '$INSTALL_DIR' created"

# Copy files
echo "Installing Coalition Server files..."
cp "$SCRIPT_DIR"/*.py "$INSTALL_DIR/"
cp "$SCRIPT_DIR/coalition.ini" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/start_server.sh" "$INSTALL_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/public_html" "$INSTALL_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/test" "$INSTALL_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/VERSION" "$INSTALL_DIR/" 2>/dev/null || true

# Set permissions
chown -R "$USER:$USER" "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/start_server.sh" 2>/dev/null || true
echo "✓ Files installed and permissions set"

# Update coalition.ini with server port if different from default
if [ "$SERVER_PORT" != "19211" ]; then
    echo "Configuring server port..."
    sed -i "s|^port=.*|port=$SERVER_PORT|" "$INSTALL_DIR/coalition.ini"
    echo "✓ Server port configured: $SERVER_PORT"
fi

# Create systemd service file
echo "Creating systemd service..."
cp "$SCRIPT_DIR/coalition-server.service" "$SERVICE_FILE"

echo "✓ Systemd service file created"

# Configure firewall using ufw (Ubuntu's default firewall)
echo "Configuring firewall..."
if command -v ufw >/dev/null 2>&1; then
    ufw --force allow "${SERVER_PORT}/tcp" >/dev/null 2>&1 || true
    echo "✓ UFW firewall configured for port $SERVER_PORT"
else
    echo "⚠ UFW firewall not found"
    echo "  Manual firewall configuration may be required"
    echo "  If using iptables, allow port $SERVER_PORT/tcp"
fi

# Reload systemd and enable service
echo "Configuring systemd..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
echo "✓ Service enabled for autostart"

echo ""
echo "============================================================"
echo "INSTALLATION COMPLETE"
echo "============================================================"
echo ""
echo "Service Commands:"
echo "  Start service:    systemctl start $SERVICE_NAME"
echo "  Stop service:     systemctl stop $SERVICE_NAME"
echo "  Restart service:  systemctl restart $SERVICE_NAME"
echo "  Check status:     systemctl status $SERVICE_NAME"
echo "  View logs:        journalctl -u $SERVICE_NAME -f"
echo ""
echo "Configuration:"
echo "  Service file:     $SERVICE_FILE"
echo "  Install directory: $INSTALL_DIR"
echo "  Config file:      $INSTALL_DIR/coalition.ini"
echo "  Web interface:    http://localhost:$SERVER_PORT"
echo "Starting service..."
systemctl start "$SERVICE_NAME"
echo "✓ Service started"
echo ""
echo "Service Status:"
systemctl status "$SERVICE_NAME" --no-pager -l
echo ""
echo "Note: Make sure port $SERVER_PORT is accessible through your firewall"
echo "      for external connections to the Coalition Server."
echo ""