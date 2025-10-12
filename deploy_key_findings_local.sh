#!/bin/bash

# Key Findings Local Docker Deployment Script
# This script sets up and runs the Key Findings module locally using Docker
# No sudo required - uses user permissions

set -e  # Exit on any error

echo "🚀 Starting Key Findings Local Docker Deployment..."
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $(pwd)"

# Create necessary directories for local deployment
echo "📂 Creating necessary directories..."
mkdir -p ./data/key_findings
mkdir -p ./logs
mkdir -p ./assets

# Set permissions for local deployment (no sudo needed)
echo "🔐 Setting permissions..."
chmod 755 ./data
chmod 755 ./data/key_findings
chmod 755 ./logs
chmod 755 ./assets

# Check if .env file exists in dashboard_app directory
if [ ! -f "./dashboard_app/.env" ]; then
    echo "⚠️  .env file not found in dashboard_app directory"
    
    # Check if .env exists in root directory and copy API key from there
    if [ -f "./.env" ]; then
        echo "📋 Found .env in root directory, copying API key..."
        
        # Extract API key from root .env
        API_KEY=$(grep "OPENROUTER_API_KEY" "./.env" | cut -d'=' -f2)
        
        if [ ! -z "$API_KEY" ] && [ "$API_KEY" != "your_api_key_here" ]; then
            echo "✅ Found API key in root .env, creating dashboard_app/.env..."
            cat > "./dashboard_app/.env" << EOF
# Key Findings Configuration
OPENROUTER_API_KEY=$API_KEY
KEY_FINDINGS_DB_PATH=./data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=./data/backups/
KEY_FINDINGS_VOLUME_MOUNT=./data/key_findings_data

# Database Configuration
DATABASE_PATH=./dbase/
DATABASE_NON_INDEXED_PATH=./dbase-non-indexed/
NEW_DATABASE_PATH=./NewDBase/

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8050
EOF
            echo "✅ dashboard_app/.env created with your API key"
        else
            echo "⚠️  No valid API key found in root .env"
            echo "Creating .env file from template..."
            
            if [ -f "./dashboard_app/.env.example" ]; then
                cp "./dashboard_app/.env.example" "./dashboard_app/.env"
                echo "✅ .env file created from .env.example"
                echo "📝 Please edit dashboard_app/.env and add your OPENROUTER_API_KEY"
            else
                echo "❌ .env.example file not found. Creating basic .env file..."
                cat > "./dashboard_app/.env" << EOF
# Key Findings Configuration
OPENROUTER_API_KEY=your_api_key_here
KEY_FINDINGS_DB_PATH=./data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=./data/backups/
KEY_FINDINGS_VOLUME_MOUNT=./data/key_findings_data

# Database Configuration
DATABASE_PATH=./dbase/
DATABASE_NON_INDEXED_PATH=./dbase-non-indexed/
NEW_DATABASE_PATH=./NewDBase/

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8050
EOF
                echo "✅ Basic .env file created"
                echo "📝 Please edit dashboard_app/.env and add your OPENROUTER_API_KEY"
            fi
        fi
    else
        echo "Creating .env file from template..."
        
        if [ -f "./dashboard_app/.env.example" ]; then
            cp "./dashboard_app/.env.example" "./dashboard_app/.env"
            echo "✅ .env file created from .env.example"
            echo "📝 Please edit dashboard_app/.env and add your OPENROUTER_API_KEY"
        else
            echo "❌ .env.example file not found. Creating basic .env file..."
            cat > "./dashboard_app/.env" << EOF
# Key Findings Configuration
OPENROUTER_API_KEY=your_api_key_here
KEY_FINDINGS_DB_PATH=./data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=./data/backups/
KEY_FINDINGS_VOLUME_MOUNT=./data/key_findings_data

# Database Configuration
DATABASE_PATH=./dbase/
DATABASE_NON_INDEXED_PATH=./dbase-non-indexed/
NEW_DATABASE_PATH=./NewDBase/

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8050
EOF
            echo "✅ Basic .env file created"
            echo "📝 Please edit dashboard_app/.env and add your OPENROUTER_API_KEY"
        fi
    fi
fi

# Check if API key is configured
if grep -q "your_api_key_here" "./dashboard_app/.env"; then
    echo "⚠️  WARNING: OPENROUTER_API_KEY is not configured!"
    echo "Please edit dashboard_app/.env and add your API key before running the application."
    echo "You can get an API key from: https://openrouter.ai/"
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled. Please configure your API key first."
        exit 1
    fi
else
    echo "✅ API key is configured in dashboard_app/.env"
fi

# Create docker-compose.override.yml for local development
echo "📝 Creating Docker Compose override for local development..."
cat > docker-compose.override.yml << EOF
services:
  dash:
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./dashboard_app/.env:/app/.env
    environment:
      - KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
      - KEY_FINDINGS_BACKUP_PATH=/app/data/backups/
      - DEBUG=True
    ports:
      - "8050:8050"
    restart: unless-stopped
EOF

echo "✅ Docker Compose override created"

# Build and start the containers
echo "🔨 Building Docker image..."
docker-compose build --no-cache

echo "🚀 Starting containers..."
docker-compose up -d

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if the application is running
if curl -s http://localhost:8050/health > /dev/null; then
    echo "✅ Application is running successfully!"
    echo ""
    echo "🌐 Access the application at: http://localhost:8050"
    echo "🧠 Key Findings module is now available"
    echo ""
    echo "📊 To view logs:"
    echo "  docker-compose logs -f dash"
    echo ""
    echo "🛑 To stop the application:"
    echo "  docker-compose down"
    echo ""
    echo "🔄 To restart the application:"
    echo "  docker-compose restart"
    echo ""
    echo "📁 Data persistence:"
    echo "  - Database: ./data/key_findings.db"
    echo "  - Backups: ./data/backups/"
    echo "  - Logs: ./logs/"
else
    echo "❌ Application failed to start properly"
    echo "📋 Checking logs..."
    docker-compose logs dash
    echo ""
    echo "🔧 Troubleshooting:"
    echo "1. Check if port 8050 is available"
    echo "2. Verify your .env configuration"
    echo "3. Check Docker logs with: docker-compose logs dash"
    exit 1
fi

echo ""
echo "🎉 Key Findings Local Deployment Complete!"
echo "=================================================="