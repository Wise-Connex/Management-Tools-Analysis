#!/bin/bash
# Simple script to build and run the Docker container manually

set -e

IMAGE_NAME="management-tools-dashboard"
CONTAINER_NAME="management-tools"

echo "🐳 Building Docker image..."
docker build -t $IMAGE_NAME .

echo "✅ Build complete!"
echo ""
echo "🚀 Starting container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p 8050:8050 \
    -e PORT=8050 \
    -e FLASK_ENV=production \
    $IMAGE_NAME

echo "✅ Container started!"
echo ""
echo "📊 Dashboard will be available at: http://localhost:8050"
echo "🏥 Health check: http://localhost:8050/health"
echo ""
echo "To view logs: docker logs -f $CONTAINER_NAME"
echo "To stop: docker stop $CONTAINER_NAME"