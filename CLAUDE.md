# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Coalition Server is a distributed job queue and farm management system written in Python 3. It consists of a central server that manages job queues and multiple workers that execute tasks. The system provides a web interface for job management and supports features like job dependencies, priorities, and worker affinity.

## Core Architecture

The system has three main components:

1. **Server (`server.py`)** - Central coordinator using Twisted web framework
   - Manages job queues, worker registration, and heartbeats
   - Provides XML-RPC and JSON APIs at `/xmlrpc/` and `/json/` endpoints
   - Serves web UI from `public_html/` directory
   - Persists state in `master_db` file using cPickle
   - Handles job states: WAITING → WORKING → FINISHED/ERROR

2. **Worker (`worker.py`)** - Job execution nodes
   - Connects to server via HTTP API at `/workers/` endpoints
   - Executes jobs as subprocesses with output capture
   - Supports multiple worker instances per machine
   - Reports system load and memory usage via `host_cpu.py` and `host_mem.py`

3. **Control Client (`control.py`)** - Command-line interface
   - Add/list/remove jobs via server's JSON API
   - Supports job properties like priority, affinity, dependencies

## Key Classes and Data Structures

- `Job` - Job definition with command, directory, priority, retry count, dependencies
- `Worker` - Worker node with affinity, load metrics, current activity
- `Activity` - Event tracking for job execution history
- `CState` - Master state containing all jobs, workers, and activities

## Development Commands

### Starting the Server
```bash
# Start server on default port 19211
python3 server.py

# Start with custom options
python3 server.py -p 8080 -v  # Custom port with verbose output
```

### Running Workers
```bash
# Auto-discover server via broadcast
python3 worker.py

# Connect to specific server
python3 worker.py http://localhost:19211

# Multiple workers with options
python3 worker.py -w 4 -v http://localhost:19211  # 4 workers, verbose
```

### Managing Jobs
```bash
# Add a job
python3 control.py -t "Test Job" -c "echo hello" http://localhost:19211 add

# List jobs
python3 control.py http://localhost:19211 list

# Remove job by ID
python3 control.py -i 123 http://localhost:19211 remove
```

### System Management
```bash
# Install as system service (Linux)
./install-server.sh

# Control system service
service coalition-server start|stop|restart|status

# Clean old log files
./cleaner.sh
```

## Configuration

The system reads configuration from `coalition.ini` file with sections:
- `[server]` - Server settings (port, timeout, email notifications)
- `[worker]` - Worker settings (server URL, worker count, affinity)

## Important File Locations

- `logs/` - Job execution logs (one file per job ID)
- `master_db*` - Server state persistence and backups
- `server.log` / `worker.log` - Service logs
- `public_html/` - Web interface assets

## Job Execution Flow

1. Jobs submitted to server via API with parent-child hierarchy
2. Server schedules jobs based on dependencies, priority, worker affinity
3. Workers poll server for available jobs matching their capabilities
4. Worker executes job as subprocess, streams output to server
5. Server updates job state and notifies on completion/errors

## Web Interface

The web UI provides real-time job queue monitoring with features:
- Job tree navigation and filtering by state
- Worker status and load monitoring
- Live activity feed showing job assignments
- CSV export functionality via `csv.html`

## Test Server Configuration

**Test Server Details:**
- Host: `opc@10.230.8.90`
- Path: `~/coalition-server`
- Web interface: `http://10.230.8.90:19211`

**Test Server Commands:**
```bash
# Copy files to test server
scp server.py worker.py opc@10.230.8.90:~/coalition-server/

# Start test server
ssh opc@10.230.8.90 "cd ~/coalition-server && python3 server.py"

# Start test server with verbose output
ssh opc@10.230.8.90 "cd ~/coalition-server && python3 server.py -v"

# Stop test server
ssh opc@10.230.8.90 "pkill -f 'python3 server.py'"

# Check test server status
ssh opc@10.230.8.90 "ps aux | grep 'python3 server.py'"
```

**Troubleshooting:**
- If database corruption occurs, backup and remove `master_db` file to start fresh:
  ```bash
  ssh opc@10.230.8.90 "cd ~/coalition-server && mv master_db master_db.backup"
  ```

## Development Notes

- Python 3 codebase using modern libraries (Twisted, pickle)
- Cross-platform support (Windows/Linux) with platform-specific code
- Uses threading for concurrent operations
- Database operations use generator-based coroutines for large saves
- Email notifications for job completion/errors via SMTP