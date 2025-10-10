#!/bin/bash
# Quick Docker Testing Script
# Tests the Docker build and deployment locally

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="dash-dashboard"
CONTAINER_NAME="dash-test"
PORT=8050

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Docker Local Testing - Dash Dashboard                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# Step 1: Prerequisites Check
# ============================================================================
echo -e "${BLUE}[1/7]${NC} Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    echo "Please start Docker Desktop"
    exit 1
fi

echo -e "${GREEN}✅ Docker is ready ($(docker --version))${NC}"

# ============================================================================
# Step 2: Clean Up Previous Test
# ============================================================================
echo ""
echo -e "${BLUE}[2/7]${NC} Cleaning up previous test containers..."

if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo "Removing existing container..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo -e "${GREEN}✅ Cleaned up${NC}"
else
    echo -e "${GREEN}✅ No cleanup needed${NC}"
fi

# ============================================================================
# Step 3: Build Docker Image
# ============================================================================
echo ""
echo -e "${BLUE}[3/7]${NC} Building Docker image..."
echo "This will take 3-5 minutes on first build..."

if docker build -t "$IMAGE_NAME:test" . ; then
    IMAGE_SIZE=$(docker images "$IMAGE_NAME:test" --format "{{.Size}}")
    echo -e "${GREEN}✅ Build successful (Image size: $IMAGE_SIZE)${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    echo "Check the error messages above"
    exit 1
fi

# ============================================================================
# Step 4: Start Container
# ============================================================================
echo ""
echo -e "${BLUE}[4/7]${NC} Starting container..."

CONTAINER_ID=$(docker run -d \
  --name "$CONTAINER_NAME" \
  -p "$PORT:$PORT" \
  -e FLASK_ENV=production \
  -e LOG_LEVEL=INFO \
  -e PORT="$PORT" \
  "$IMAGE_NAME:test")

if [ -n "$CONTAINER_ID" ]; then
    echo -e "${GREEN}✅ Container started (ID: ${CONTAINER_ID:0:12})${NC}"
else
    echo -e "${RED}❌ Failed to start container${NC}"
    exit 1
fi

# ============================================================================
# Step 5: Wait for Application
# ============================================================================
echo ""
echo -e "${BLUE}[5/7]${NC} Waiting for application to start..."

MAX_WAIT=60
WAIT_TIME=0
SLEEP_INTERVAL=5

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if docker ps | grep -q "$CONTAINER_NAME"; then
        echo -n "."
        sleep $SLEEP_INTERVAL
        WAIT_TIME=$((WAIT_TIME + SLEEP_INTERVAL))
        
        # Try health check
        if curl -s -f "http://localhost:$PORT/health" > /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}✅ Application is ready!${NC}"
            break
        fi
    else
        echo ""
        echo -e "${RED}❌ Container stopped unexpectedly${NC}"
        echo "Logs:"
        docker logs "$CONTAINER_NAME"
        exit 1
    fi
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Timeout waiting for application${NC}"
    echo "Container logs:"
    docker logs "$CONTAINER_NAME"
fi

# ============================================================================
# Step 6: Test Health Endpoint
# ============================================================================
echo ""
echo -e "${BLUE}[6/7]${NC} Testing health endpoint..."

HEALTH_RESPONSE=$(curl -s "http://localhost:$PORT/health")

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "Response:"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "Response: $HEALTH_RESPONSE"
    echo "Container logs:"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# ============================================================================
# Step 7: Display Results
# ============================================================================
echo ""
echo -e "${BLUE}[7/7]${NC} Test Results"
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  🎉 ALL TESTS PASSED! 🎉                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Container Information:${NC}"
docker ps | grep "$CONTAINER_NAME"
echo ""
echo -e "${BLUE}💾 Resource Usage:${NC}"
docker stats --no-stream "$CONTAINER_NAME"
echo ""
echo -e "${BLUE}🌐 Access Points:${NC}"
echo "   Dashboard:  http://localhost:$PORT"
echo "   Health:     http://localhost:$PORT/health"
echo ""
echo -e "${BLUE}📋 Useful Commands:${NC}"
echo "   View logs:  docker logs -f $CONTAINER_NAME"
echo "   Stop:       docker stop $CONTAINER_NAME"
echo "   Remove:     docker rm $CONTAINER_NAME"
echo "   Restart:    docker restart $CONTAINER_NAME"
echo ""
echo -e "${YELLOW}⚠️  Container is still running. Stop it when done testing.${NC}"
echo ""
echo -e "${GREEN}Next step: Deploy to Dokploy! See DEPLOYMENT.md${NC}"
echo ""