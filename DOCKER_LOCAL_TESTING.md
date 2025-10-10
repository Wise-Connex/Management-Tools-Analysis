# Docker Local Testing Guide - Step by Step

**Purpose:** Detailed instructions for testing the Docker build locally before deploying to Dokploy

---

## Prerequisites Check

Before starting, verify you have:

```bash
# 1. Check Docker is installed and running
docker --version
# Expected: Docker version 20.10.0 or higher

# 2. Check Docker daemon is running
docker ps
# Should show running containers or empty list (not an error)

# 3. Check you're in the correct directory
pwd
# Should show: /Users/Dimar/Documents/python-code/MTSA/Management-Tools-Analysis

# 4. Verify required files exist
ls -la Dockerfile gunicorn.conf.py healthcheck.sh entrypoint.sh
# All files should be listed
```

---

## Step-by-Step Local Testing

### Step 1: Build the Docker Image

```bash
# Navigate to project root (where Dockerfile is located)
cd /Users/Dimar/Documents/python-code/MTSA/Management-Tools-Analysis

# Build the image (this will take 3-5 minutes first time)
docker build -t dash-dashboard:latest .

# What happens during build:
# Stage 1 (Builder):
#   - Downloads Python 3.11-slim image
#   - Installs build tools (gcc, g++, gfortran)
#   - Builds wheels from requirements.txt
#   - This stage is ~1.5GB but discarded
#
# Stage 2 (Runtime):
#   - Downloads Python 3.11-slim image again
#   - Installs only runtime dependencies
#   - Copies wheels from Stage 1
#   - Installs dependencies from wheels
#   - Copies application code
#   - Final image: ~800MB

# Expected output (last lines):
# Successfully built abc123def456
# Successfully tagged dash-dashboard:latest

# Verify image was created
docker images | grep dash-dashboard
# Should show: dash-dashboard   latest   abc123   2 minutes ago   800MB
```

### Step 2: Run the Container

```bash
# Run container in detached mode (-d)
docker run -d \
  --name dash-dashboard \
  -p 8050:8050 \
  -e FLASK_ENV=production \
  -e LOG_LEVEL=INFO \
  -e PORT=8050 \
  dash-dashboard:latest

# What this command does:
# -d                    = Run in background (detached)
# --name dash-dashboard = Name the container
# -p 8050:8050         = Map port 8050 (host:container)
# -e FLASK_ENV=...     = Set environment variables
# dash-dashboard:latest = Image to run

# Expected output:
# abc123def456789... (container ID)

# Verify container is running
docker ps
# Should show dash-dashboard with status "Up X seconds"
```

### Step 3: Check Container Logs

```bash
# View container logs (real-time)
docker logs -f dash-dashboard

# Expected output:
# [INFO] Starting Dash Dashboard initialization...
# [INFO] Python version: Python 3.11.x
# [INFO] Running as user: dashuser
# [SUCCESS] Created logs directory
# [SUCCESS] Found data.db (Size: XXX)
# [SUCCESS] Found notes_and_doi.db (Size: XXX)
# [INFO] Environment configuration:
# [INFO]   PORT: 8050
# [INFO]   FLASK_ENV: production
# [SUCCESS] Pre-flight checks completed successfully
# [INFO] Starting Dash Dashboard with command: gunicorn -c gunicorn.conf.py dashboard_app.app:server
# [2025-01-09 16:00:00] [INFO] Starting Dash Dashboard server
# [2025-01-09 16:00:00] [INFO] Listening at: http://0.0.0.0:8050
# [2025-01-09 16:00:00] [INFO] Using worker: sync
# [2025-01-09 16:00:00] [INFO] Booting worker with pid: 123

# Press Ctrl+C to stop following logs
```

### Step 4: Test Health Endpoint

```bash
# Test health check from host machine
curl http://localhost:8050/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-01-09T16:00:00Z",
#   "version": "1.0.0",
#   "service": "management-tools-dashboard",
#   "database": "connected",
#   "cache_size": 0,
#   "environment": "production"
# }

# Pretty print with jq (if installed)
curl http://localhost:8050/health | jq

# Test from inside container
docker exec dash-dashboard curl http://localhost:8050/health

# Test health check script
docker exec dash-dashboard ./healthcheck.sh
# Expected: ✓ Health check passed
```

