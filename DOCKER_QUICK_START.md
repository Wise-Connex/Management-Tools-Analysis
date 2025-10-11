# Docker Quick Start Guide

## Running the Management Tools Analysis Dashboard in Docker

### Option 1: Using the test script (recommended)

```bash
./test_docker_build.sh
```

This will build the image and run a complete test of the deployment.

### Option 2: Manual build and run

```bash
# Build the image
docker build -t management-tools-dashboard .

# Run the container
docker run -d \
  --name management-tools \
  -p 8050:8050 \
  -e PORT=8050 \
  -e FLASK_ENV=production \
  management-tools-dashboard

# View logs
docker logs -f management-tools

# Test health endpoint
curl http://localhost:8050/health

# Access the dashboard
open http://localhost:8050
```

### Option 3: Using the run script

```bash
# Build first
docker build -t management-tools-dashboard .

# Then run
./run_docker.sh
```

## Accessing the Application

- **Main Dashboard**: http://localhost:8050
- **Health Check**: http://localhost:8050/health

## Stopping the Application

```bash
docker stop management-tools
docker rm management-tools
```

## Troubleshooting

If the build fails, check:

1. Docker is running: `docker info`
2. You have enough disk space
3. All required files are present

View build errors:

```bash
docker build -t management-tools-dashboard . 2>&1 | tee build.log
```

## Production Deployment

For production deployment to Dokploy:

1. Push all changes to GitHub
2. Connect your repository in Dokploy
3. Use the Dockerfile as the build context
4. Set environment variables:
   - PORT=8050
   - FLASK_ENV=production
   - LOG_LEVEL=INFO
5. Configure health check: `/health` endpoint on port 8050
