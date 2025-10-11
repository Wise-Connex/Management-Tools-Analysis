#!/bin/bash
# Script to rebuild Docker image with the translation fix and test it

echo "========================================"
echo "REBUILDING DOCKER WITH TRANSLATION FIX"
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
mkdir -p docker_test_output

# Build the Docker image
log_info "Building Docker image with translation fix..."
docker build -t dash_dashboard_fixed .

if [ $? -ne 0 ]; then
    log_error "Failed to build Docker image"
    exit 1
fi

log_success "Docker image built successfully"

# Run the test script in Docker
log_info "Running translation test in Docker..."

docker run --rm -v "$(pwd)/test_translation_fix.py:/app/test_translation_fix.py" \
    -v "$(pwd)/docker_test_output:/app/docker_test_output" \
    dash_dashboard_fixed \
    python /app/test_translation_fix.py > docker_test_output/docker_test_results.txt 2>&1

if [ $? -eq 0 ]; then
    log_success "Docker test completed successfully"
else
    log_error "Docker test failed"
fi

# Show the results
log_info "Docker test results:"
cat docker_test_output/docker_test_results.txt

# Check if the test passed
if grep -q "ALL TESTS PASSED" docker_test_output/docker_test_results.txt; then
    log_success "Translation fix is working in Docker!"
    
    # Run the app in Docker and test it
    log_info "Starting the app in Docker for testing..."
    
    # Start the container in background
    CONTAINER_ID=$(docker run -d -p 8051:8050 \
        -v "$(pwd)/dashboard_app/data.db:/app/dashboard_app/data.db" \
        dash_dashboard_fixed)
    
    if [ $? -eq 0 ]; then
        log_success "App started in Docker (container: $CONTAINER_ID)"
        log_info "App is available at http://localhost:8051"
        log_info "Test by switching the language to English and selecting Bain sources"
        
        # Wait for user input
        echo -e "\n${YELLOW}Press Enter to stop the Docker container...${NC}"
        read
        
        # Stop the container
        docker stop $CONTAINER_ID
        docker rm $CONTAINER_ID
        log_success "Docker container stopped and removed"
    else
        log_error "Failed to start app in Docker"
    fi
else
    log_error "Translation fix is NOT working in Docker"
    log_warning "Check docker_test_output/docker_test_results.txt for details"
fi

log_info "Docker testing complete. Check docker_test_output/ directory for detailed results."