#!/bin/bash

# Coalition Server v3.0 Release Packaging Script
# This script creates release packages for Coalition Server and Worker

VERSION="3.0"
DATE=$(date '+%Y-%m-%d')
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RELEASE_BASE_DIR="${BASE_DIR}/releases/v${VERSION}"

echo "============================================================"
echo "Coalition Server v${VERSION} Release Packaging"
echo "============================================================"

# Clean and create release directories
echo "Creating release directories..."
rm -rf "${RELEASE_BASE_DIR}"
mkdir -p "${RELEASE_BASE_DIR}/coalition-server-v${VERSION}"
mkdir -p "${RELEASE_BASE_DIR}/coalition-worker-v${VERSION}"

echo "✓ Release directories created"

# ==============================================================
# COALITION SERVER PACKAGE
# ==============================================================
echo ""
echo "Packaging Coalition Server..."

SERVER_DIR="${RELEASE_BASE_DIR}/coalition-server-v${VERSION}"

# Core server files
echo "  → Copying core server files..."
cp "${BASE_DIR}/server.py" "${SERVER_DIR}/"
cp "${BASE_DIR}/control.py" "${SERVER_DIR}/"
cp "${BASE_DIR}/host_cpu.py" "${SERVER_DIR}/"
cp "${BASE_DIR}/host_mem.py" "${SERVER_DIR}/"
cp "${BASE_DIR}/job.py" "${SERVER_DIR}/"

# Web interface files
echo "  → Copying web interface files..."
cp -r "${BASE_DIR}/public_html" "${SERVER_DIR}/"

# Documentation
echo "  → Copying documentation..."
cp "${BASE_DIR}/CLAUDE.md" "${SERVER_DIR}/README.md"
cp "${BASE_DIR}/LICENCE" "${SERVER_DIR}/" 2>/dev/null || echo "    (LICENCE file not found, skipping)"

# Configuration and scripts
echo "  → Copying configuration and utility scripts..."
cp "${BASE_DIR}/coalition.ini" "${SERVER_DIR}/"
cp "${BASE_DIR}/coalition-server.service" "${SERVER_DIR}/"
cp "${BASE_DIR}/install_server_service_rhel.sh" "${SERVER_DIR}/"
cp "${BASE_DIR}/coalition-server" "${SERVER_DIR}/" 2>/dev/null || echo "    (coalition-server script not found, skipping)"
cp "${BASE_DIR}/install-server.sh" "${SERVER_DIR}/" 2>/dev/null || echo "    (install-server.sh not found, skipping)"
cp "${BASE_DIR}/cleaner.sh" "${SERVER_DIR}/" 2>/dev/null || echo "    (cleaner.sh not found, skipping)"
cp "${BASE_DIR}/deploy.sh" "${SERVER_DIR}/" 2>/dev/null || echo "    (deploy.sh not found, skipping)"

# Test suite
echo "  → Copying test suite..."
cp -r "${BASE_DIR}/test" "${SERVER_DIR}/"

# Version information
echo "  → Creating version information..."
cat > "${SERVER_DIR}/VERSION" << EOF
Coalition Server v${VERSION}
Release Date: ${DATE}
Python Version: Python 3.6+
Platform: Cross-platform (Linux, Windows)

Components:
- Coalition Server (server.py)
- Control Client (control.py)
- Web Interface (public_html/)
- System Utilities (host_cpu.py, host_mem.py)
- Test Suite (test/)
- RHEL 8+ Service Installation (install_server_service_rhel.sh)

For documentation see README.md

RHEL 8+ Service Installation:
For production deployment on RHEL 8+ systems, use:
  sudo ./install_server_service_rhel.sh [PORT]

This will install Coalition Server as a systemd service with:
- Auto-start on boot
- Auto-restart on failure  
- Dedicated system user
- Firewall configuration
- Security hardening
EOF

# Create server-specific startup script
cat > "${SERVER_DIR}/start_server.sh" << 'EOF'
#!/bin/bash
# Coalition Server Startup Script

echo "Starting Coalition Server..."
echo "Press Ctrl+C to stop"

