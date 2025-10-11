#!/bin/bash
# Script to rebuild the Docker image with the translation fixes and test them

set -e

IMAGE_NAME="management-tools-dashboard"
CONTAINER_NAME="management-tools-test"

echo "🔧 Rebuilding Docker image with translation fixes..."

# Build the new Docker image
docker build -t $IMAGE_NAME .

echo "✅ Docker image rebuilt successfully!"
echo ""

echo "🚀 Starting container to test fixes..."

# Stop and remove existing test container if it exists
if docker ps -a | grep -q $CONTAINER_NAME; then
    echo "Removing existing test container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Run the database fix script in a temporary container
echo "Running database fix script..."
docker run --name $CONTAINER_NAME-fix \
    -v $(pwd):/app \
    -w /app \
    $IMAGE_NAME \
    python3 fix_docker_database.py

echo "✅ Database fix completed!"
echo ""

# Start the main container
echo "Starting main container for testing..."
docker run -d \
    --name $CONTAINER_NAME \
    -p 8050:8050 \
    -e PORT=8050 \
    -e FLASK_ENV=production \
    -e LOG_LEVEL=INFO \
    $IMAGE_NAME

echo "✅ Container started successfully!"
echo ""
echo "📊 Dashboard will be available at: http://localhost:8050"
echo ""
echo "To test the fix:"
echo "1. Open http://localhost:8050 in your browser"
echo "2. Switch language to English (🇺🇸 EN)"
echo "3. Select a management tool (e.g., Benchmarking)"
echo "4. Select 'Bain Usability' and 'Bain Satisfaction' sources"
echo "5. Verify that the graphs load without errors"
echo ""
echo "To view logs: docker logs -f $CONTAINER_NAME"
echo "To stop: docker stop $CONTAINER_NAME"

# Clean up the temporary container
docker rm $CONTAINER_NAME-fix