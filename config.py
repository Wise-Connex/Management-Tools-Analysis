"""
Configuration management for the Management Tools Analysis Dashboard.
Provides centralized configuration loading with environment variable overrides.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """
    Centralized configuration management class.

    Loads configuration from JSON files in the config/ directory and allows
    environment variable overrides for deployment flexibility.
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_dir: Path to config directory (defaults to 'config' relative to project root)
        """
        # Determine project root and config directory
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Assume we're in the project root or dashboard_app directory
            current_dir = Path.cwd()
            if current_dir.name == 'dashboard_app':
                self.project_root = current_dir.parent
            else:
                self.project_root = current_dir

            self.config_dir = self.project_root / "config"

        # Load configurations
        self.database_config = self._load_config("database.json")
        self.server_config = self._load_config("server.json")
        self.paths_config = self._load_config("paths.json")

        # Apply environment variable overrides
        self._apply_env_overrides()

    def _load_config(self, filename: str) -> Dict[str, Any]:
        """
        Load a JSON configuration file.

        Args:
            filename: Name of the config file

        Returns:
            Dictionary containing configuration values
        """
        config_file = self.config_dir / filename

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {filename}: {e}")
                return self._get_default_config(filename)
        else:
            print(f"Warning: Config file {filename} not found, using defaults")
            return self._get_default_config(filename)

    def _get_default_config(self, filename: str) -> Dict[str, Any]:
        """
        Get default configuration values for a given config file.

        Args:
            filename: Name of the config file

        Returns:
            Dictionary with default configuration values
        """
        defaults = {
            "database.json": {
                "path": "dashboard_app/data.db",
                "schema_version": "1.0",
                "tables": {
                    "google_trends": "google_trends",
                    "crossref": "crossref",
                    "google_books": "google_books",
                    "bain_usability": "bain_usability",
                    "bain_satisfaction": "bain_satisfaction",
                    "metadata": "metadata"
                },
                "connection_pool": {
                    "max_connections": 10,
                    "timeout": 30.0
                }
            },
            "server.json": {
                "host": "127.0.0.1",
                "port": 8050,
                "debug": True,
                "workers": 1,
                "threaded": True,
                "processes": 1
            },
            "paths.json": {
                "data_sources": "dbase",
                "interpolation_profiles": "interpolation_profiles",
                "assets": "dashboard_app/assets",
                "logs": "logs",
                "temp": "temp",
                "backups": "backups",
                "cache": "cache"
            }
        }
        return defaults.get(filename, {})

    def _apply_env_overrides(self):
        """
        Apply environment variable overrides to configuration.
        Environment variables should be prefixed with DASHBOARD_.
        """
        # Database overrides
        if os.getenv('DASHBOARD_DATABASE_PATH'):
            self.database_config['path'] = os.getenv('DASHBOARD_DATABASE_PATH')

        # Server overrides
        if os.getenv('DASHBOARD_HOST'):
            self.server_config['host'] = os.getenv('DASHBOARD_HOST')
        if os.getenv('DASHBOARD_PORT'):
            self.server_config['port'] = int(os.getenv('DASHBOARD_PORT'))
        if os.getenv('DASHBOARD_DEBUG'):
            self.server_config['debug'] = os.getenv('DASHBOARD_DEBUG').lower() == 'true'

        # Path overrides
        if os.getenv('DASHBOARD_DATA_SOURCES'):
            self.paths_config['data_sources'] = os.getenv('DASHBOARD_DATA_SOURCES')
        if os.getenv('DASHBOARD_CONFIG_DIR'):
            self.config_dir = Path(os.getenv('DASHBOARD_CONFIG_DIR'))

    # Property accessors for commonly used paths
    @property
    def database_path(self) -> Path:
        """Get the full path to the database file."""
        return self.project_root / self.database_config.get("path", "dashboard_app/data.db")

    @property
    def data_sources_path(self) -> Path:
        """Get the full path to the data sources directory."""
        return self.project_root / self.paths_config.get("data_sources", "dbase")

    @property
    def interpolation_profiles_path(self) -> Path:
        """Get the full path to the interpolation profiles directory."""
        return self.project_root / self.paths_config.get("interpolation_profiles", "interpolation_profiles")

    @property
    def assets_path(self) -> Path:
        """Get the full path to the assets directory."""
        return self.project_root / self.paths_config.get("assets", "dashboard_app/assets")

    @property
    def logs_path(self) -> Path:
        """Get the full path to the logs directory."""
        return self.project_root / self.paths_config.get("logs", "logs")

    @property
    def server_host(self) -> str:
        """Get the server host."""
        return self.server_config.get("host", "127.0.0.1")

    @property
    def server_port(self) -> int:
        """Get the server port."""
        return self.server_config.get("port", 8050)

    @property
    def server_debug(self) -> bool:
        """Get the server debug mode."""
        return self.server_config.get("debug", True)

    def get_table_name(self, source_key: str) -> str:
        """
        Get the database table name for a given source key.

        Args:
            source_key: The source identifier (e.g., 'google_trends', 'crossref')

        Returns:
            The table name for the source
        """
        return self.database_config.get("tables", {}).get(source_key, source_key)

    def get_connection_config(self) -> Dict[str, Any]:
        """
        Get database connection configuration.

        Returns:
            Dictionary with connection parameters
        """
        return self.database_config.get("connection_pool", {})

    def save_config(self, filename: str, config: Dict[str, Any]):
        """
        Save configuration to a JSON file.

        Args:
            filename: Name of the config file
            config: Configuration dictionary to save
        """
        config_file = self.config_dir / filename
        self.config_dir.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def reload_config(self):
        """
        Reload all configuration files from disk.
        Useful for runtime configuration updates.
        """
        self.database_config = self._load_config("database.json")
        self.server_config = self._load_config("server.json")
        self.paths_config = self._load_config("paths.json")
        self._apply_env_overrides()

    def validate_config(self) -> bool:
        """
        Validate the current configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        # Check required paths exist or can be created
        required_paths = [
            self.database_path.parent,
            self.data_sources_path,
            self.logs_path
        ]

        for path in required_paths:
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    print(f"Warning: Could not create required path {path}: {e}")
                    return False

        # Check database configuration
        if not self.database_config.get("path"):
            print("Error: Database path not configured")
            return False

        return True

    def __str__(self) -> str:
        """String representation of the configuration."""
        return f"Config(project_root={self.project_root}, config_dir={self.config_dir})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Config(\n"
                f"  project_root={self.project_root},\n"
                f"  config_dir={self.config_dir},\n"
                f"  database_path={self.database_path},\n"
                f"  data_sources_path={self.data_sources_path},\n"
                f"  server_host={self.server_host}:{self.server_port}\n"
                f")")


# Global configuration instance
_config_instance = None

def get_config() -> Config:
    """
    Get the global configuration instance (singleton pattern).

    Returns:
        The global Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def reload_global_config():
    """
    Reload the global configuration instance.
    """
    global _config_instance
    if _config_instance:
        _config_instance.reload_config()

# Convenience functions for common operations
def get_database_path() -> Path:
    """Get the database file path."""
    return get_config().database_path

def get_data_sources_path() -> Path:
    """Get the data sources directory path."""
    return get_config().data_sources_path

def get_server_config() -> Dict[str, Any]:
    """Get the server configuration."""
    config = get_config()
    return {
        'host': config.server_host,
        'port': config.server_port,
        'debug': config.server_debug
    }