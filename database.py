"""
Database operations module for the Management Tools Analysis Dashboard.
Provides SQLite database management with connection pooling and data retrieval.
"""

import sqlite3
import pandas as pd
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import time
from datetime import datetime

from config import get_config


class DatabaseManager:
    """
    SQLite database manager for pre-interpolated data storage and retrieval.

    Handles schema creation, data insertion, querying, and connection management.
    """

    def __init__(self):
        """Initialize database manager with configuration."""
        self.config = get_config()
        self.db_path = self.config.database_path

        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self, timeout: float = 30.0):
        """
        Context manager for database connections.

        Args:
            timeout: Connection timeout in seconds

        Yields:
            SQLite connection object
        """
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=timeout,
                isolation_level=None  # Enable autocommit mode
            )
            conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
            conn.execute("PRAGMA synchronous=NORMAL")  # Balance between performance and safety
            conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            conn.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def create_schema(self):
        """
        Create database schema with all required tables and indexes.

        This includes data tables for each source and metadata table.
        """
        schema_sql = self._get_schema_sql()

        with self.get_connection() as conn:
            # Execute schema creation
            for statement in schema_sql:
                conn.execute(statement)

            # Create indexes
            for index_sql in self.config.database_config.get("indexes", []):
                try:
                    conn.execute(index_sql)
                except sqlite3.OperationalError as e:
                    print(f"Warning: Could not create index: {e}")

            # Insert schema version
            conn.execute("""
                INSERT OR REPLACE INTO metadata (key, value)
                VALUES (?, ?)
            """, ("schema_version", self.config.database_config.get("schema_version", "1.0")))

            # Insert creation timestamp
            conn.execute("""
                INSERT OR REPLACE INTO metadata (key, value)
                VALUES (?, ?)
            """, ("created_at", datetime.now().isoformat()))

            conn.commit()

    def _get_schema_sql(self) -> List[str]:
        """
        Get SQL statements for database schema creation.

        Returns:
            List of SQL statements to create tables
        """
        return [
            # Data tables for each source
            """
            CREATE TABLE IF NOT EXISTS google_trends (
                date TEXT NOT NULL,
                keyword TEXT NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY (date, keyword)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS crossref (
                date TEXT NOT NULL,
                keyword TEXT NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY (date, keyword)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS google_books (
                date TEXT NOT NULL,
                keyword TEXT NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY (date, keyword)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS bain_usability (
                date TEXT NOT NULL,
                keyword TEXT NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY (date, keyword)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS bain_satisfaction (
                date TEXT NOT NULL,
                keyword TEXT NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY (date, keyword)
            )
            """,
            # Metadata table
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        ]

    def insert_data_batch(self, table_name: str, data: List[Tuple[str, str, float]]):
        """
        Insert a batch of data into a table.

        Args:
            table_name: Name of the table to insert into
            data: List of tuples (date, keyword, value)
        """
        if not data:
            return

        with self.get_connection() as conn:
            conn.executemany(
                f"INSERT OR REPLACE INTO {table_name} (date, keyword, value) VALUES (?, ?, ?)",
                data
            )
            conn.commit()

    def get_data_for_keyword(self, keyword: str, sources: List[int]) -> Tuple[Dict[int, pd.DataFrame], List[int]]:
        """
        Retrieve pre-interpolated data for a keyword and list of sources.

        Args:
            keyword: The keyword to retrieve data for
            sources: List of source IDs (1=Google Trends, 2=Google Books, 3=Bain Usability, 4=Crossref, 5=Bain Satisfaction)

        Returns:
            Tuple of (datasets_norm, selected_sources) matching the original get_file_data2 format
        """
        # Map source IDs to table names
        source_to_table = {
            1: "google_trends",
            2: "google_books",
            3: "bain_usability",
            4: "crossref",
            5: "bain_satisfaction"
        }

        datasets_norm = {}
        valid_sources = []

        with self.get_connection() as conn:
            for source_id in sources:
                table_name = source_to_table.get(source_id)
                if not table_name:
                    continue

                try:
                    # Query data for this source and keyword
                    df = pd.read_sql_query(
                        f"SELECT date, value FROM {table_name} WHERE keyword = ? ORDER BY date",
                        conn,
                        params=[keyword],
                        index_col="date",
                        parse_dates=["date"]
                    )

                    if not df.empty:
                        # Normalize to 0-100 scale (assuming data is already normalized during insertion)
                        df_norm = df.copy()
                        datasets_norm[source_id] = df_norm
                        valid_sources.append(source_id)

                except Exception as e:
                    print(f"Warning: Could not retrieve data for source {source_id} ({table_name}): {e}")
                    continue

        return datasets_norm, valid_sources

    def get_metadata(self, key: Optional[str] = None) -> Dict[str, str]:
        """
        Retrieve metadata from the database.

        Args:
            key: Specific metadata key to retrieve (optional)

        Returns:
            Dictionary of metadata key-value pairs
        """
        with self.get_connection() as conn:
            if key:
                cursor = conn.execute("SELECT key, value FROM metadata WHERE key = ?", [key])
            else:
                cursor = conn.execute("SELECT key, value FROM metadata")

            return {row[0]: row[1] for row in cursor.fetchall()}

    def update_metadata(self, key: str, value: str):
        """
        Update or insert metadata.

        Args:
            key: Metadata key
            value: Metadata value
        """
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                [key, value]
            )
            conn.commit()

    def get_table_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all data tables.

        Returns:
            Dictionary with table statistics
        """
        tables = ["google_trends", "crossref", "google_books", "bain_usability", "bain_satisfaction"]
        stats = {}

        with self.get_connection() as conn:
            for table in tables:
                try:
                    # Get row count
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]

                    # Get keyword count
                    cursor = conn.execute(f"SELECT COUNT(DISTINCT keyword) FROM {table}")
                    keyword_count = cursor.fetchone()[0]

                    # Get date range
                    cursor = conn.execute(f"SELECT MIN(date), MAX(date) FROM {table}")
                    min_date, max_date = cursor.fetchone()

                    stats[table] = {
                        "row_count": row_count,
                        "keyword_count": keyword_count,
                        "min_date": min_date,
                        "max_date": max_date
                    }
                except Exception as e:
                    print(f"Warning: Could not get stats for table {table}: {e}")
                    stats[table] = {"error": str(e)}

        return stats

    def clear_table(self, table_name: str):
        """
        Clear all data from a table.

        Args:
            table_name: Name of the table to clear
        """
        with self.get_connection() as conn:
            conn.execute(f"DELETE FROM {table_name}")
            conn.commit()

    def drop_table(self, table_name: str):
        """
        Drop a table from the database.

        Args:
            table_name: Name of the table to drop
        """
        with self.get_connection() as conn:
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.commit()

    def vacuum_database(self):
        """
        Optimize database by reclaiming unused space.
        """
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            conn.commit()

    def backup_database(self, backup_path: Path):
        """
        Create a backup of the database.

        Args:
            backup_path: Path where to save the backup
        """
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as source_conn:
            with sqlite3.connect(str(backup_path)) as backup_conn:
                source_conn.backup(backup_conn)

    def get_keywords_list(self, source_id: Optional[int] = None) -> List[str]:
        """
        Get list of all keywords in the database.

        Args:
            source_id: Optional source ID to filter keywords

        Returns:
            List of unique keywords
        """
        tables = []
        if source_id:
            # Map source ID to table name
            source_to_table = {
                1: "google_trends",
                2: "google_books",
                3: "bain_usability",
                4: "crossref",
                5: "bain_satisfaction"
            }
            table_name = source_to_table.get(source_id)
            if table_name:
                tables = [table_name]
        else:
            tables = ["google_trends", "crossref", "google_books", "bain_usability", "bain_satisfaction"]

        keywords = set()

        with self.get_connection() as conn:
            for table in tables:
                try:
                    cursor = conn.execute(f"SELECT DISTINCT keyword FROM {table}")
                    keywords.update(row[0] for row in cursor.fetchall())
                except Exception as e:
                    print(f"Warning: Could not get keywords from {table}: {e}")

        return sorted(list(keywords))

    def database_exists(self) -> bool:
        """
        Check if the database file exists and has valid schema.

        Returns:
            True if database exists and is valid
        """
        if not self.db_path.exists():
            return False

        try:
            with self.get_connection(timeout=5.0) as conn:
                # Check if metadata table exists
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metadata'")
                return len(cursor.fetchall()) > 0
        except Exception:
            return False

    def get_database_size(self) -> int:
        """
        Get the size of the database file in bytes.

        Returns:
            Size in bytes, or 0 if file doesn't exist
        """
        if self.db_path.exists():
            return self.db_path.stat().st_size
        return 0

    def __str__(self) -> str:
        """String representation of the database manager."""
        exists = "exists" if self.database_exists() else "does not exist"
        size = self.get_database_size()
        return f"DatabaseManager(path={self.db_path}, {exists}, size={size} bytes)"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"DatabaseManager(db_path={self.db_path}, config={self.config})"


# Global database manager instance
_db_manager_instance = None

def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance (singleton pattern).

    Returns:
        The global DatabaseManager instance
    """
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance

def reset_database_manager():
    """
    Reset the global database manager instance.
    Useful for testing or configuration changes.
    """
    global _db_manager_instance
    _db_manager_instance = None