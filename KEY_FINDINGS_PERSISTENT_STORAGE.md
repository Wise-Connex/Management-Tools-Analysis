# Key Findings - Persistent Storage Configuration

## Overview

To ensure the Key Findings cache persists across Docker deployments in Dokploy, we need to implement persistent volume mounting. This prevents cache loss when containers are updated or restarted.

## Docker Configuration Updates

### 1. Docker Compose Configuration

#### Update `docker-compose.yml`:

```yaml
version: "3.8"

services:
  dashboard-app:
    build: .
    ports:
      - "8050:8050"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
    volumes:
      - key_findings_data:/app/data
      - ./dashboard_app:/app
    restart: unless-stopped

volumes:
  key_findings_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /var/lib/key_findings_data
```

### 2. Dockerfile Updates

#### Update `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Create data directory for persistent storage
RUN mkdir -p /app/data && \
    chmod 755 /app/data

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY dashboard_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY dashboard_app/ .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/health || exit 1

# Start the application
CMD ["python", "app.py"]
```

### 3. Environment Configuration

#### Update `.env` for persistent storage:

```env
# Persistent Database Configuration
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=/app/data/backups/
KEY_FINDINGS_BACKUP_INTERVAL=3600  # Backup every hour

# Docker-specific Configuration
KEY_FINDINGS_DATA_DIR=/app/data
KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data
```

## Database Manager Updates

### Enhanced Database Manager with Persistence

#### Update `key_findings/database_manager.py`:

```python
import sqlite3
import json
import hashlib
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
import threading

