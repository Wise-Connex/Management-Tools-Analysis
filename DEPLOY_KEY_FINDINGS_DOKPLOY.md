# Key Findings Dokploy Deployment Guide

## 🚀 Dokploy-Specific Deployment

### 1. Dokploy Volume Configuration

Dokploy uses specific volume paths that differ from local Docker. Update your deployment:

#### Required Dokploy Environment Variables:

```bash
# Dokploy-specific paths
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=/app/data/backups
KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data

# Dokploy data persistence
DOKPLOY_DATA_PATH=/data/key_findings
```

### 2. Update .env for Dokploy

Create or update your `.env` file with Dokploy-specific settings:

```bash
cat > .env << EOF
# Key Findings Configuration for Dokploy
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=/app/data/backups
KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data
DOKPLOY_DATA_PATH=/data/key_findings

# AI Configuration (REQUIRED)
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
PRIMARY_MODEL=openai/gpt-4o-mini
FALLBACK_MODELS=nvidia/llama-3.1-nemotron-70b-instruct,meta-llama/llama-3.1-8b-instruct:free

# Analysis Parameters
KEY_FINDINGS_PCA_WEIGHT=0.3
KEY_FINDINGS_CONFIDENCE_THRESHOLD=0.7
KEY_FINDINGS_MAX_TOKENS=4000
KEY_FINDINGS_CACHE_TTL=86400
KEY_FINDINGS_MAX_HISTORY=100
KEY_FINDINGS_AUTO_GENERATE=true
KEY_FINDINGS_DEBUG=false
EOF
```

### 3. Dokploy Deployment Script

Create `deploy_key_findings_dokploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying Key Findings Module for Dokploy..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found. Please create it with your OPENROUTER_API_KEY"
    exit 1
fi

echo "✅ .env file found - using Dokploy configuration"

# Create local directories (for Dokploy volume mapping)
echo "📁 Creating Dokploy-compatible directories..."
mkdir -p ./data/key_findings
mkdir -p ./data/key_findings/backups

# Set permissions
echo "🔒 Setting permissions for Dokploy..."
chmod 755 ./data/key_findings
chmod 755 ./data/key_findings/backups

# Deploy with Docker Compose (Dokploy compatible)
echo "🐳 Starting Dokploy deployment..."
docker-compose up --build -d

# Wait for startup
echo "⏳ Waiting for service to start..."
sleep 15

# Health check
echo "🔍 Performing health check..."
if curl -f http://localhost:8050/health > /dev/null 2>&1; then
    echo "✅ Dokploy deployment successful!"
    echo "🌐 Access your application at: http://localhost:8050"
    echo ""
    echo "🧠 To test Key Findings:"
    echo "1. Select a Management Tool from dropdown"
    echo "2. Select Data Sources (at least one)"
    echo "3. Click '🧠 Generar Key Findings' button"
    echo "4. Verify AI-generated content appears"
    echo ""
    echo "📊 Dokploy persistence is automatically configured!"
else
    echo "❌ Health check failed. Check logs with: docker-compose logs"
    echo ""
    echo "🔍 Debugging commands:"
    echo "docker-compose logs dashboard-app"
    echo "docker ps"
    echo "curl http://localhost:8050/health"
    exit 1
fi

echo "🎉 Key Findings module is ready on Dokploy!"
```

### 4. Docker Compose for Dokploy

Update your `docker-compose.yml` for Dokploy volumes:

```yaml
version: "3.8"

services:
  dashboard-app:
    build: .
    container_name: management-tools-dashboard
    ports:
      - "8050:8050"
    volumes:
      # Dokploy-specific volume mapping
      - ./data/key_findings:/app/data:rw
      - ./data/key_findings/backups:/app/data/backups:rw
      # Dokploy persistent volume
      - /var/lib/key_findings_data:/var/lib/key_findings_data:rw
    environment:
      # Load from .env file
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
      - KEY_FINDINGS_BACKUP_PATH=/app/data/backups
      - KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data
      - PRIMARY_MODEL=${PRIMARY_MODEL:-openai/gpt-4o-mini}
      - FALLBACK_MODELS=${FALLBACK_MODELS:-nvidia/llama-3.1-nemotron-70b-instruct,meta-llama/llama-3.1-8b-instruct:free}
      - KEY_FINDINGS_PCA_WEIGHT=${KEY_FINDINGS_PCA_WEIGHT:-0.3}
      - KEY_FINDINGS_CONFIDENCE_THRESHOLD=${KEY_FINDINGS_CONFIDENCE_THRESHOLD:-0.7}
      - KEY_FINDINGS_MAX_TOKENS=${KEY_FINDINGS_MAX_TOKENS:-4000}
      - KEY_FINDINGS_CACHE_TTL=${KEY_FINDINGS_CACHE_TTL:-86400}
      - KEY_FINDINGS_MAX_HISTORY=${KEY_FINDINGS_MAX_HISTORY:-100}
      - KEY_FINDINGS_AUTO_GENERATE=${KEY_FINDINGS_AUTO_GENERATE:-true}
      - KEY_FINDINGS_DEBUG=${KEY_FINDINGS_DEBUG:-false}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8050/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  # Dokploy persistent volume
  key_findings_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /var/lib/key_findings_data
```

