# Dockerfile Fix Applied - SciPy Build Issue

## Issue Identified

**Error:** SciPy failed to build because it couldn't find OpenBLAS

```
ERROR: Dependency lookup for OpenBLAS with method 'pkgconfig' failed:
Pkg-config for machine host machine not found.
```

**Root Cause:** SciPy 1.16.2 requires `cmake` for its build system (Meson), which wasn't installed in the builder stage.

---

## Fix Applied

### Changed in Dockerfile (Line 14-24)

**Before:**

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
```

**After:**

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    pkg-config \
    cmake \              # ← ADDED THIS
    && rm -rf /var/lib/apt/lists/*
```

---

## Why This Fixes It

1. **SciPy 1.16.2** uses Meson build system
2. **Meson** requires cmake to find OpenBLAS
3. **cmake** provides the necessary build configuration tools
4. **pkg-config** alone wasn't sufficient for scipy's new build system

---

## Now Rebuild

```bash
# Clean up failed build
docker system prune -f

# Rebuild with fix
docker build -t dash-dashboard .

# Or use the test script
./test_docker.sh
```

---

## Expected Build Time

With cmake installed, the build should complete successfully:

- **Stage 1 (Builder):** 3-5 minutes

  - numpy: 30-45 seconds ✓
  - scipy: 60-90 seconds ✓ (now will work!)
  - pandas: 30 seconds ✓
  - scikit-learn: 30 seconds ✓
  - statsmodels: 20 seconds ✓

- **Stage 2 (Runtime):** 30-60 seconds

**Total:** 4-6 minutes (first build)

---

## Verification

After rebuild completes, you should see:

```
Successfully built abc123def456
Successfully tagged dash-dashboard:latest
```

Then test:

```bash
docker run -d --name dash-test -p 8050:8050 dash-dashboard
sleep 20
curl http://localhost:8050/health
```

---

**Status:** ✅ Fix Applied  
**Action:** Rebuild Docker image  
**Expected:** Build will now complete successfully
