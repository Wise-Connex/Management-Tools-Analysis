#!/bin/bash
set -e

echo "🚀 Deploying Key Findings Module..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found. Please create it with your OPENROUTER_API_KEY"
    exit 1
fi

echo "✅ .env file found - using existing configuration"

# Create directories
echo "📁 Creating directories..."
mkdir -p ./data/key_findings
mkdir -p ./data/key_findings/backups

# Create system directory with sudo if needed
if [ ! -d "/var/lib/key_findings_data" ]; then
    echo "🔧 Creating system directory (may require sudo)..."
    sudo mkdir -p /var/lib/key_findings_data || {
        echo "⚠️  Could not create /var/lib/key_findings_data - using local directory instead"
        mkdir -p ./data/key_findings_system
        export KEY_FINDINGS_VOLUME_MOUNT=./data/key_findings_system
    }
fi

# Set permissions
echo "🔒 Setting permissions..."
chmod 755 ./data/key_findings
chmod 755 ./data/key_findings/backups

if [ -d "/var/lib/key_findings_data" ]; then
    sudo chmod 755 /var/lib/key_findings_data
fi

# Deploy with Docker Compose
echo "🐳 Starting Docker deployment..."
docker-compose up --build -d

# Wait for startup
echo "⏳ Waiting for service to start..."
sleep 10

# Health check
echo "🔍 Performing health check..."
if curl -f http://localhost:8050/health > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
    echo "🌐 Access your application at: http://localhost:8050"
else
    echo "❌ Health check failed. Check logs with: docker-compose logs"
    exit 1
fi

echo "🎉 Key Findings module is ready!"