### 5. Dokploy Deployment Commands

```bash
# Make script executable
chmod +x deploy_key_findings_dokploy.sh

# Deploy to Dokploy
./deploy_key_findings_dokploy.sh

# Verify Dokploy persistence
curl http://localhost:8050/health | jq '.database_metrics.persistence_status'
```

### 6. Dokploy-Specific Verification

```bash
# Check if Dokploy volume is properly mounted
docker exec management-tools-dashboard python -c "
import os
print(f'Database path: {os.environ.get(\"KEY_FINDINGS_DB_PATH\", \"not set\")}')
print(f'Volume mount: {os.environ.get(\"KEY_FINDINGS_VOLUME_MOUNT\", \"not set\")}')
print(f'Data directory exists: {os.path.exists(\"/app/data\")}')
"

# Test database persistence in Dokploy
docker exec management-tools-dashboard python -c "
from key_findings.database_manager import KeyFindingsDBManager
db = KeyFindingsDBManager('/app/data/key_findings.db')
persistence_ok = db.verify_persistence()
print(f'Dokploy persistence working: {persistence_ok}')
"
```

### 7. Dokploy Environment Variables

Dokploy automatically sets these environment variables:

```bash
# Dokploy-specific
DOKPLOY_DATA_PATH=/data/key_findings
DOKPLOY_BACKUP_PATH=/data/key_findings/backups

# Application paths (already configured in .env)
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=/app/data/backups
KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data
```

### 8. Troubleshooting for Dokploy

#### Volume Mount Issues:

```bash
# Check volume mounts
docker exec management-tools-dashboard df -h

# Check permissions
docker exec management-tools-dashboard ls -la /app/data/

# Test write access
docker exec management-tools-dashboard touch /app/data/test.txt
```

#### Database Issues in Dokploy:

```bash
# Check database location
docker exec management-tools-dashboard find /app -name "*.db"

# Test database connectivity
docker exec management-tools-dashboard python -c "
from key_findings.database_manager import KeyFindingsDBManager
try:
    db = KeyFindingsDBManager('/app/data/key_findings.db')
    print('Database connection successful')
except Exception as e:
    print(f'Database error: {e}')
"
```

#### Performance Monitoring in Dokploy:

```bash
# Check performance metrics
curl http://localhost:8050/health | jq '.performance_metrics'

# Monitor cache performance
curl http://localhost:8050/health | jq '.database_metrics.cache_hit_rate'

# Check AI service performance
curl http://localhost:8050/health | jq '.ai_performance'
```

## 🎯 Dokploy Success Indicators

Your Dokploy deployment is successful when:

- ✅ Container starts without errors
- ✅ Health check returns `{"status": "healthy"}`
- ✅ Database persists across container restarts
- ✅ Volume mounts are working (`/app/data` accessible)
- ✅ Key Findings button appears in sidebar
- ✅ Modal opens with AI-generated content
- ✅ Performance metrics are being collected

## 🚀 Quick Dokploy Deployment

```bash
# 1. Update .env for Dokploy
# (Copy the .env content from section 2 above)

# 2. Deploy
chmod +x deploy_key_findings_dokploy.sh
./deploy_key_findings_dokploy.sh

# 3. Access your app
# http://your-dokploy-domain.com
```

---

**🚀 Your Key Findings module is ready for Dokploy deployment!**

The Dokploy-specific configuration ensures proper volume mounting and persistence for your AI-powered analysis system.
