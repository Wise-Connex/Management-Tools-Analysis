#!/bin/bash
# Script to run translation debugging both locally and in Docker

echo "========================================"
echo "TRANSLATION DEBUG COMPARISON SCRIPT"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Create output directory
mkdir -p debug_output

# Run debug locally
log_info "Running translation debug locally..."
python debug_docker_translation_comprehensive.py > debug_output/local_debug.txt 2>&1

if [ $? -eq 0 ]; then
    log_success "Local debug completed successfully"
else
    log_error "Local debug failed"
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    log_warning "Docker not available, skipping Docker debug"
    exit 0
fi

# Check if the Docker image exists
IMAGE_NAME="dash_dashboard"
if ! docker image inspect $IMAGE_NAME &> /dev/null; then
    log_info "Docker image not found, building it..."
    docker build -t $IMAGE_NAME .
    
    if [ $? -ne 0 ]; then
        log_error "Failed to build Docker image"
        exit 1
    fi
    
    log_success "Docker image built successfully"
fi

# Run debug in Docker
log_info "Running translation debug in Docker..."

# Create a container with the debug script mounted
docker run --rm -v "$(pwd)/debug_docker_translation_comprehensive.py:/app/debug_docker_translation_comprehensive.py" \
    -v "$(pwd)/debug_output:/app/debug_output" \
    $IMAGE_NAME \
    python /app/debug_docker_translation_comprehensive.py > debug_output/docker_debug.txt 2>&1

if [ $? -eq 0 ]; then
    log_success "Docker debug completed successfully"
else
    log_error "Docker debug failed"
fi

# Compare results
log_info "Comparing local and Docker debug results..."

if [ -f "debug_output/local_debug.txt" ] && [ -f "debug_output/docker_debug.txt" ]; then
    echo "========================================"
    echo "DIFFERENCES BETWEEN LOCAL AND DOCKER"
    echo "========================================"
    diff -u debug_output/local_debug.txt debug_output/docker_debug.txt > debug_output/diff.txt
    
    if [ -s "debug_output/diff.txt" ]; then
        log_warning "Differences found between local and Docker"
        echo "See debug_output/diff.txt for details"
        
        # Show first 20 lines of differences
        echo "First 20 lines of differences:"
        head -20 debug_output/diff.txt
    else
        log_success "No differences found between local and Docker"
    fi
    
    echo "========================================"
    echo "KEY SECTIONS FROM DOCKER DEBUG"
    echo "========================================"
    
    # Extract key sections from Docker debug
    echo -e "\n--- TRANSLATION FUNCTION TESTING ---"
    grep -A 20 "TRANSLATION FUNCTION TESTING" debug_output/docker_debug.txt || echo "Section not found"
    
    echo -e "\n--- SOURCE MAPPING TESTING ---"
    grep -A 20 "SOURCE MAPPING TESTING" debug_output/docker_debug.txt || echo "Section not found"
    
    echo -e "\n--- DATABASE ACCESS TESTING ---"
    grep -A 20 "DATABASE ACCESS TESTING" debug_output/docker_debug.txt || echo "Section not found"
    
    echo -e "\n--- APP IMPORTS TESTING ---"
    grep -A 20 "APP IMPORTS TESTING" debug_output/docker_debug.txt || echo "Section not found"
    
    echo -e "\n--- LANGUAGE SWITCH SIMULATION ---"
    grep -A 20 "LANGUAGE SWITCH SIMULATION" debug_output/docker_debug.txt || echo "Section not found"
else
    log_error "Debug output files not found"
fi

log_info "Debug complete. Check debug_output/ directory for detailed results."