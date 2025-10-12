"""
Docker persistence configuration for Key Findings module
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class DockerPersistenceConfig:
    """
    Docker-specific persistence configuration for Key Findings module.
    
    Ensures data persistence across container restarts and deployments.
    """
    
    def __init__(self):
        """Initialize Docker persistence configuration"""
        self.logger = logging.getLogger(__name__)
        
        # Docker-specific paths
        self.docker_paths = {
            'data_dir': '/app/data',
            'backup_dir': '/app/data/backups',
            'volume_mount': '/var/lib/key_findings_data',
            'config_dir': '/app/config'
        }
        
        # Host paths for volume mounting
        self.host_paths = {
            'data_dir': './data/key_findings',
            'backup_dir': './data/key_findings/backups',
            'volume_mount': '/var/lib/key_findings_data',
            'config_dir': './config/key_findings'
        }
        
        # Database configuration
        self.db_config = {
            'path': self._get_db_path(),
            'backup_enabled': True,
            'backup_interval_hours': 1,
            'max_backups': 24,  # Keep 24 hours of backups
            'auto_vacuum': True,
            'vacuum_interval_hours': 6
        }
        
        # Performance monitoring
        self.performance_config = {
            'metrics_retention_days': 30,
            'log_level': 'INFO',
            'enable_detailed_logging': os.getenv('KEY_FINDINGS_DEBUG', 'false').lower() == 'true'
        }
    
    def _get_db_path(self) -> str:
        """
        Get appropriate database path based on environment.
        
        Returns:
            Database path string
        """
        # Check if running in Docker
        if self._is_docker_environment():
            db_path = os.getenv('KEY_FINDINGS_DB_PATH', self.docker_paths['data_dir'] + '/key_findings.db')
            self.logger.info(f"Using Docker database path: {db_path}")
            return db_path
        else:
            db_path = os.getenv('KEY_FINDINGS_DB_PATH', self.host_paths['data_dir'] + '/key_findings.db')
            self.logger.info(f"Using host database path: {db_path}")
            return db_path
    
    def _is_docker_environment(self) -> bool:
        """
        Check if running in Docker environment.
        
        Returns:
            True if in Docker, False otherwise
        """
        # Check for Docker indicators
        docker_indicators = [
            os.path.exists('/.dockerenv'),
            os.getenv('DOCKER_CONTAINER') is not None,
            os.getenv('KUBERNETES_SERVICE_HOST') is not None,
            '/docker/' in os.getenv('PATH', '')
        ]
        
        is_docker = any(docker_indicators)
        self.logger.info(f"Docker environment detected: {is_docker}")
        return is_docker
    
    def ensure_persistence_directories(self) -> Dict[str, bool]:
        """
        Ensure all necessary directories exist for persistence.
        
        Returns:
            Dictionary with directory creation results
        """
        results = {}
        
        if self._is_docker_environment():
            paths_to_create = [
                self.docker_paths['data_dir'],
                self.docker_paths['backup_dir'],
                self.docker_paths['config_dir']
            ]
        else:
            paths_to_create = [
                self.host_paths['data_dir'],
                self.host_paths['backup_dir'],
                self.host_paths['config_dir']
            ]
        
        for path in paths_to_create:
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
                results[path] = True
                self.logger.info(f"Ensured directory exists: {path}")
            except Exception as e:
                results[path] = False
                self.logger.error(f"Failed to create directory {path}: {e}")
        
        return results
    
    def get_docker_compose_config(self) -> str:
        """
        Generate Docker Compose configuration for Key Findings persistence.
        
        Returns:
            Docker Compose YAML string
        """
        config = f"""
version: '3.8'