# Check Python version
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is required but not found"
    echo "Please install Python 3.6 or later"
    exit 1
fi

# Check for required Python modules
python3 -c "import twisted" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Twisted web framework is required"
    echo "Install with: pip3 install twisted"
    exit 1
fi

# Start server
python3 server.py "$@"
EOF

chmod +x "${SERVER_DIR}/start_server.sh"

echo "✓ Coalition Server package completed"

# ==============================================================
# COALITION WORKER PACKAGE
# ==============================================================
echo ""
echo "Packaging Coalition Worker..."

WORKER_DIR="${RELEASE_BASE_DIR}/coalition-worker-v${VERSION}"

# Core worker files
echo "  → Copying core worker files..."
cp "${BASE_DIR}/worker.py" "${WORKER_DIR}/"
cp "${BASE_DIR}/host_cpu.py" "${WORKER_DIR}/"
cp "${BASE_DIR}/host_mem.py" "${WORKER_DIR}/"
cp "${BASE_DIR}/job.py" "${WORKER_DIR}/"
cp "${BASE_DIR}/coalition.ini" "${WORKER_DIR}/"
cp "${BASE_DIR}/coalition-worker.service" "${WORKER_DIR}/"

# Documentation (worker-specific)
echo "  → Creating worker documentation..."
cat > "${WORKER_DIR}/README.md" << EOF
# Coalition Worker v${VERSION}

Coalition Worker is the job execution component of the Coalition distributed computing system.

## Quick Start