### Step 5: Access Dashboard

```bash
# Open in browser
open http://localhost:8050

# Or manually navigate to:
# http://localhost:8050

# Verify:
# ✅ Dashboard loads
# ✅ Can select "Herramienta Gerencial"
# ✅ Can select data sources
# ✅ Graphs render correctly
# ✅ No console errors (check browser DevTools)
```

### Step 6: Monitor Container

```bash
# Check container status
docker ps

# Check resource usage
docker stats dash-dashboard
# Shows: CPU%, MEM USAGE, NET I/O, BLOCK I/O

# Check container details
docker inspect dash-dashboard

# Check container health
docker inspect --format='{{.State.Health.Status}}' dash-dashboard
# Expected: healthy
```

### Step 7: Cleanup

```bash
# Stop container
docker stop dash-dashboard

# Remove container
docker rm dash-dashboard

# Optional: Remove image
docker rmi dash-dashboard:latest

# Optional: Clean up all unused Docker resources
docker system prune -a
```

---

## Common Issues & Solutions

### Issue 1: "Cannot connect to Docker daemon"

**Symptom:**

```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solution:**

```bash
# Start Docker Desktop (macOS)
open -a Docker

# Wait for Docker to start (check menu bar icon)

# Verify Docker is running
docker ps
```

### Issue 2: "Port 8050 already in use"

**Symptom:**

```
Error starting userland proxy: listen tcp4 0.0.0.0:8050: bind: address already in use
```

**Solution:**

```bash
# Find what's using port 8050
lsof -i :8050

# Option A: Stop the conflicting process
kill -9 <PID>

# Option B: Use a different port
docker run -d --name dash-dashboard -p 8051:8050 dash-dashboard:latest
# Then access at http://localhost:8051
```

### Issue 3: "Build failed - requirements.txt not found"

**Symptom:**

```
COPY failed: file not found in build context
```

**Solution:**

```bash
# Verify you're in the correct directory
pwd
# Should be: /Users/Dimar/Documents/python-code/MTSA/Management-Tools-Analysis

# Check if requirements.txt exists
ls -la dashboard_app/requirements.txt

# Check .dockerignore isn't excluding it
cat .dockerignore | grep requirements.txt
# Should NOT show requirements.txt
```

### Issue 4: "Container starts then immediately stops"

**Symptom:**

```bash
docker ps
# Container not listed

docker ps -a
# Shows: Exited (1) 2 seconds ago
```

**Solution:**

```bash
# Check container logs for errors
docker logs dash-dashboard

# Common causes:
# 1. Missing database files
# 2. Permission errors
# 3. Python import errors
# 4. Port binding issues

# Debug by running interactively
docker run -it --rm dash-dashboard:latest /bin/bash
# Then manually run commands to find issue
```

### Issue 5: "Health check failing"

**Symptom:**

```bash
docker inspect --format='{{.State.Health.Status}}' dash-dashboard
# Shows: unhealthy
```

**Solution:**

```bash
# Check health check logs
docker inspect dash-dashboard | grep -A 10 Health

# Test health endpoint manually
docker exec dash-dashboard curl http://localhost:8050/health

# Check if app is actually running
docker exec dash-dashboard ps aux

# Check if databases exist
docker exec dash-dashboard ls -la /app/dashboard_app/
```

### Issue 6: "Permission denied" errors

**Symptom:**

```
PermissionError: [Errno 13] Permission denied: '/app/logs'
```

**Solution:**

```bash
# This shouldn't happen with our Dockerfile, but if it does:

# Check file ownership in container
docker exec dash-dashboard ls -la /app/

# Verify dashuser owns files
docker exec dash-dashboard whoami
# Should show: dashuser

# If needed, rebuild with --no-cache
docker build --no-cache -t dash-dashboard .
```

---

## Detailed Build Process

### What Happens During `docker build`

```bash
# Command
docker build -t dash-dashboard .