services:
  dashboard-app:
    build: .
    container_name: management-tools-dashboard
    ports:
      - "8050:8050"
    environment:
      # Key Findings Configuration
      - KEY_FINDINGS_DB_PATH={self.docker_paths['data_dir']}/key_findings.db
      - KEY_FINDINGS_BACKUP_PATH={self.docker_paths['backup_dir']}
      - KEY_FINDINGS_VOLUME_MOUNT={self.docker_paths['volume_mount']}
      - OPENROUTER_API_KEY=${{OPENROUTER_API_KEY}}
      - KEY_FINDINGS_DEBUG=false
      
      # Performance Configuration
      - KEY_FINDINGS_CACHE_TTL=86400
      - KEY_FINDINGS_MAX_HISTORY=100
      - KEY_FINDINGS_AUTO_GENERATE=true
      
      # AI Configuration
      - PRIMARY_MODEL=openai/gpt-4o-mini
      - FALLBACK_MODELS=nvidia/llama-3.1-nemotron-70b-instruct,meta-llama/llama-3.1-8b-instruct:free
      
      # Analysis Parameters
      - KEY_FINDINGS_PCA_WEIGHT=0.3
      - KEY_FINDINGS_CONFIDENCE_THRESHOLD=0.7
      - KEY_FINDINGS_MAX_TOKENS=4000
    
    volumes:
      # Persistent data volume
      - {self.host_paths['volume_mount']}:{self.docker_paths['volume_mount']}:rw
      
      # Database and backups
      - {self.host_paths['data_dir']}:{self.docker_paths['data_dir']}:rw
      - {self.host_paths['backup_dir']}:{self.docker_paths['backup_dir']}:rw
      
      # Configuration
      - {self.host_paths['config_dir']}:{self.docker_paths['config_dir']}:rw
    
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8050/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # Resource limits for stability
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

volumes:
  key_findings_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: {self.host_paths['volume_mount']}
"""
        return config
    
    def get_dockerfile_instructions(self) -> str:
        """
        Generate Dockerfile instructions for Key Findings persistence.
        
        Returns:
            Dockerfile instructions string
        """
        instructions = f"""
# Key Findings Persistence Dockerfile Instructions

# Add these lines to your existing Dockerfile:

# Create necessary directories
RUN mkdir -p {self.docker_paths['data_dir']} \\
    && mkdir -p {self.docker_paths['backup_dir']} \\
    && mkdir -p {self.docker_paths['config_dir']} \\
    && mkdir -p {self.docker_paths['volume_mount']}

# Set proper permissions for data persistence
RUN chmod 755 {self.docker_paths['data_dir']} \\
    && chmod 755 {self.docker_paths['backup_dir']} \\
    && chmod 755 {self.docker_paths['config_dir']} \\
    && chmod 755 {self.docker_paths['volume_mount']}

# Create non-root user for security
RUN groupadd -r keyfindings && useradd -r -g keyfindings keyfindings

# Set ownership for persistence directories
RUN chown -R keyfindings:keyfindings {self.docker_paths['data_dir']} \\
    && chown -R keyfindings:keyfindings {self.docker_paths['backup_dir']} \\
    && chown -R keyfindings:keyfindings {self.docker_paths['config_dir']} \\
    && chown -R keyfindings:keyfindings {self.docker_paths['volume_mount']}

# Switch to non-root user
USER keyfindings

# Volume declarations for Docker Compose
VOLUME ["{self.docker_paths['data_dir']}", "{self.docker_paths['backup_dir']}", "{self.docker_paths['config_dir']}"]
"""
        return instructions
    
    def get_kubernetes_config(self) -> str:
        """
        Generate Kubernetes configuration for Key Findings persistence.
        
        Returns:
            Kubernetes YAML string
        """
        config = f"""
# Key Findings Kubernetes Persistence Configuration

apiVersion: apps/v1
kind: Deployment
metadata:
  name: management-tools-dashboard
spec:
  replicas: 1
  selector:
    matchLabels:
      app: management-tools-dashboard
  template:
    metadata:
      labels:
        app: management-tools-dashboard
    spec:
      containers:
      - name: dashboard-app
        image: management-tools-dashboard:latest
        ports:
        - containerPort: 8050
        env:
        - name: KEY_FINDINGS_DB_PATH
          value: "{self.docker_paths['data_dir']}/key_findings.db"
        - name: KEY_FINDINGS_BACKUP_PATH
          value: "{self.docker_paths['backup_dir']}"
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: OPENROUTER_API_KEY
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        volumeMounts:
        - name: key-findings-data
          mountPath: "{self.docker_paths['data_dir']}"
        - name: key-findings-backups
          mountPath: "{self.docker_paths['backup_dir']}"
        livenessProbe:
          httpGet:
            path: /health
            port: 8050
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8050
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: key-findings-data
        persistentVolumeClaim:
          claimName: key-findings-data-pvc
      - name: key-findings-backups
        persistentVolumeClaim:
          claimName: key-findings-backups-pvc

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: key-findings-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: key-findings-backups-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
  storageClassName: standard
