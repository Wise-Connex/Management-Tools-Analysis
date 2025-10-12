#!/bin/bash
set -e

echo "🚀 Deploying Key Findings Module (Simple Version)..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found. Please create it with your OPENROUTER_API_KEY"
    exit 1
fi

echo "✅ .env file found - using existing configuration"

# Create local directories (no sudo required)
echo "📁 Creating local directories..."
mkdir -p ./data/key_findings
mkdir -p ./data/key_findings/backups
mkdir -p ./data/key_findings_system

# Set permissions
echo "🔒 Setting permissions..."
chmod 755 ./data/key_findings
chmod 755 ./data/key_findings/backups
chmod 755 ./data/key_findings_system

# Deploy with Docker Compose
echo "🐳 Starting Docker deployment..."
docker-compose up --build -d

# Wait for startup
echo "⏳ Waiting for service to start..."
sleep 15

# Health check
echo "🔍 Performing health check..."
if curl -f http://localhost:8050/health > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
    echo "🌐 Access your application at: http://localhost:8050"
    echo ""
    echo "🧠 To test Key Findings:"
    echo "1. Select a Management Tool from dropdown"
    echo "2. Select Data Sources (at least one)"
    echo "3. Click '🧠 Generar Key Findings' button"
    echo "4. Verify AI-generated content appears"
else
    echo "❌ Health check failed. Check logs with: docker-compose logs"
    echo ""
    echo "🔍 Debugging commands:"
    echo "docker-compose logs dashboard-app"
    echo "docker ps"
    echo "curl http://localhost:8050/health"
    exit 1
fi

echo "🎉 Key Findings module is ready!"