class KeyFindingsDBManager:
    """Database manager for Key Findings caching system with persistent storage"""

    def __init__(self, db_path: str = "key_findings.db", backup_dir: str = None):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir) if backup_dir else self.db_path.parent / "backups"
        self.logger = logging.getLogger(__name__)

        # Ensure directories exist
        self._ensure_directories()

        # Initialize database
        self._create_schema()

        # Start backup thread if configured
        self.backup_interval = int(os.getenv('KEY_FINDINGS_BACKUP_INTERVAL', '3600'))  # 1 hour
        if self.backup_interval > 0:
            self._start_backup_scheduler()

        self.logger.info(f"Key Findings database initialized at: {self.db_path}")
        self.logger.info(f"Backup directory: {self.backup_dir}")

    def _ensure_directories(self):
        """Ensure database and backup directories exist"""
        try:
            # Create database directory
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Set appropriate permissions
            os.chmod(self.db_path.parent, 0o755)
            os.chmod(self.backup_dir, 0o755)

        except Exception as e:
            self.logger.error(f"Error creating directories: {e}")
            raise

    def _create_schema(self):
        """Create database schema if not exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript("""
                    -- Enable WAL mode for better concurrent access
                    PRAGMA journal_mode=WAL;
                    PRAGMA synchronous=NORMAL;
                    PRAGMA cache_size=10000;
                    PRAGMA temp_store=memory;

                    -- Reports table for storing AI-generated findings
                    CREATE TABLE IF NOT EXISTS key_findings_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scenario_hash TEXT UNIQUE NOT NULL,
                        tool_name TEXT NOT NULL,
                        selected_sources TEXT NOT NULL,
                        date_range_start TEXT,
                        date_range_end TEXT,
                        language TEXT DEFAULT 'es',

                        -- AI Analysis Results
                        principal_findings TEXT NOT NULL,
                        pca_insights TEXT,
                        executive_summary TEXT NOT NULL,

                        -- Metadata
                        model_used TEXT NOT NULL,
                        api_latency_ms INTEGER,
                        confidence_score REAL,
                        generation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        cache_version TEXT DEFAULT '1.0',

                        -- User Interaction
                        user_rating INTEGER,
                        user_feedback TEXT,
                        access_count INTEGER DEFAULT 0,
                        last_accessed DATETIME,

                        -- Performance Metrics
                        data_points_analyzed INTEGER,
                        sources_count INTEGER,
                        analysis_depth TEXT DEFAULT 'comprehensive'
                    );

                    -- Analysis history for tracking changes over time
                    CREATE TABLE IF NOT EXISTS key_findings_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scenario_hash TEXT NOT NULL,
                        report_id INTEGER NOT NULL,
                        change_type TEXT NOT NULL,
                        previous_version_id INTEGER,
                        change_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        change_reason TEXT,
                        FOREIGN KEY (report_id) REFERENCES key_findings_reports(id)
                    );

                    -- Model performance tracking
                    CREATE TABLE IF NOT EXISTS model_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT NOT NULL,
                        request_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        response_time_ms INTEGER,
                        token_count INTEGER,
                        success BOOLEAN,
                        error_message TEXT,
                        user_satisfaction INTEGER
                    );

                    -- Cache statistics for optimization
                    CREATE TABLE IF NOT EXISTS cache_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        total_requests INTEGER DEFAULT 0,
                        cache_hits INTEGER DEFAULT 0,
                        cache_misses INTEGER DEFAULT 0,
                        avg_response_time_ms REAL,
                        unique_scenarios INTEGER DEFAULT 0
                    );

                    -- Create indexes for performance
                    CREATE INDEX IF NOT EXISTS idx_reports_scenario_hash ON key_findings_reports(scenario_hash);
                    CREATE INDEX IF NOT EXISTS idx_reports_tool_name ON key_findings_reports(tool_name);
                    CREATE INDEX IF NOT EXISTS idx_reports_timestamp ON key_findings_reports(generation_timestamp);
                    CREATE INDEX IF NOT EXISTS idx_history_scenario_hash ON key_findings_history(scenario_hash);
                    CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON model_performance(request_timestamp);
                """)

                self.logger.info("Database schema created/verified successfully")

        except Exception as e:
            self.logger.error(f"Error creating database schema: {e}")
            raise

    def _start_backup_scheduler(self):
        """Start background thread for periodic backups"""
        def backup_worker():
            while True:
                try:
                    self._create_backup()
                    threading.Event().wait(self.backup_interval)
                except Exception as e:
                    self.logger.error(f"Backup error: {e}")
                    threading.Event().wait(60)  # Wait 1 minute on error

        backup_thread = threading.Thread(target=backup_worker, daemon=True)
        backup_thread.start()
        self.logger.info(f"Backup scheduler started with {self.backup_interval}s interval")

    def _create_backup(self):
        """Create a backup of the database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"key_findings_backup_{timestamp}.db"

            # Create backup using SQLite backup API
            source = sqlite3.connect(str(self.db_path))
            backup = sqlite3.connect(str(backup_file))
            source.backup(backup)
            backup.close()
            source.close()

            # Compress old backups (keep only last 10)
            self._cleanup_old_backups()

            self.logger.info(f"Database backup created: {backup_file}")

        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")

    def _cleanup_old_backups(self):
        """Clean up old backup files, keeping only the most recent 10"""
        try:
            backup_files = list(self.backup_dir.glob("key_findings_backup_*.db"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Remove old backups (keep last 10)
            for old_backup in backup_files[10:]:
                old_backup.unlink()
                self.logger.debug(f"Removed old backup: {old_backup}")

        except Exception as e:
            self.logger.error(f"Error cleaning up backups: {e}")

    def restore_from_backup(self, backup_timestamp: str = None):
        """Restore database from backup"""
        try:
            if backup_timestamp:
                backup_file = self.backup_dir / f"key_findings_backup_{backup_timestamp}.db"
            else:
                # Use the most recent backup
                backup_files = list(self.backup_dir.glob("key_findings_backup_*.db"))
                if not backup_files:
                    raise FileNotFoundError("No backup files found")
                backup_file = max(backup_files, key=lambda x: x.stat().st_mtime)

            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")

            # Close current connections and restore
            temp_path = self.db_path.with_suffix('.tmp')
            shutil.copy2(backup_file, temp_path)
            shutil.move(temp_path, self.db_path)

            self.logger.info(f"Database restored from backup: {backup_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error restoring from backup: {e}")
            return False

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT
                        COUNT(*) as total_reports,
                        COUNT(DISTINCT tool_name) as unique_tools,
                        COUNT(DISTINCT scenario_hash) as unique_scenarios,
                        MAX(generation_timestamp) as last_report,
                        SUM(access_count) as total_accesses
                    FROM key_findings_reports
                """)
                stats = cursor.fetchone()

                # Get database file size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

                # Get backup count
                backup_count = len(list(self.backup_dir.glob("key_findings_backup_*.db")))

                return {
                    'database_path': str(self.db_path),
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'total_reports': stats[0],
                    'unique_tools': stats[1],
                    'unique_scenarios': stats[2],
                    'last_report': stats[3],
                    'total_accesses': stats[4],
                    'backup_count': backup_count,
                    'backup_directory': str(self.backup_dir),
                    'persistent_storage': True
                }

        except Exception as e:
            self.logger.error(f"Error getting database info: {e}")
            return {'error': str(e)}

    def verify_persistence(self) -> bool:
        """Verify that persistent storage is working correctly"""
        try:
            # Check if database file exists and is writable
            if not self.db_path.exists():
                return False

            # Test write operation
            test_data = {"test": "persistence_check", "timestamp": datetime.now().isoformat()}
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS persistence_test (data TEXT)")
                conn.execute("INSERT INTO persistence_test (data) VALUES (?)", (json.dumps(test_data),))
                conn.commit()

                # Verify data was written
                cursor = conn.execute("SELECT data FROM persistence_test ORDER BY rowid DESC LIMIT 1")
                result = cursor.fetchone()

                if result:
                    stored_data = json.loads(result[0])
                    if stored_data.get('test') == 'persistence_check':
                        # Clean up test data
                        conn.execute("DELETE FROM persistence_test")
                        conn.commit()
                        return True

            return False

        except Exception as e:
            self.logger.error(f"Persistence verification failed: {e}")
            return False

    # ... (rest of the existing methods remain the same)
```

## Dokploy Configuration

### 1. Volume Mounting in Dokploy

When deploying to Dokploy, ensure you configure persistent volumes:

```yaml
# dokploy-compose.yml
services:
  dashboard-app:
    image: your-registry/management-tools-dashboard:latest
    volumes:
      - /var/lib/key_findings_data:/app/data
    environment:
      - KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
      - KEY_FINDINGS_BACKUP_PATH=/app/data/backups/
```

### 2. Pre-deployment Setup

#### Create persistent directory on server:

```bash
# SSH into your Dokploy server
ssh your-server

# Create persistent directory
sudo mkdir -p /var/lib/key_findings_data
sudo chmod 755 /var/lib/key_findings_data
sudo chown 1000:1000 /var/lib/key_findings_data  # Match container user

# Verify directory exists and has correct permissions
ls -la /var/lib/key_findings_data
```

### 3. Health Check for Persistence

#### Add to `dashboard_app/app.py`:

```python
@app.server.route('/health/persistence')
def persistence_health_check():
    """Health check for persistent storage"""
    try:
        from key_findings.database_manager import KeyFindingsDBManager

        db_manager = KeyFindingsDBManager()
        persistence_ok = db_manager.verify_persistence()
        db_info = db_manager.get_database_info()

        health_status = {
            'status': 'healthy' if persistence_ok else 'unhealthy',
            'persistence_verified': persistence_ok
```
