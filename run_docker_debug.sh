#!/bin/bash
# Script to run the debug script inside the Docker container

set -e

IMAGE_NAME="management-tools-dashboard"
CONTAINER_NAME="management-tools-debug"

echo "🐳 Starting Docker debug session..."

# Stop and remove existing debug container if it exists
if docker ps -a | grep -q $CONTAINER_NAME; then
    echo "Removing existing debug container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Run the debug script in a new container
echo "Running debug script in Docker container..."
docker run --name $CONTAINER_NAME \
    -v $(pwd):/app \
    -w /app \
    $IMAGE_NAME \
    python debug_docker_translation.py > docker_debug_output.txt 2>&1

echo "Debug complete! Output saved to docker_debug_output.txt"

# Display the output
echo "=== DOCKER DEBUG OUTPUT ==="
cat docker_debug_output.txt

# Clean up
docker rm $CONTAINER_NAME

echo "Debug session completed."