#!/usr/bin/env python3
"""
Database creation and update script for the Management Tools Analysis Dashboard.

This script processes all raw data, applies interpolation algorithms, and stores
the results in a SQLite database for fast access by the dashboard application.

Usage:
    python create_database.py                    # Create/update database
    python create_database.py --force           # Force full rebuild
    python create_database.py --verbose         # Verbose output
    python create_database.py --status          # Check database status
    python create_database.py --help            # Show help

Environment Variables:
    DASHBOARD_CONFIG_DIR: Path to config directory (default: config)
    DASHBOARD_DATABASE_PATH: Custom database path
    DASHBOARD_DATA_SOURCES: Custom data sources path
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime

from config import get_config
from database import get_database_manager
from data_processor import get_data_processor


def main():
    """Main entry point for the database creation script."""
    parser = argparse.ArgumentParser(
        description="Create and update the Management Tools Analysis database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_database.py                    # Normal update
  python create_database.py --force           # Force rebuild
  python create_database.py --verbose         # Verbose output
  python create_database.py --status          # Check status
        """
    )

    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force full rebuild of database (ignore timestamps)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Check database status and exit'
    )

    parser.add_argument(
        '--config-dir',
        type=str,
        help='Path to config directory (overrides DASHBOARD_CONFIG_DIR)'
    )

    args = parser.parse_args()

    # Override config directory if specified
    if args.config_dir:
        import config
        config._config_instance = None  # Reset singleton
        config._config_instance = config.Config(args.config_dir)

    try:
        # Initialize components
        config_obj = get_config()
        db_manager = get_database_manager()
        data_processor = get_data_processor()

        if args.status:
            # Show database status
            show_database_status(db_manager, config_obj)
            return

        # Check if database needs updating
        needs_update = check_if_update_needed(db_manager, config_obj, args.force, args.verbose)

        if not needs_update and not args.force:
            print("Database is up to date. Use --force to rebuild anyway.")
            return

        # Create/update database
        print("Starting database creation/update process...")
        start_time = time.time()

        # Create schema if needed
        if not db_manager.database_exists():
            print("Creating database schema...")
            db_manager.create_schema()
            print("Schema created successfully.")
        elif args.force:
            print("Forcing schema recreation...")
            # Drop and recreate tables
            for table in config_obj.database_config.get("tables", {}).keys():
                db_manager.drop_table(table)
            db_manager.create_schema()
            print("Schema recreated successfully.")

        # Process all data
        print("Processing data..." if not args.verbose else "Processing data (verbose mode)...")
        stats = data_processor.process_all_data(force=args.force, verbose=args.verbose)

        # Show results
        elapsed_time = time.time() - start_time
        print("\nDatabase update completed!")
        print(f"Time elapsed: {elapsed_time:.2f} seconds")
        print(f"Records processed: {stats['processed']}")
        print(f"Records skipped: {stats['skipped']}")
        print(f"Errors encountered: {stats['errors']}")

        # Show final status
        show_database_status(db_manager, config_obj)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def check_if_update_needed(db_manager, config_obj, force=False, verbose=False):
    """
    Check if database update is needed.

    Args:
        db_manager: Database manager instance
        config_obj: Configuration instance
        force: Force update flag
        verbose: Verbose output flag

    Returns:
        True if update is needed
    """
    if force:
        if verbose:
            print("Force rebuild requested.")
        return True

    if not db_manager.database_exists():
        if verbose:
            print("Database does not exist.")
        return True

    # Check file modification times
    try:
        db_mtime = db_manager.db_path.stat().st_mtime

        # Check data source files
        data_sources_path = config_obj.data_sources_path
        if data_sources_path.exists():
            for csv_file in data_sources_path.glob("*.csv"):
                if csv_file.stat().st_mtime > db_mtime:
                    if verbose:
                        print(f"Data source file {csv_file.name} is newer than database.")
                    return True

        # Check interpolation profile files
        profiles_path = config_obj.interpolation_profiles_path
        if profiles_path.exists():
            for csv_file in profiles_path.glob("*.csv"):
                if csv_file.stat().st_mtime > db_mtime:
                    if verbose:
                        print(f"Interpolation profile {csv_file.name} is newer than database.")
                    return True

        if verbose:
            print("Database is up to date.")
        return False

    except Exception as e:
        if verbose:
            print(f"Error checking file timestamps: {e}")
        return True


def show_database_status(db_manager, config_obj):
    """
    Display database status information.

    Args:
        db_manager: Database manager instance
        config_obj: Configuration instance
    """
    print("\n" + "="*50)
    print("DATABASE STATUS")
    print("="*50)

    if not db_manager.database_exists():
        print("❌ Database does not exist")
        print(f"Expected path: {db_manager.db_path}")
        return

    print("✅ Database exists")
    print(f"Path: {db_manager.db_path}")
    print(f"Size: {db_manager.get_database_size()} bytes")

    # Show metadata
    metadata = db_manager.get_metadata()
    if metadata:
        print("\nMetadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

    # Show table statistics
    print("\nTable Statistics:")
    table_stats = db_manager.get_table_stats()
    total_records = 0
    total_keywords = 0

    for table, stats in table_stats.items():
        if "error" in stats:
            print(f"  {table}: ERROR - {stats['error']}")
        else:
            records = stats.get('row_count', 0)
            keywords = stats.get('keyword_count', 0)
            min_date = stats.get('min_date', 'N/A')
            max_date = stats.get('max_date', 'N/A')

            print(f"  {table}: {records} records, {keywords} keywords")
            print(f"    Date range: {min_date} to {max_date}")

            total_records += records
            total_keywords += keywords

    print(f"\nTotal: {total_records} records across {len(table_stats)} tables")
    print(f"Unique keywords: {total_keywords}")

    # Check data sources
    print("\nData Sources:")
    data_sources_path = config_obj.data_sources_path
    if data_sources_path.exists():
        csv_files = list(data_sources_path.glob("*.csv"))
        print(f"✅ Found {len(csv_files)} CSV files in {data_sources_path}")
        if csv_files:
            print("Sample files:", ", ".join(f.name for f in csv_files[:3]))
            if len(csv_files) > 3:
                print(f"... and {len(csv_files) - 3} more")
    else:
        print(f"❌ Data sources directory not found: {data_sources_path}")

    # Check interpolation profiles
    print("\nInterpolation Profiles:")
    profiles_path = config_obj.interpolation_profiles_path
    if profiles_path.exists():
        csv_files = list(profiles_path.glob("*.csv"))
        print(f"✅ Found {len(csv_files)} profile files in {profiles_path}")
    else:
        print(f"⚠️  Interpolation profiles directory not found: {profiles_path}")
        print("   (Google Books interpolation will use even distribution)")


def format_timestamp(timestamp):
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return timestamp


if __name__ == "__main__":
    main()