### Basic Usage
\`\`\`bash
# Auto-discover server
./start_worker.sh

# Connect to specific server
./start_worker.sh http://server:19211

# Run multiple workers
./start_worker.sh -w 4 http://server:19211
\`\`\`

### Requirements
- Python 3.6+
- Network access to Coalition Server

### Features
- Automatic server discovery via broadcast
- Multiple worker instances per machine
- System load and memory monitoring
- Cross-platform support (Linux, Windows)
- Worker affinity support

### Configuration
Workers can be configured via command line arguments:
- \`-w N\`: Number of worker processes (default: 1)
- \`-v\`: Verbose output
- \`server_url\`: Coalition Server URL

### System Integration
For production deployments, consider:
- Running workers as system services
- Configuring worker affinity based on hardware
- Setting up monitoring and logging
- Implementing automatic restart on failure

#### RHEL 8+ Service Installation
For RHEL 8+ systems, use the included service installation script:
\`\`\`bash
# Install as system service with auto-discovery
sudo ./install_worker_service_rhel.sh

# Install with specific server URL
sudo ./install_worker_service_rhel.sh http://server:19211

# Install with specific server URL and worker count
sudo ./install_worker_service_rhel.sh http://server:19211 4
\`\`\`

The service will be installed as 'coalition-worker' and configured to:
- Start automatically on boot
- Run as dedicated 'coalition' user
- Restart on failure
- Log to systemd journal

For complete documentation, see the Coalition Server documentation.
EOF

# Copy license if available
cp "${BASE_DIR}/LICENCE" "${WORKER_DIR}/" 2>/dev/null || echo "    (LICENCE file not found, skipping)"

# Version information for worker
cat > "${WORKER_DIR}/VERSION" << EOF
Coalition Worker v${VERSION}
Release Date: ${DATE}
Python Version: Python 3.6+
Platform: Cross-platform (Linux, Windows)

Components:
- Coalition Worker (worker.py)
- System Monitoring (host_cpu.py, host_mem.py)
- Job Execution (job.py)

Compatible with Coalition Server v${VERSION}
For documentation see README.md
EOF

# Create worker-specific startup script
cat > "${WORKER_DIR}/start_worker.sh" << 'EOF'
#!/bin/bash
# Coalition Worker Startup Script

echo "Starting Coalition Worker..."
echo "Press Ctrl+C to stop"

# Check Python version
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is required but not found"
    echo "Please install Python 3.6 or later"
    exit 1
fi

# Default to auto-discovery if no server specified
if [ $# -eq 0 ]; then
    echo "Auto-discovering Coalition Server..."
    echo "Use: $0 http://server:19211 to specify server manually"
    echo ""
fi

# Start worker
python3 worker.py "$@"
EOF

chmod +x "${WORKER_DIR}/start_worker.sh"

# Create RHEL 8+ systemd service installation script
echo "  → Creating RHEL service installation script..."
cat > "${WORKER_DIR}/install_worker_service_rhel.sh" << 'EOF'
#!/bin/bash
# Coalition Worker RHEL 8+ Service Installation Script
# This script installs Coalition Worker as a systemd service on RHEL 8+ systems

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="coalition-worker"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
INSTALL_DIR="/opt/coalition-worker"
USER="coalition"

echo "============================================================"
echo "Coalition Worker Service Installation for RHEL 8+"
echo "============================================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root"
   echo "Usage: sudo ./install_worker_service_rhel.sh [SERVER_URL] [WORKERS_COUNT]"
   exit 1
fi

# Parse command line arguments
SERVER_URL="${1:-}"
WORKERS_COUNT="${2:-1}"

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
cat > "$SERVICE_FILE" << SERVICEEOF
[Unit]
Description=Coalition Worker
Documentation=file://$INSTALL_DIR/README.md
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/worker.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=coalition-worker

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
SERVICEEOF

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
echo ""
echo "To start the service now:"
echo "  systemctl start $SERVICE_NAME"
echo ""
EOF

chmod +x "${WORKER_DIR}/install_worker_service_rhel.sh"

echo "✓ Coalition Worker package completed"

# ==============================================================
# CREATE ARCHIVES
# ==============================================================
echo ""
echo "Creating release archives..."

cd "${RELEASE_BASE_DIR}"

# Create tar.gz archives
echo "  → Creating coalition-server-v${VERSION}.tar.gz..."
tar -czf "coalition-server-v${VERSION}.tar.gz" "coalition-server-v${VERSION}/"

echo "  → Creating coalition-worker-v${VERSION}.tar.gz..."
tar -czf "coalition-worker-v${VERSION}.tar.gz" "coalition-worker-v${VERSION}/"

# Create zip archives for Windows compatibility
if command -v zip >/dev/null 2>&1; then
    echo "  → Creating coalition-server-v${VERSION}.zip..."
    zip -r "coalition-server-v${VERSION}.zip" "coalition-server-v${VERSION}/" >/dev/null
    
    echo "  → Creating coalition-worker-v${VERSION}.zip..."
    zip -r "coalition-worker-v${VERSION}.zip" "coalition-worker-v${VERSION}/" >/dev/null
else
    echo "  → Zip not available, skipping .zip archives"
fi

# ==============================================================
# SUMMARY
# ==============================================================
echo ""
echo "============================================================"
echo "RELEASE PACKAGING COMPLETE"
echo "============================================================"
echo ""
echo "Release directory: ${RELEASE_BASE_DIR}"
echo ""
echo "📦 Coalition Server Package:"
echo "   Directory: coalition-server-v${VERSION}/"
echo "   Archive:   coalition-server-v${VERSION}.tar.gz"
if command -v zip >/dev/null 2>&1; then
echo "   Archive:   coalition-server-v${VERSION}.zip"
fi
echo ""
echo "📦 Coalition Worker Package:"
echo "   Directory: coalition-worker-v${VERSION}/"
echo "   Archive:   coalition-worker-v${VERSION}.tar.gz"
if command -v zip >/dev/null 2>&1; then
echo "   Archive:   coalition-worker-v${VERSION}.zip"
fi
echo ""

# Show file sizes
echo "📊 Package Sizes:"
ls -lh "${RELEASE_BASE_DIR}"/*.tar.gz "${RELEASE_BASE_DIR}"/*.zip 2>/dev/null | awk '{print "   " $9 ": " $5}'

echo ""
echo "✅ Ready for distribution!"
echo ""
echo "To test the packages:"
echo "  cd ${RELEASE_BASE_DIR}/coalition-server-v${VERSION} && ./start_server.sh"
echo "  cd ${RELEASE_BASE_DIR}/coalition-worker-v${VERSION} && ./start_worker.sh"
echo ""