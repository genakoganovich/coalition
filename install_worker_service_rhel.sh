#!/bin/bash
# Coalition Worker RHEL 8+ Service Installation Script
# This script installs Coalition Worker as a systemd service on RHEL 8+ systems

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="coalition-worker"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
INSTALL_DIR="/opt/coalition-worker"

echo "============================================================"
echo "Coalition Worker Service Installation for RHEL 8+"
echo "============================================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root"
   echo "Usage: sudo ./install_worker_service_rhel.sh <USERNAME> [SERVER_URL] [WORKERS_COUNT]"
   exit 1
fi

# Parse command line arguments
USER="${1:-}"
SERVER_URL="${2:-}"
WORKERS_COUNT="${3:-1}"

# Check if username is provided
if [[ -z "$USER" ]]; then
   echo "Error: Username is mandatory"
   echo "Usage: sudo ./install_worker_service_rhel.sh <USERNAME> [SERVER_URL] [WORKERS_COUNT]"
   echo ""
   echo "Arguments:"
   echo "  USERNAME       - The user account that will run the service (mandatory)"
   echo "  SERVER_URL     - Coalition server URL (optional, auto-discover if not provided)"
   echo "  WORKERS_COUNT  - Number of worker processes (optional, default: 1)"
   exit 1
fi

echo "Configuration:"
echo "  Service Name: ${SERVICE_NAME}"
echo "  Install Directory: ${INSTALL_DIR}"
echo "  Service User: ${USER}"
echo "  Server URL: ${SERVER_URL:-Auto-discover}"
echo "  Worker Count: ${WORKERS_COUNT}"
echo ""

# Check RHEL version
if [ -f /etc/redhat-release ]; then
    RHEL_VERSION=$(grep -oE 'release [0-9]+' /etc/redhat-release | awk '{print $2}')
    if [ "$RHEL_VERSION" -lt 8 ]; then
        echo "Error: This script requires RHEL 8 or higher"
        echo "Current version: RHEL $RHEL_VERSION"
        exit 1
    fi
    echo "✓ RHEL $RHEL_VERSION detected"
else
    echo "Warning: Could not detect RHEL version, proceeding anyway..."
fi

# Check Python 3
echo "Checking Python 3..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required but not found"
    echo "Install with: dnf install python3"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"

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
echo "Installing Coalition Worker files..."
cp "$SCRIPT_DIR"/*.py "$INSTALL_DIR/"
cp "$SCRIPT_DIR/coalition.ini" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/start_worker.sh" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/VERSION" "$INSTALL_DIR/" 2>/dev/null || true

# Set permissions
chown -R "$USER:$USER" "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/start_worker.sh"
echo "✓ Files installed and permissions set"

# Update coalition.ini with server URL if provided
if [ -n "$SERVER_URL" ]; then
    echo "Configuring server URL..."
    sed -i "s|^serverUrl=.*|serverUrl=$SERVER_URL|" "$INSTALL_DIR/coalition.ini"
    echo "✓ Server URL configured: $SERVER_URL"
fi

# Update coalition.ini with worker count
if [ "$WORKERS_COUNT" != "1" ]; then
    echo "Configuring worker count..."
    if grep -q "^#workers=" "$INSTALL_DIR/coalition.ini"; then
        sed -i "s|^#workers=.*|workers=$WORKERS_COUNT|" "$INSTALL_DIR/coalition.ini"
    else
        echo "workers=$WORKERS_COUNT" >> "$INSTALL_DIR/coalition.ini"
    fi
    echo "✓ Worker count configured: $WORKERS_COUNT"
fi

# Create systemd service file
echo "Creating systemd service..."
cp "$SCRIPT_DIR/coalition-worker.service" "$SERVICE_FILE"

echo "✓ Systemd service file created"

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
echo "Starting service..."
systemctl start "$SERVICE_NAME"
echo "✓ Service started"
echo ""
echo "Service Status:"
systemctl status "$SERVICE_NAME" --no-pager -l
echo ""
