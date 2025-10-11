#!/bin/bash
# Simple script to run the Management Tools Analysis Dashboard in Docker

set -e

IMAGE_NAME="management-tools-dashboard"
CONTAINER_NAME="management-tools"

echo "🐳 Starting Management Tools Analysis Dashboard in Docker"
echo "========================================================"

# Stop and remove existing container if it exists
if docker ps -a | grep -q $CONTAINER_NAME; then
    echo "Stopping existing container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Run the container
echo "Starting container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p 8050:8050 \
    -e PORT=8050 \
    -e FLASK_ENV=production \
    -e LOG_LEVEL=INFO \
    $IMAGE_NAME

echo "Container started successfully!"
echo ""
echo "Dashboard will be available at: http://localhost:8050"
echo "Health check endpoint: http://localhost:8050/health"
echo ""
echo "To view logs: docker logs -f $CONTAINER_NAME"
echo "To stop: docker stop $CONTAINER_NAME"