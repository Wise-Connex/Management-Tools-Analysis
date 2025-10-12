# Key Findings Docker Deployment Commands

## 🚀 Quick Deployment Guide

### 1. Set Up Environment Variables

Since your API key is already in `.env`, you can skip the manual setup:

```bash
# The .env file will be automatically loaded by Docker
# No need to set environment variables manually
```

### 2. Create Required Directories

```bash
# Create data directories for persistence
mkdir -p ./data/key_findings
mkdir -p ./data/key_findings/backups
mkdir -p ./config/key_findings
mkdir -p /var/lib/key_findings_data

# Set proper permissions
chmod 755 ./data/key_findings
chmod 755 ./data/key_findings/backups
chmod 755 ./config/key_findings
chmod 755 /var/lib/key_findings_data
```

### 3. Update .env File

Create or update your `.env` file:

```bash
cat > .env << EOF
# Key Findings Configuration
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=/app/data/backups
KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data

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

### 4. Docker Deployment Commands

#### Option A: Using Docker Compose (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

#### Option B: Using Docker Run

```bash
# Build the image
docker build -t management-tools-dashboard .

# Run with volume mounts
docker run -d \
  --name management-tools-dashboard \
  -p 8050:8050 \
  -v ./data/key_findings:/app/data:rw \
  -v ./data/key_findings/backups:/app/data/backups:rw \
  -v /var/lib/key_findings_data:/var/lib/key_findings_data:rw \
  -e OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
  management-tools-dashboard

# View logs
docker logs -f management-tools-dashboard

# Stop the container
docker stop management-tools-dashboard
```

### 5. Verify Deployment

```bash
# Check if container is running
docker ps | grep management-tools-dashboard

# Check health status
curl http://localhost:8050/health

# View application logs
docker logs management-tools-dashboard

# Test Key Findings functionality
curl -X POST http://localhost:8050/health \
  -H "Content-Type: application/json" \
  -d '{"test": "key_findings"}'
```

### 6. Access the Application

Open your browser and navigate to:

```
http://localhost:8050
```

### 7. Test Key Findings Feature

1. **Select a Management Tool** from the dropdown
2. **Select Data Sources** (at least one)
3. **Click "🧠 Generar Key Findings"** button
4. **Verify modal opens** with AI-generated content
5. **Test caching** by closing and reopening the same analysis

## 🔧 Troubleshooting Commands

### Check Container Status

```bash
# List running containers
docker ps

# Check container logs for errors
docker logs management-tools-dashboard

# Inspect container configuration
docker inspect management-tools-dashboard
```

### Database Issues

```bash
# Check database file permissions
ls -la ./data/key_findings/

# Test database connectivity
docker exec management-tools-dashboard python -c "
from key_findings.database_manager import KeyFindingsDBManager
db = KeyFindingsDBManager('/app/data/key_findings.db')
print(f'Database working: {db.verify_persistence()}')
"
```

### API Key Issues

```bash
# Test API key validity
docker exec management-tools-dashboard python -c "
import asyncio
from key_findings.ai_service import OpenRouterService
async def test():
    service = OpenRouterService('your-api-key')
    result = await service.test_model_availability()
    print(f'Model availability: {result}')
asyncio.run(test())
"
```

### Performance Monitoring

```bash
# Check performance metrics
curl http://localhost:8050/health | jq '.performance_metrics'

# Monitor cache hit rates
docker exec management-tools-dashboard python -c "
from key_findings.key_findings_service import get_key_findings_service
service = get_key_findings_service()
metrics = service.get_performance_metrics()
print(f'Cache hit rate: {metrics[\"service_metrics\"][\"cache_hit_rate\"]}%')
"
```

## 🐳 Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace management-tools
```

### 2. Apply Configuration

```bash
# Apply all Kubernetes resources
kubectl apply -f k8s-key-findings.yaml

# Check pod status
kubectl get pods -n management-tools

# View logs
kubectl logs -f deployment/management-tools-dashboard -n management-tools
```

### 3. Port Forwarding

```bash
# Forward port to local machine
kubectl port-forward deployment/management-tools-dashboard 8050:8050 -n management-tools
```

## 📊 Monitoring Commands

### Health Checks

```bash
# Basic health check
curl http://localhost:8050/health

# Detailed health with metrics
curl http://localhost:8050/health | jq '.'

# Continuous monitoring
watch -n 5 'curl -s http://localhost:8050/health | jq ".overall_status"'
```

### Performance Metrics

```bash
# Get current metrics
curl http://localhost:8050/health | jq '.performance_metrics'

# Monitor cache performance
curl http://localhost:8050/health | jq '.database_metrics.cache_hit_rate'

# Check AI service performance
curl http://localhost:8050/health | jq '.ai_performance'
```

## 🔒 Security Commands

### API Key Security

```bash
# Never expose API key in logs
echo "OPENROUTER_API_KEY=***REDACTED***" >> .env

# Use Docker secrets (production)
kubectl create secret generic api-secrets --from-literal=OPENROUTER_API_KEY=your-key
```

### Database Security

```bash
# Set proper ownership
sudo chown -R 1000:1000 ./data/key_findings
sudo chown -R 1000:1000 /var/lib/key_findings_data

# Set appropriate permissions
chmod 600 ./data/key_findings/key_findings.db
```

## 🚀 Production Deployment

### 1. Environment Setup

```bash
# Production environment variables
export NODE_ENV=production
export KEY_FINDINGS_DEBUG=false
export KEY_FINDINGS_CACHE_TTL=86400
```

### 2. SSL/TLS Configuration

```bash
# Run with HTTPS
docker run -d \
  --name management-tools-dashboard \
  -p 443:8050 \
  -v ./ssl:/app/ssl:ro \
  -e SSL_CERT_PATH=/app/ssl/cert.pem \
  -e SSL_KEY_PATH=/app/ssl/key.pem \
  management-tools-dashboard
```

### 3. Load Balancer Setup

```bash
# Multiple instances for load balancing
docker-compose up --scale dashboard-app=3

# Configure nginx load balancer
# (nginx configuration would go here)
```

## 📝 Quick Start Script

Save this as `deploy_key_findings.sh` and make it executable:

```bash
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
mkdir -p /var/lib/key_findings_data

# Set permissions
echo "🔒 Setting permissions..."
chmod 755 ./data/key_findings
chmod 755 ./data/key_findings/backups
chmod 755 /var/lib/key_findings_data

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
```

Make it executable and run:

```bash
chmod +x deploy_key_findings.sh
./deploy_key_findings.sh
```

## 🎯 Success Indicators

Your deployment is successful when:

- ✅ Container starts without errors
- ✅ Health check returns `{"status": "healthy"}`
- ✅ Key Findings button appears in sidebar
- ✅ Modal opens with AI-generated content
- ✅ Database persists across container restarts
- ✅ Performance metrics are being collected

---

**🚀 Your Key Findings module is ready for production use!**
