#!/bin/bash
# Entrypoint Script for Dash Dashboard Container
# Handles initialization and graceful startup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

log_info "Starting Dash Dashboard initialization..."

# Check Python version
PYTHON_VERSION=$(python --version 2>&1)
log_info "Python version: $PYTHON_VERSION"

# Check if UV is available
UV_VERSION=$(uv --version 2>&1 || echo "UV not installed")
log_info "UV version: $UV_VERSION"

# Check if running as correct user
CURRENT_USER=$(whoami)
log_info "Running as user: $CURRENT_USER"

# ============================================================================
# Directory Setup
# ============================================================================

log_info "Setting up directories..."

# Create logs directory if it doesn't exist
if [ ! -d "/app/logs" ]; then
    mkdir -p /app/logs
    log_success "Created logs directory"
fi

# Ensure proper permissions
if [ -w "/app/logs" ]; then
    log_success "Logs directory is writable"
else
    log_warning "Logs directory is not writable"
fi

# ============================================================================
# Database Verification
# ============================================================================

log_info "Verifying database files..."

# Check for data.db
if [ -f "/app/dashboard_app/data.db" ]; then
    DB_SIZE=$(du -h /app/dashboard_app/data.db | cut -f1)
    log_success "Found data.db (Size: $DB_SIZE)"
else
    log_error "data.db not found at /app/dashboard_app/data.db"
    log_warning "Application may not function correctly without database"
fi

# Check for notes_and_doi.db
if [ -f "/app/dashboard_app/notes_and_doi.db" ]; then
    NOTES_SIZE=$(du -h /app/dashboard_app/notes_and_doi.db | cut -f1)
    log_success "Found notes_and_doi.db (Size: $NOTES_SIZE)"
else
    log_warning "notes_and_doi.db not found"
fi

# ============================================================================
# Environment Configuration
# ============================================================================

log_info "Environment configuration:"
log_info "  PORT: ${PORT:-8050}"
log_info "  FLASK_ENV: ${FLASK_ENV:-production}"
log_info "  LOG_LEVEL: ${LOG_LEVEL:-info}"
log_info "  MAX_WORKERS: ${MAX_WORKERS:-auto}"
log_info "  WORKER_TIMEOUT: ${WORKER_TIMEOUT:-120}"

# ============================================================================
# Application Verification
# ============================================================================

log_info "Verifying application files..."

# Check if main app file exists
if [ -f "/app/dashboard_app/app.py" ]; then
    log_success "Found dashboard_app/app.py"
else
    log_error "app.py not found!"
    exit 1
fi

# Check if tools.py exists
if [ -f "/app/tools.py" ]; then
    log_success "Found tools.py"
else
    log_warning "tools.py not found"
fi

# Check if database.py exists
if [ -f "/app/database.py" ]; then
    log_success "Found database.py"
else
    log_warning "database.py not found"
fi

# Check if assets directory exists
if [ -d "/app/assets" ]; then
    ASSET_COUNT=$(find /app/assets -type f | wc -l)
    log_success "Found assets directory ($ASSET_COUNT files)"
else
    log_warning "Assets directory not found"
fi

# ============================================================================
# Signal Handling for Graceful Shutdown
# ============================================================================

# Trap SIGTERM and SIGINT for graceful shutdown
trap 'log_info "Received shutdown signal, gracefully stopping..."; exit 0' SIGTERM SIGINT

# ============================================================================
# Startup
# ============================================================================

log_success "Pre-flight checks completed successfully"
log_info "Starting Dash Dashboard with command: $@"
log_info "Dashboard will be available at http://0.0.0.0:${PORT:-8050}"
log_info "Health check endpoint: http://0.0.0.0:${PORT:-8050}/health"

# Execute the command passed to the container
# This will typically be: gunicorn -c gunicorn.conf.py dashboard_app.app:server
exec "$@"