# Process:
Step 1/20 : FROM python:3.11-slim as builder
 ---> Pulling python:3.11-slim
 ---> Downloaded (takes 1-2 min first time)

Step 2/20 : WORKDIR /build
 ---> Creating /build directory

Step 3/20 : RUN apt-get update && apt-get install...
 ---> Installing build tools (gcc, g++, gfortran)
 ---> Takes 1-2 minutes

Step 4/20 : COPY dashboard_app/requirements.txt .
 ---> Copying requirements file

Step 5/20 : RUN pip wheel...
 ---> Building wheels for all dependencies
 ---> Takes 2-3 minutes (numpy, scipy, pandas, etc.)
 ---> Creates /wheels directory

Step 6/20 : FROM python:3.11-slim
 ---> Starting fresh with clean image

Step 7/20 : RUN apt-get update && apt-get install...
 ---> Installing runtime dependencies only
 ---> Much faster (30 seconds)

Step 8/20 : RUN useradd -m -u 1000 dashuser
 ---> Creating non-root user

Step 9/20 : WORKDIR /app
 ---> Setting working directory

Step 10/20 : COPY --from=builder /wheels /wheels
 ---> Copying pre-built wheels from Stage 1

Step 11/20 : RUN pip install...
 ---> Installing from wheels (fast - 30 seconds)

Step 12/20 : RUN pip install gunicorn gevent
 ---> Installing production server

Step 13-17 : COPY application files
 ---> Copying dashboard_app/, assets/, etc.

Step 18/20 : RUN chmod +x healthcheck.sh entrypoint.sh
 ---> Making scripts executable

Step 19/20 : RUN mkdir -p /app/logs...
 ---> Creating logs directory

Step 20/20 : USER dashuser
 ---> Switching to non-root user

Successfully built abc123def456
Successfully tagged dash-dashboard:latest
```

---

## Detailed Run Process

### What Happens During `docker run`

```bash
# Command
docker run -d --name dash-dashboard -p 8050:8050 dash-dashboard:latest

# Process:
1. Docker creates container from image
2. Runs entrypoint.sh:
   - Checks Python version
   - Verifies user (dashuser)
   - Creates logs directory
   - Checks database files exist
   - Displays environment config
   - Verifies application files

3. Executes CMD (gunicorn):
   - Loads gunicorn.conf.py
   - Calculates worker count (CPU * 2 + 1)
   - Starts master process
   - Forks worker processes
   - Loads Dash application
   - Binds to 0.0.0.0:8050
   - Starts accepting requests

4. Health check begins:
   - Waits 40 seconds (start_period)
   - Runs healthcheck.sh every 30 seconds
   - Checks /health endpoint
   - Marks container as healthy

# Timeline:
# 0s   - Container created
# 0-5s - entrypoint.sh runs
# 5-10s - Gunicorn starts
# 10-15s - Workers spawn
# 15-20s - Dash app loads
# 40s - First health check
# 40s+ - Container marked healthy
```

---

## Debugging Failed Builds

### Enable Verbose Output

```bash
# Build with progress output
docker build --progress=plain -t dash-dashboard .

# Build without cache (if something is cached incorrectly)
docker build --no-cache -t dash-dashboard .

# Build and show all output
docker build --progress=plain --no-cache -t dash-dashboard . 2>&1 | tee build.log
```

### Check Build Context

```bash
# See what files Docker is using
docker build --progress=plain -t dash-dashboard . 2>&1 | grep "COPY"

# Verify .dockerignore is working
# Create a test to see what's included
docker build --progress=plain -t dash-dashboard . 2>&1 | grep "Sending build context"
# Should show: Sending build context to Docker daemon  XXX MB
# If > 100MB, .dockerignore might not be working
```

### Inspect Failed Build

```bash
# If build fails at a specific step, you can inspect that layer
# Find the last successful layer ID from build output
docker run -it <layer-id> /bin/bash

# Then manually run the failed command to see detailed error
```

---

## Debugging Failed Container Startup

### Check Why Container Stopped

```bash
# List all containers (including stopped)
docker ps -a

