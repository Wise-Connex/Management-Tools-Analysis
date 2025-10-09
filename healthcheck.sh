#!/bin/sh
# Health Check Script for Dash Dashboard
# Used by Docker HEALTHCHECK and Dokploy monitoring

set -e

# Configuration
HEALTH_URL="http://localhost:${PORT:-8050}/health"
MAX_RETRIES=3
RETRY_DELAY=2
TIMEOUT=5

# Colors for output (if terminal supports it)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check health endpoint
check_health() {
    local attempt=$1
    
    # Use curl to check health endpoint
    if curl -f -s -m "$TIMEOUT" "$HEALTH_URL" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check database files
check_databases() {
    if [ ! -f "/app/dashboard_app/data.db" ]; then
        echo "${YELLOW}WARNING: data.db not found${NC}" >&2
        return 1
    fi
    
    if [ ! -f "/app/dashboard_app/notes_and_doi.db" ]; then
        echo "${YELLOW}WARNING: notes_and_doi.db not found${NC}" >&2
        return 1
    fi
    
    return 0
}

# Main health check logic
main() {
    local retry=0
    
    # Try health endpoint with retries
    while [ $retry -lt $MAX_RETRIES ]; do
        if check_health $((retry + 1)); then
            # Health endpoint responded successfully
            
            # Optional: Check database files
            if check_databases; then
                echo "${GREEN}✓ Health check passed${NC}" >&2
                exit 0
            else
                echo "${YELLOW}⚠ Health check passed but database warnings${NC}" >&2
                exit 0  # Still pass health check
            fi
        fi
        
        retry=$((retry + 1))
        
        if [ $retry -lt $MAX_RETRIES ]; then
            echo "${YELLOW}Health check attempt $retry failed, retrying in ${RETRY_DELAY}s...${NC}" >&2
            sleep $RETRY_DELAY
        fi
    done
    
    # All retries failed
    echo "${RED}✗ Health check failed after $MAX_RETRIES attempts${NC}" >&2
    exit 1
}

# Run main function
main