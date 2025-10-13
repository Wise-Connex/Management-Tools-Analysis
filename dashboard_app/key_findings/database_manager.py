"""
Key Findings Database Manager

Handles SQLite database operations for caching AI-generated findings
and managing analysis reports with persistent storage for Docker deployments.
"""

import sqlite3
import pandas as pd
import json
import hashlib
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KeyFindingsDBManager:
    """
    Database manager for Key Findings module with persistent storage.
    
    Handles caching of AI-generated reports, performance metrics,
    and analysis history with Docker-compatible persistence.
    """

    def __init__(self, db_path: str = "/app/data/key_findings.db"):
        """
        Initialize Key Findings database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._initialize_schema()

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

    def _initialize_schema(self):
        """Create database schema with all required tables and indexes."""
        schema_sql = self._get_schema_sql()
        
        with self.get_connection() as conn:
            # Execute schema creation
            for statement in schema_sql:
                try:
                    conn.execute(statement)
                except sqlite3.OperationalError as e:
                    if "already exists" not in str(e):
                        logging.warning(f"Schema creation warning: {e}")
            
            # Create indexes for better query performance
            indexes = self._get_index_sql()
            for index_sql in indexes:
                try:
                    conn.execute(index_sql)
                except sqlite3.OperationalError as e:
                    logging.warning(f"Index creation warning: {e}")

    def _get_schema_sql(self) -> List[str]:
        """
        Get SQL statements for database schema creation.
        
        Returns:
            List of SQL statements to create tables
        """
        return [
            # Reports table for storing AI-generated findings
            """
            CREATE TABLE IF NOT EXISTS key_findings_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_hash TEXT UNIQUE NOT NULL,
                tool_name TEXT NOT NULL,
                selected_sources TEXT NOT NULL,  -- JSON array
                date_range_start TEXT,
                date_range_end TEXT,
                language TEXT DEFAULT 'es',
                
                -- AI Analysis Results
                principal_findings TEXT NOT NULL,  -- JSON array
                pca_insights TEXT,  -- JSON object
                executive_summary TEXT NOT NULL,
                
                -- Metadata
                model_used TEXT NOT NULL,
                api_latency_ms INTEGER,
                confidence_score REAL,
                generation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cache_version TEXT DEFAULT '1.0',
                
                -- User Interaction
                user_rating INTEGER,  -- 1-5 stars
                user_feedback TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed DATETIME,
                
                -- Performance Metrics
                data_points_analyzed INTEGER,
                sources_count INTEGER,
                analysis_depth TEXT  -- 'basic', 'comprehensive', 'advanced'
            )
            """,
            
            # Analysis history for tracking changes over time
            """
            CREATE TABLE IF NOT EXISTS key_findings_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_hash TEXT NOT NULL,
                report_id INTEGER NOT NULL,
                change_type TEXT NOT NULL,  -- 'new', 'updated', 'rerun'
                previous_version_id INTEGER,
                change_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                change_reason TEXT,
                FOREIGN KEY (report_id) REFERENCES key_findings_reports(id)
            )
            """,
            
            # Model performance tracking
            """
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                request_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                response_time_ms INTEGER,
                token_count INTEGER,
                success BOOLEAN,
                error_message TEXT,
                user_satisfaction INTEGER  -- 1-5, if provided
            )
            """,
            
            # Cache statistics for optimization
            """
            CREATE TABLE IF NOT EXISTS cache_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_requests INTEGER DEFAULT 0,
                cache_hits INTEGER DEFAULT 0,
                cache_misses INTEGER DEFAULT 0,
                avg_response_time_ms REAL,
                unique_scenarios INTEGER DEFAULT 0
            )
            """
        ]

    def _get_index_sql(self) -> List[str]:
        """
        Get SQL statements for index creation.
        
        Returns:
            List of SQL statements to create indexes
        """
        return [
            "CREATE INDEX IF NOT EXISTS idx_reports_scenario_hash ON key_findings_reports(scenario_hash)",
            "CREATE INDEX IF NOT EXISTS idx_reports_tool_name ON key_findings_reports(tool_name)",
            "CREATE INDEX IF NOT EXISTS idx_reports_generation_timestamp ON key_findings_reports(generation_timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_history_scenario_hash ON key_findings_history(scenario_hash)",
            "CREATE INDEX IF NOT EXISTS idx_history_timestamp ON key_findings_history(change_timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_performance_model ON model_performance(model_name)",
            "CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON model_performance(request_timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_stats_date ON cache_statistics(date)"
        ]

    def generate_scenario_hash(self, tool_name: str, selected_sources: List[str], 
                           date_range_start: str = None, date_range_end: str = None,
                           language: str = 'es') -> str:
        """
        Generate unique hash for scenario identification.
        
        Args:
            tool_name: Selected management tool
            selected_sources: List of selected data sources
            date_range_start: Start date for analysis (optional)
            date_range_end: End date for analysis (optional)
            language: Analysis language
            
        Returns:
            SHA256 hash string for scenario
        """
        # Create normalized scenario data
        scenario_data = {
            'tool': tool_name.lower().strip(),
            'sources': sorted([s.lower().strip() for s in selected_sources]),
            'date_start': date_range_start or '',
            'date_end': date_range_end or '',
            'language': language.lower().strip()
        }
        
        # Convert to JSON string and generate hash
        scenario_json = json.dumps(scenario_data, sort_keys=True)
        return hashlib.sha256(scenario_json.encode('utf-8')).hexdigest()

    def cache_report(self, scenario_hash: str, report_data: Dict[str, Any]) -> int:
        """
        Cache a new AI-generated report.
        
        Args:
            scenario_hash: Unique scenario identifier
            report_data: Dictionary containing all report data
            
        Returns:
            Report ID of cached report
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO key_findings_reports (
                    scenario_hash, tool_name, selected_sources, date_range_start, date_range_end,
                    language, principal_findings, pca_insights, executive_summary,
                    model_used, api_latency_ms, confidence_score, data_points_analyzed,
                    sources_count, analysis_depth
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scenario_hash,
                report_data.get('tool_name'),
                json.dumps(report_data.get('selected_sources', [])),
                report_data.get('date_range_start'),
                report_data.get('date_range_end'),
                report_data.get('language', 'es'),
                json.dumps(report_data.get('principal_findings', [])),
                json.dumps(report_data.get('pca_insights', {})),
                report_data.get('executive_summary'),
                report_data.get('model_used'),
                report_data.get('api_latency_ms'),
                report_data.get('confidence_score'),
                report_data.get('data_points_analyzed'),
                report_data.get('sources_count'),
                report_data.get('analysis_depth', 'comprehensive')
            ))
            
            report_id = cursor.lastrowid
            
            # Add to history
            self._add_history_entry(scenario_hash, report_id, 'new', None, 'Initial generation')
            
            return report_id

    def get_cached_report(self, scenario_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached report for scenario.
        
        Args:
            scenario_hash: Unique scenario identifier
            
        Returns:
            Report data dictionary or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, tool_name, selected_sources, date_range_start, date_range_end,
                       language, principal_findings, pca_insights, executive_summary,
                       model_used, api_latency_ms, confidence_score, generation_timestamp,
                       user_rating, user_feedback, access_count, data_points_analyzed,
                       sources_count, analysis_depth
                FROM key_findings_reports
                WHERE scenario_hash = ?
            """, (scenario_hash,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Update access count and last accessed
            conn.execute("""
                UPDATE key_findings_reports 
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (row[0],))
            
            # Convert to dictionary
            return {
                'id': row[0],
                'tool_name': row[1],
                'selected_sources': json.loads(row[2]) if row[2] else [],
                'date_range_start': row[3],
                'date_range_end': row[4],
                'language': row[5],
                'principal_findings': json.loads(row[6]) if row[6] else [],
                'pca_insights': json.loads(row[7]) if row[7] else {},
                'executive_summary': row[8],
                'model_used': row[9],
                'api_latency_ms': row[10],
                'confidence_score': row[11],
                'generation_timestamp': row[12],
                'user_rating': row[13],
                'user_feedback': row[14],
                'access_count': row[15],
                'data_points_analyzed': row[16],
                'sources_count': row[17],
                'analysis_depth': row[18]
            }

    def log_model_performance(self, model_name: str, response_time_ms: int,
                           token_count: int, success: bool, error_message: str = None,
                           user_satisfaction: int = None):
        """
        Log model performance metrics.
        
        Args:
            model_name: Name of the AI model used
            response_time_ms: Response time in milliseconds
            token_count: Number of tokens processed
            success: Whether the request was successful
            error_message: Error message if failed
            user_satisfaction: User satisfaction rating (1-5)
        """
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO model_performance (
                    model_name, response_time_ms, token_count, success, error_message, user_satisfaction
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (model_name, response_time_ms, token_count, success, error_message, user_satisfaction))

    def update_cache_statistics(self, date: str, cache_hit: bool, response_time_ms: int):
        """
        Update daily cache statistics.
        
        Args:
            date: Date string (YYYY-MM-DD)
            cache_hit: Whether this was a cache hit
            response_time_ms: Response time in milliseconds
        """
        with self.get_connection() as conn:
            # Check if entry exists for this date
            cursor = conn.execute("""
                SELECT total_requests, cache_hits, cache_misses, avg_response_time_ms
                FROM cache_statistics
                WHERE date = ?
            """, (date,))
            
            row = cursor.fetchone()
            if row:
                # Update existing entry
                total_requests = row[0] + 1
                cache_hits = row[1] + (1 if cache_hit else 0)
                cache_misses = row[2] + (0 if cache_hit else 1)
                avg_response_time = (row[3] * row[0] + response_time_ms) / total_requests
                
                conn.execute("""
                    UPDATE cache_statistics
                    SET total_requests = ?, cache_hits = ?, cache_misses = ?, avg_response_time_ms = ?
                    WHERE date = ?
                """, (total_requests, cache_hits, cache_misses, avg_response_time, date))
            else:
                # Create new entry
                conn.execute("""
                    INSERT INTO cache_statistics (
                        date, total_requests, cache_hits, cache_misses, avg_response_time_ms
                    ) VALUES (?, ?, ?, ?, ?)
                """, (date, 1, 1 if cache_hit else 0, 0 if cache_hit else 1, response_time_ms))

    def _add_history_entry(self, scenario_hash: str, report_id: int, 
                         change_type: str, previous_version_id: int = None,
                         change_reason: str = None):
        """Add entry to analysis history."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO key_findings_history (
                    scenario_hash, report_id, change_type, previous_version_id, change_reason
                ) VALUES (?, ?, ?, ?, ?)
            """, (scenario_hash, report_id, change_type, previous_version_id, change_reason))

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache performance metrics
        """
        with self.get_connection() as conn:
            # Get overall statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_reports,
                    AVG(access_count) as avg_access_count,
                    COUNT(DISTINCT tool_name) as unique_tools,
                    COUNT(DISTINCT scenario_hash) as unique_scenarios
                FROM key_findings_reports
            """)
            
            overall_stats = cursor.fetchone()
            
            # Get recent cache performance
            cursor = conn.execute("""
                SELECT 
                    SUM(total_requests) as total_requests,
                    SUM(cache_hits) as total_hits,
                    SUM(cache_misses) as total_misses,
                    AVG(avg_response_time_ms) as avg_response_time
                FROM cache_statistics
                WHERE date >= date('now', '-30 days')
            """)
            
            recent_stats = cursor.fetchone()
            
            # Calculate hit rate
            total_requests = recent_stats[0] or 0
            total_hits = recent_stats[1] or 0
            hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_reports': overall_stats[0] or 0,
                'avg_access_count': round(overall_stats[1] or 0, 2),
                'unique_tools': overall_stats[2] or 0,
                'unique_scenarios': overall_stats[3] or 0,
                'recent_total_requests': total_requests,
                'recent_cache_hits': total_hits,
                'recent_cache_misses': recent_stats[2] or 0,
                'recent_hit_rate': round(hit_rate, 2),
                'recent_avg_response_time': round(recent_stats[3] or 0, 2)
            }

    def verify_persistence(self) -> bool:
        """
        Verify database persistence and integrity.
        
        Returns:
            True if database is accessible and has valid schema
        """
        try:
            with self.get_connection(timeout=5.0) as conn:
                # Check if main table exists
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='key_findings_reports'
                """)
                return len(cursor.fetchall()) > 0
        except Exception as e:
            logging.error(f"Persistence verification failed: {e}")
            return False

    def cleanup_old_cache(self, days_to_keep: int = 90):
        """
        Clean up old cache entries to manage database size.
        
        Args:
            days_to_keep: Number of days to keep cache entries
        """
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
        
        with self.get_connection() as conn:
            # Delete old reports
            cursor = conn.execute("""
                DELETE FROM key_findings_reports 
                WHERE generation_timestamp < ?
            """, (cutoff_date.isoformat(),))
            
            deleted_reports = cursor.rowcount
            
            # Delete old history
            cursor = conn.execute("""
                DELETE FROM key_findings_history 
                WHERE change_timestamp < ?
            """, (cutoff_date.isoformat(),))
            
            deleted_history = cursor.rowcount
            
            # Delete old performance logs
            cursor = conn.execute("""
                DELETE FROM model_performance 
                WHERE request_timestamp < ?
            """, (cutoff_date.isoformat(),))
            
            deleted_performance = cursor.rowcount
            
            # Delete old statistics
            cursor = conn.execute("""
                DELETE FROM cache_statistics 
                WHERE date < ?
            """, (cutoff_date.strftime('%Y-%m-%d'),))
            
            deleted_stats = cursor.rowcount
            
            logging.info(f"Cache cleanup completed: {deleted_reports} reports, {deleted_history} history entries, "
                        f"{deleted_performance} performance logs, {deleted_stats} statistics entries")
            
            # Vacuum database to reclaim space
            conn.execute("VACUUM")
            
            return {
                'deleted_reports': deleted_reports,
                'deleted_history': deleted_history,
                'deleted_performance': deleted_performance,
                'deleted_statistics': deleted_stats
            }

    def get_database_size(self) -> int:
        """
        Get size of database file in bytes.
        
        Returns:
            Size in bytes, or 0 if file doesn't exist
        """
        if self.db_path.exists():
            return self.db_path.stat().st_size
        return 0