# Check exit code
docker inspect dash-dashboard --format='{{.State.ExitCode}}'
# 0 = normal exit
# 1 = application error
# 137 = killed (out of memory)
# 139 = segmentation fault

# View full container logs
docker logs dash-dashboard

# View last 50 lines
docker logs --tail=50 dash-dashboard

# Follow logs in real-time
docker logs -f dash-dashboard
```

### Run Container Interactively

```bash
# Instead of -d (detached), run interactively to see errors
docker run -it --rm \
  --name dash-dashboard-debug \
  -p 8050:8050 \
  dash-dashboard:latest

# This will show all output in your terminal
# Press Ctrl+C to stop

# Or run with bash to debug manually
docker run -it --rm \
  --name dash-dashboard-debug \
  -p 8050:8050 \
  dash-dashboard:latest \
  /bin/bash

# Then manually run commands:
cd /app
ls -la
python dashboard_app/app.py
```

### Check File Permissions

```bash
# Start container
docker run -d --name dash-dashboard -p 8050:8050 dash-dashboard:latest

# Check file ownership
docker exec dash-dashboard ls -la /app/

# Should show:
# drwxr-xr-x  dashuser dashuser  dashboard_app/
# drwxr-xr-x  dashuser dashuser  assets/
# -rwxr-xr-x  dashuser dashuser  healthcheck.sh
# -rwxr-xr-x  dashuser dashuser  entrypoint.sh

# Check current user
docker exec dash-dashboard whoami
# Should show: dashuser

