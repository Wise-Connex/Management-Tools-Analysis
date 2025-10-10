#!/bin/bash
# Simple rebuild and test script

set -e

echo "🧹 Cleaning up old containers..."
docker stop dash-test 2>/dev/null || true
docker rm dash-test 2>/dev/null || true

echo ""
echo "🏗️  Building Docker image (forcing rebuild of app layer)..."
docker build --no-cache-filter=stage-1 -t dash-dashboard .

echo ""
echo "🚀 Starting container..."
docker run -d --name dash-test -p 8050:8050 -e MAX_WORKERS=4 dash-dashboard

echo ""
echo "⏳ Waiting 25 seconds for app to start..."
sleep 25

echo ""
echo "🏥 Testing health endpoint..."
curl http://localhost:8050/health

echo ""
echo ""
echo "✅ Container is running!"
echo "🌐 Dashboard: http://localhost:8050"
echo "🏥 Health: http://localhost:8050/health"
echo ""
echo "📋 View logs: docker logs -f dash-test"
echo "🛑 Stop: docker stop dash-test && docker rm dash-test"