# Troubleshooting: Container Running But Page Not Loading

## Quick Diagnosis Commands

Run these commands to diagnose the issue:

```bash
# 1. Check if container is actually running
docker ps | grep dash

# 2. Check container logs
docker logs dash-test

# 3. Check if app is listening on port
docker exec dash-test netstat -tlnp 2>/dev/null || docker exec dash-test ss -tlnp

# 4. Test health endpoint from inside container
docker exec dash-test curl http://localhost:8050/health

# 5. Test from host
curl http://localhost:8050/health

# 6. Check port mapping
docker port dash-test
```

---

## Common Causes & Solutions

### Cause 1: Application Not Started Yet

**Symptom:** Container running but app still starting

**Check:**

```bash
docker logs dash-test | tail -20
```

**Look for:**

```
[INFO] Starting Dash Dashboard server
[INFO] Listening at: http://0.0.0.0:8050
[INFO] Booting worker with pid: 123
```

**Solution:** Wait 20-30 seconds for app to fully start

---

### Cause 2: Application Crashed After Start

**Symptom:** Container running but no gunicorn process

**Check:**

```bash
docker exec dash-test ps aux
```

**Look for:** gunicorn processes should be running

**If not running:**

```bash
# Check logs for Python errors
docker logs dash-test | grep -i error
docker logs dash-test | grep -i traceback
```

**Common errors:**

- Import errors (missing dependencies)
- Database file not found
- Permission errors

---

### Cause 3: Wrong Port or Port Not Mapped

**Check port mapping:**

```bash
docker port dash-test
# Should show: 8050/tcp -> 0.0.0.0:8050
```

**If empty or wrong:**

```bash
# Stop and remove container
docker stop dash-test
docker rm dash-test

# Run with explicit port mapping
docker run -d --name dash-test -p 8050:8050 dash-dashboard
```

---

### Cause 4: Firewall Blocking Port

**Check if port is accessible:**

```bash
# Test with curl
curl -v http://localhost:8050

# Test with telnet
telnet localhost 8050
```

**If connection refused:**

- Check macOS firewall settings
- Check if another app is using port 8050

---

### Cause 5: Dash Server Not Binding Correctly

**Check if server is listening:**

```bash
# From inside container
docker exec dash-test curl http://localhost:8050/health

# If this works but http://localhost:8050 from host doesn't:
# The issue is port mapping or firewall
```

---

## Step-by-Step Debugging

### Step 1: Get Container Status

```bash
docker ps -a | grep dash-test
```

**Expected:**

```
abc123  dash-dashboard  Up 2 minutes (healthy)  0.0.0.0:8050->8050/tcp
```

**If "Exited":** Container crashed, check logs
**If "Up" but not "(healthy)":** Health check failing

### Step 2: Check Logs

```bash
docker logs dash-test
```

**What to look for:**

✅ **Good signs:**

```
[SUCCESS] Pre-flight checks completed
[INFO] Starting Dash Dashboard with command: gunicorn...
[INFO] Listening at: http://0.0.0.0:8050
[INFO] Booting worker with pid: 123
Dash is running on http://0.0.0.0:8050/
```

❌ **Bad signs:**

```
ERROR: ...
Traceback (most recent call last):
ModuleNotFoundError: No module named '...'
FileNotFoundError: [Errno 2] No such file or directory: '...'
```

### Step 3: Test Health Endpoint

```bash
# From host
curl http://localhost:8050/health

# From inside container
docker exec dash-test curl http://localhost:8050/health
```

**If works inside but not outside:**

- Port mapping issue
- Firewall issue

**If doesn't work inside:**

- App not running
- App crashed
- Wrong port

### Step 4: Check Processes

```bash
docker exec dash-test ps aux
```

**Should see:**

```
USER  PID  COMMAND
dashuser  1  /bin/bash ./entrypoint.sh gunicorn...
dashuser  7  gunicorn: master [dashboard_app.app:server]
dashuser  8  gunicorn: worker [dashboard_app.app:server]
dashuser  9  gunicorn: worker [dashboard_app.app:server]
...
```

**If no gunicorn processes:**

- App failed to start
- Check logs for errors

### Step 5: Interactive Debugging

```bash
# Get a shell in the container
docker exec -it dash-test /bin/bash

# Once inside:
cd /app
ls -la dashboard_app/
python dashboard_app/app.py
# See if app starts manually
```

---

## Most Likely Issues

### Issue A: Import Error (Missing fix_source_mapping.py)

**Error in logs:**

```
ModuleNotFoundError: No module named 'fix_source_mapping'
```

**Solution:**
The Dockerfile needs to copy `dashboard_app/fix_source_mapping.py`. Let me check if it's being copied.

**Quick fix:**

```bash
# Check if file exists in container
docker exec dash-test ls -la /app/dashboard_app/fix_source_mapping.py

# If not found, the file needs to be in dashboard_app/ directory
```

### Issue B: Database Files Not Found

**Error in logs:**

```
FileNotFoundError: [Errno 2] No such file or directory: 'dashboard_app/data.db'
```

**Solution:**

```bash
# Check if databases exist in container
docker exec dash-test ls -la /app/dashboard_app/*.db

# If not found, databases weren't copied
```

### Issue C: Port Binding Issue

**Error in logs:**

```
[ERROR] [Errno 98] Address already in use
```

**Solution:**

```bash
# Use different port
docker stop dash-test
docker rm dash-test
docker run -d --name dash-test -p 8051:8050 dash-dashboard

# Then access at http://localhost:8051
```

---

## Diagnostic Script

Save this as `diagnose.sh`:

```bash
#!/bin/bash

echo "=== Container Status ==="
docker ps -a | grep dash-test

echo ""
echo "=== Port Mapping ==="
docker port dash-test

echo ""
echo "=== Last 30 Log Lines ==="
docker logs --tail=30 dash-test

echo ""
echo "=== Running Processes ==="
docker exec dash-test ps aux 2>/dev/null || echo "Container not running"

echo ""
echo "=== Health Check (Internal) ==="
docker exec dash-test curl -s http://localhost:8050/health 2>/dev/null || echo "Health check failed"

echo ""
echo "=== Health Check (External) ==="
curl -s http://localhost:8050/health || echo "Cannot reach from host"

echo ""
echo "=== Files Check ==="
docker exec dash-test ls -la /app/dashboard_app/ 2>/dev/null | head -20

echo ""
echo "=== Network Test ==="
curl -v http://localhost:8050/ 2>&1 | head -20
```

Run it:

```bash
chmod +x diagnose.sh
./diagnose.sh
```

---

## Quick Fixes

### Fix 1: Restart Container

```bash
docker restart dash-test
sleep 20
curl http://localhost:8050/health
```

### Fix 2: Check Logs for Specific Error

```bash
docker logs dash-test 2>&1 | grep -A 5 -i "error\|traceback\|exception"
```

### Fix 3: Run Interactively to See Errors

```bash
# Stop current container
docker stop dash-test
docker rm dash-test

# Run interactively (see all output)
docker run -it --rm -p 8050:8050 dash-dashboard

# Watch for errors in real-time
# Press Ctrl+C to stop
```

---

## What to Share for Help

If still not working, share this information:

```bash
# 1. Container status
docker ps -a | grep dash-test

# 2. Full logs
docker logs dash-test > container-logs.txt

# 3. Port check
docker port dash-test

# 4. Process list
docker exec dash-test ps aux

# 5. Health check
docker exec dash-test curl http://localhost:8050/health
curl http://localhost:8050/health
```

---

**Next Step:** Run the diagnostic commands above and share the output