# Check if databases are accessible
docker exec dash-dashboard ls -la /app/dashboard_app/*.db
```

---

## Complete Testing Workflow

### Full Test Script

Create a file `test_docker.sh`:

```bash
#!/bin/bash
# test_docker.sh - Complete Docker testing script

set -e  # Exit on error

echo "🔍 Step 1: Checking prerequisites..."
docker --version || { echo "❌ Docker not installed"; exit 1; }
docker ps > /dev/null || { echo "❌ Docker daemon not running"; exit 1; }
echo "✅ Docker is ready"

echo ""
echo "🏗️  Step 2: Building Docker image..."
docker build -t dash-dashboard:test . || { echo "❌ Build failed"; exit 1; }
echo "✅ Build successful"

echo ""
echo "🚀 Step 3: Starting container..."
docker run -d \
  --name dash-test \
  -p 8050:8050 \
  -e FLASK_ENV=production \
  -e LOG_LEVEL=INFO \
  dash-dashboard:test || { echo "❌ Container start failed"; exit 1; }
echo "✅ Container started"

echo ""
echo "⏳ Step 4: Waiting for application to start (20 seconds)..."
sleep 20

echo ""
echo "🏥 Step 5: Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8050/health)
echo "$HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    echo "📋 Container logs:"
    docker logs dash-test
    exit 1
fi

echo ""
echo "📊 Step 6: Checking container status..."
docker ps | grep dash-test
docker stats --no-stream dash-test

echo ""
echo "✅ All tests passed!"
echo ""
echo "🌐 Dashboard is running at: http://localhost:8050"
echo "🏥 Health endpoint: http://localhost:8050/health"
echo ""
echo "To view logs: docker logs -f dash-test"
echo "To stop: docker stop dash-test && docker rm dash-test"
```

Make it executable and run:

```bash
chmod +x test_docker.sh
./test_docker.sh
```

---

## Manual Testing Checklist

### Build Phase

- [ ] Docker daemon is running
- [ ] In correct directory (project root)
- [ ] Dockerfile exists
- [ ] requirements.txt exists in dashboard_app/
- [ ] Build completes without errors
- [ ] Image size is ~800MB (not 2GB+)

### Run Phase

- [ ] Container starts successfully
- [ ] Container stays running (not exiting)
- [ ] Logs show "Listening at: http://0.0.0.0:8050"
- [ ] No error messages in logs
- [ ] Health check passes after 40 seconds

### Application Phase

- [ ] Health endpoint responds with JSON
- [ ] Dashboard loads in browser
- [ ] Can select management tool
- [ ] Can select data sources
- [ ] Graphs render correctly
- [ ] No JavaScript errors in console
- [ ] Assets load (images, fonts)

---

## Expected vs Actual

### Expected Behavior

```bash
# Build
$ docker build -t dash-dashboard .
[+] Building 180.5s (20/20) FINISHED
Successfully tagged dash-dashboard:latest

# Run
$ docker run -d --name dash-dashboard -p 8050:8050 dash-dashboard:latest
abc123def456789...

# Status
$ docker ps
CONTAINER ID   IMAGE              STATUS                    PORTS
abc123def456   dash-dashboard     Up 30 seconds (healthy)   0.0.0.0:8050->8050/tcp

# Health
$ curl http://localhost:8050/health
{"status":"healthy","timestamp":"2025-01-09T16:00:00Z",...}

# Dashboard
$ open http://localhost:8050
# Dashboard loads successfully
```

### If Something Goes Wrong

```bash
# Build fails
$ docker build -t dash-dashboard .
ERROR: failed to solve: ...

# Solution: Check error message, verify files exist

# Container exits immediately
$ docker ps
# (empty)

$ docker ps -a
CONTAINER ID   STATUS
abc123         Exited (1) 2 seconds ago

# Solution: Check logs
$ docker logs dash-dashboard
# Read error message and fix issue

# Health check fails
$ docker inspect dash-dashboard | grep Health
"Status": "unhealthy"

# Solution: Check if app is running
$ docker exec dash-dashboard ps aux
# Should show gunicorn processes
```

---

## Alternative: Using Docker Compose

If `docker run` is confusing, use Docker Compose:

```bash
# Step 1: Start services
docker-compose up -d

# What this does:
# - Builds image if not exists
# - Creates network
# - Starts container
# - Configures health checks
# - Maps ports

# Step 2: Check status
docker-compose ps
# Should show: dash   Up (healthy)

# Step 3: View logs
docker-compose logs -f dash

# Step 4: Test health
curl http://localhost:8050/health

# Step 5: Access dashboard
open http://localhost:8050

# Step 6: Stop
docker-compose down
```

---

## Verification Commands

### Quick Verification

```bash
# One-liner to test everything
docker build -t dash-dashboard . && \
docker run -d --name dash-test -p 8050:8050 dash-dashboard && \
sleep 20 && \
curl http://localhost:8050/health && \
echo "✅ Success! Dashboard at http://localhost:8050" && \
docker stop dash-test && docker rm dash-test
```

### Detailed Verification

```bash
# 1. Image exists
docker images | grep dash-dashboard

# 2. Container running
docker ps | grep dash-dashboard

# 3. Health check passing
docker inspect --format='{{.State.Health.Status}}' dash-dashboard

# 4. App responding
curl -I http://localhost:8050

# 5. Health endpoint working
curl http://localhost:8050/health | jq

# 6. Logs clean
docker logs dash-dashboard | grep ERROR
# Should be empty or minimal

# 7. Resources normal
docker stats --no-stream dash-dashboard
# CPU < 50%, Memory < 1GB
```

---

## Next Steps After Successful Local Test

1. **Commit Changes**

   ```bash
   git add .
   git commit -m "Add production deployment configuration"
   git push origin main
   ```

2. **Deploy to Dokploy**

   - Follow [`DEPLOYMENT.md`](DEPLOYMENT.md)
   - Use same configuration as local test
   - Monitor deployment in Dokploy UI

3. **Verify Production**
   ```bash
   curl https://your-domain.com/health
   open https://your-domain.com
   ```

---

## Getting Help

If you're still having issues:

1. **Check logs carefully**

   ```bash
   docker logs dash-dashboard 2>&1 | tee docker-logs.txt
   ```

2. **Verify all files**

   ```bash
   ls -la Dockerfile gunicorn.conf.py healthcheck.sh entrypoint.sh .dockerignore
   ```

3. **Test Python dependencies**

   ```bash
   cd dashboard_app
   pip install -r requirements.txt
   python app.py
   ```

4. **Share error output**
   - Copy full error message
   - Include `docker logs` output
   - Include `docker inspect` output

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-01-09  
**Status:** ✅ Ready for Testing
