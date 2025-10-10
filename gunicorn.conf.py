"""
Gunicorn Configuration for Dash Dashboard Production Deployment
Optimized for serving Dash applications with Plotly visualizations
"""

import multiprocessing
import os

# ============================================================================
# Server Socket Configuration
# ============================================================================

# Bind to all interfaces on the specified port
bind = f"0.0.0.0:{os.getenv('PORT', '8050')}"

# Maximum number of pending connections
backlog = 2048

# ============================================================================
# Worker Processes Configuration
# ============================================================================

# Number of worker processes
# Formula: (2 x CPU cores) + 1, but cap at 8 for container environments
# Can be overridden with MAX_WORKERS environment variable
cpu_count = multiprocessing.cpu_count()
default_workers = min(cpu_count * 2 + 1, 8)  # Cap at 8 workers
workers = int(os.getenv('MAX_WORKERS', default_workers))

# Worker class - use 'sync' for Dash (gevent can cause issues with callbacks)
# For CPU-intensive Dash apps, sync workers are more reliable
worker_class = os.getenv('WORKER_CLASS', 'sync')

# Maximum number of simultaneous clients (for gevent/eventlet workers)
worker_connections = 1000

# Workers silent for more than this many seconds are killed and restarted
timeout = int(os.getenv('WORKER_TIMEOUT', '120'))

# Keep-alive connections
keepalive = 5

# ============================================================================
# Worker Recycling (Prevent Memory Leaks)
# ============================================================================

# Restart workers after this many requests (with jitter to prevent thundering herd)
max_requests = 1000
max_requests_jitter = 100

# ============================================================================
# Logging Configuration
# ============================================================================

# Access log - write to stdout for Docker/Dokploy log aggregation
accesslog = '-'

# Error log - write to stderr
errorlog = '-'

# Log level
loglevel = os.getenv('LOG_LEVEL', 'info').lower()

# Access log format
# %(h)s - remote address
# %(l)s - '-'
# %(u)s - user name
# %(t)s - date of the request
# %(r)s - request line
# %(s)s - status
# %(b)s - response length
# %(f)s - referer
# %(a)s - user agent
# %(D)s - request time in microseconds
# %(L)s - request time in seconds
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ============================================================================
# Process Naming
# ============================================================================

proc_name = 'dash_dashboard'

# ============================================================================
# Server Mechanics
# ============================================================================

# Don't daemonize (required for Docker)
daemon = False

# PID file (None for Docker)
pidfile = None

# File mode creation mask
umask = 0

# User and group to run workers as (None = current user)
user = None
group = None

# Directory to use for temporary files
tmp_upload_dir = None

# ============================================================================
# SSL Configuration (Handled by Dokploy)
# ============================================================================

# SSL is terminated at Dokploy level, so these are None
keyfile = None
certfile = None

# ============================================================================
# Application Loading
# ============================================================================

# Preload application code before worker processes are forked
# This can save RAM and speed up server boot times
preload_app = True

# ============================================================================
# Server Hooks
# ============================================================================

def on_starting(server):
    """Called just before the master process is initialized"""
    server.log.info("Starting Dash Dashboard server")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP"""
    server.log.info("Reloading Dash Dashboard")

def when_ready(server):
    """Called just after the server is started"""
    server.log.info("Dash Dashboard is ready to serve requests")

def pre_fork(server, worker):
    """Called just before a worker is forked"""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked"""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    """Called just after a worker has initialized the application"""
    worker.log.info(f"Worker initialized (pid: {worker.pid})")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal"""
    worker.log.info(f"Worker received INT or QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal"""
    worker.log.info(f"Worker received ABORT signal (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked"""
    server.log.info("Forking new master process")

def pre_request(worker, req):
    """Called just before a worker processes the request"""
    worker.log.debug(f"{req.method} {req.path}")

def post_request(worker, req, environ, resp):
    """Called after a worker processes the request"""
    pass

def child_exit(server, worker):
    """Called just after a worker has been exited"""
    server.log.info(f"Worker exited (pid: {worker.pid})")

def worker_exit(server, worker):
    """Called just after a worker has been exited"""
    server.log.info(f"Worker shutdown (pid: {worker.pid})")

def nworkers_changed(server, new_value, old_value):
    """Called when the number of workers changes"""
    server.log.info(f"Number of workers changed from {old_value} to {new_value}")

def on_exit(server):
    """Called just before exiting Gunicorn"""
    server.log.info("Shutting down Dash Dashboard server")

# ============================================================================
# Graceful Shutdown
# ============================================================================

# Timeout for graceful workers restart
graceful_timeout = 30

# ============================================================================
# Security & Proxy Configuration
# ============================================================================

# Allow all IPs for forwarded headers (Dokploy handles proxy)
forwarded_allow_ips = '*'

# Trust X-Forwarded-* headers from proxy
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# ============================================================================
# Performance Tuning
# ============================================================================

# Use /dev/shm for worker heartbeat (faster than disk)
worker_tmp_dir = '/dev/shm'

# Limit request line size (prevent DOS)
limit_request_line = 4094

# Limit request header field size
limit_request_field_size = 8190

# Limit number of request header fields
limit_request_fields = 100

# ============================================================================
# Development vs Production Settings
# ============================================================================

if os.getenv('FLASK_ENV') == 'development':
    # Development settings
    reload = True
    reload_extra_files = [
        'dashboard_app/app.py',
        'dashboard_app/tools.py',
        'database.py'
    ]
    loglevel = 'debug'
else:
    # Production settings
    reload = False
    loglevel = 'info'