"""
        return config
    
    def verify_persistence_setup(self) -> Dict[str, Any]:
        """
        Verify that persistence is properly configured.
        
        Returns:
            Verification results dictionary
        """
        results = {
            'verified': False,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Check directory structure
            dir_results = self.ensure_persistence_directories()
            failed_dirs = [path for path, success in dir_results.items() if not success]
            
            if failed_dirs:
                results['issues'].append(f"Failed to create directories: {failed_dirs}")
            
            # Check database path accessibility
            db_path = self._get_db_path()
            db_dir = os.path.dirname(db_path)
            
            if not os.path.exists(db_dir):
                results['issues'].append(f"Database directory does not exist: {db_dir}")
            elif not os.access(db_dir, os.W_OK):
                results['issues'].append(f"Database directory not writable: {db_dir}")
            
            # Check backup directory
            backup_dir = self.docker_paths['backup_dir'] if self._is_docker_environment() else self.host_paths['backup_dir']
            if not os.path.exists(backup_dir):
                results['issues'].append(f"Backup directory does not exist: {backup_dir}")
            
            # Check environment variables
            required_env_vars = [
                'KEY_FINDINGS_DB_PATH',
                'OPENROUTER_API_KEY'
            ]
            
            missing_env_vars = []
            for env_var in required_env_vars:
                if not os.getenv(env_var):
                    missing_env_vars.append(env_var)
            
            if missing_env_vars:
                results['issues'].append(f"Missing environment variables: {missing_env_vars}")
                results['recommendations'].append("Set required environment variables in Docker environment")
            
            # Check volume mounts (Docker only)
            if self._is_docker_environment():
                volume_mount = self.docker_paths['volume_mount']
                if not os.path.exists(volume_mount):
                    results['issues'].append(f"Volume mount point not accessible: {volume_mount}")
                    results['recommendations'].append("Ensure Docker volumes are properly mounted")
            
            # Overall verification
            results['verified'] = len(results['issues']) == 0
            
            if results['verified']:
                results['recommendations'].append("Persistence setup is correctly configured")
            
        except Exception as e:
            results['issues'].append(f"Verification failed: {str(e)}")
        
        return results
    
    def get_environment_setup_script(self) -> str:
        """
        Generate script to set up environment for Key Findings persistence.
        
        Returns:
            Shell script string
        """
        script = f"""#!/bin/bash
# Key Findings Environment Setup Script

set -e

echo "Setting up Key Findings persistence environment..."

# Create necessary directories
mkdir -p {self.host_paths['data_dir']}
mkdir -p {self.host_paths['backup_dir']}
mkdir -p {self.host_paths['config_dir']}
mkdir -p {self.host_paths['volume_mount']}

# Set proper permissions
chmod 755 {self.host_paths['data_dir']}
chmod 755 {self.host_paths['backup_dir']}
chmod 755 {self.host_paths['config_dir']}
chmod 755 {self.host_paths['volume_mount']}

# Create environment file
cat > .env << EOF
# Key Findings Configuration
KEY_FINDINGS_DB_PATH={self.host_paths['data_dir']}/key_findings.db
KEY_FINDINGS_BACKUP_PATH={self.host_paths['backup_dir']}
KEY_FINDINGS_VOLUME_MOUNT={self.host_paths['volume_mount']}

# AI Configuration
OPENROUTER_API_KEY=your_api_key_here
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

echo "Environment setup complete!"
echo "Please edit .env file and add your OPENROUTER_API_KEY"
echo "Then run: docker-compose up --build"
"""
        return script


# Global configuration instance
_docker_config = None

def get_docker_config() -> DockerPersistenceConfig:
    """
    Get or create global Docker configuration instance.
    
    Returns:
        DockerPersistenceConfig instance
    """
    global _docker_config
    
    if _docker_config is None:
        _docker_config = DockerPersistenceConfig()
    
    return _docker_config


def setup_docker_persistence() -> Dict[str, Any]:
    """
    Set up Docker persistence for Key Findings module.
    
    Returns:
        Setup results dictionary
    """
    config = get_docker_config()
    
    # Ensure directories exist
    dir_results = config.ensure_persistence_directories()
    
    # Verify setup
    verification = config.verify_persistence_setup()
    
    return {
        'directories_created': dir_results,
        'verification': verification,
        'docker_environment': config._is_docker_environment(),
        'database_path': config._get_db_path()
    }