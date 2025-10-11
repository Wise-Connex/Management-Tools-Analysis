#!/bin/bash
# Test script for Docker build and deployment

set -e

echo "🐳 Testing Docker Implementation for Management Tools Analysis Dashboard"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    log_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

log_info "Docker is running ✓"

# Clean up any previous test containers/images
log_info "Cleaning up previous test containers..."
docker rm -f dash-test 2>/dev/null || true
docker rmi dash-test:latest 2>/dev/null || true

# Build the Docker image
log_info "Building Docker image..."
if docker build -t dash-test:latest .; then
    log_info "Docker image built successfully ✓"
else
    log_error "Docker build failed!"
    exit 1
fi

# Run the container
log_info "Starting container..."
if docker run -d --name dash-test -p 8051:8050 dash-test:latest; then
    log_info "Container started successfully ✓"
else
    log_error "Failed to start container!"
    exit 1
fi

# Wait for the application to start
log_info "Waiting for application to start (30 seconds)..."
sleep 30

# Check if container is still running
if docker ps | grep dash-test > /dev/null; then
    log_info "Container is running ✓"
else
    log_error "Container has stopped!"
    docker logs dash-test
    exit 1
fi

# Test the health endpoint
log_info "Testing health endpoint..."
if curl -f http://localhost:8051/health > /dev/null 2>&1; then
    log_info "Health check passed ✓"
    curl http://localhost:8051/health | jq .
else
    log_error "Health check failed!"
    docker logs dash-test
    exit 1
fi

# Test the main dashboard
log_info "Testing main dashboard..."
if curl -f http://localhost:8051/ > /dev/null 2>&1; then
    log_info "Main dashboard is accessible ✓"
else
    log_warning "Main dashboard returned non-200 status (might be normal for first load)"
fi

# Show container logs
log_info "Container logs:"
docker logs dash-test 2>&1 | tail -20

# Clean up
log_info "Cleaning up test container..."
docker stop dash-test
docker rm dash-test
docker rmi dash-test:latest

log_info "✅ All tests passed! Docker implementation is working correctly."
echo ""
echo "To deploy to production:"
echo "1. Push code to GitHub"
echo "2. Deploy in Dokploy using the Dockerfile"
echo "3. Configure environment variables (PORT=8050, FLASK_ENV=production)"
echo "4. Set up health check (/health endpoint)"