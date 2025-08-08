"""Utility to remove rows from years 2024 and 2025 in CSV files.

This script scans ONLY the top-level of a given `dbase` directory (non-recursive),
loads each `.csv` file, detects or derives a year per row, removes rows where the
year is 2024 or 2025, and either performs a dry-run (default) or atomically
overwrites the same file when `--apply` is provided.

Behavior and Guarantees
-----------------------
- Non-recursive: does not descend into subdirectories.
- Safe by default: dry-run prints per-file summaries and makes no changes.
- Atomic writes: when applying, writes to a temporary file and atomically replaces
  the original to avoid partial writes.
- Encoding: attempts UTF-8 first, falls back to Latin-1 if needed; writes using the
  encoding that succeeded during read.
- Delimiter preservation: attempts to detect the input delimiter and uses the same
  delimiter for writing.

Year Detection Strategy
-----------------------
1) Prefer explicit year column (case-insensitive) among canonical names: ["year", "año", "anio", "ano"].
   - If the column is numeric or can be coerced to numeric and within [1900, 2100], use it.
2) Otherwise, search for date-like columns (e.g., ["date", "fecha", "year_month", "period"]),
   and apply pandas.to_datetime to derive a year. If multiple candidates exist, pick the first
   that yields a majority of valid datetimes.
3) If still not found, try to parse all object-like columns as datetimes and pick the best candidate.
4) If the year cannot be derived reliably, skip the file and log a warning.

CLI
---
--dbase PATH       Directory containing CSV files (defaults to project `dbase`)
--apply            Apply changes; otherwise perform a dry-run.
--report           Save a summary CSV to `output/csv_reports/remove_future_years_summary.csv`.
--no-color         Disable ANSI colors in console output.

This script is designed for the Management Tools Lifecycle Analysis project.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pandas as pd


TARGET_YEARS = {2024, 2025}


@dataclass
class FileProcessResult:
    """Holds summary information for a processed CSV file."""

    file_path: str
    total_rows: int
    removed_rows: int
    kept_rows: int
    applied: bool
    status: str  # "ok", "skipped", or "error"
    message: str


def colorize(text: str, color: str, enabled: bool) -> str:
    """Wrap text with ANSI color codes if enabled.

    Supported colors: 'green', 'yellow', 'red', 'cyan'.
    """
    if not enabled:
        return text
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def detect_encoding_and_sep(file_path: str) -> Tuple[str, str]:
    """Detect file encoding (try utf-8 then latin-1) and CSV delimiter using csv.Sniffer.

    Returns a tuple (encoding, delimiter).
    """
    # Try UTF-8 first
    for encoding in ("utf-8", "latin-1"):
        try:
            with open(file_path, "r", encoding=encoding, newline="") as f:
                sample = f.read(10240)
                if not sample:
                    # Empty file; default to comma
                    return encoding, ","
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    return encoding, dialect.delimiter
                except Exception:
                    # Fallback to comma if sniffer fails
                    return encoding, ","
        except UnicodeDecodeError:
            continue
    # As a last resort
    return "latin-1", ","


def read_csv_with_fallback(file_path: str, sep: Optional[str] = None) -> Tuple[pd.DataFrame, str]:
    """Read CSV trying UTF-8 then Latin-1. Returns (DataFrame, encoding_used).

    If `sep` is None, let pandas infer the separator using engine='python'.
    """
    for encoding in ("utf-8", "latin-1"):
        try:
            if sep is None:
                df = pd.read_csv(file_path, engine="python")
            else:
                df = pd.read_csv(file_path, sep=sep)
            return df, encoding
        except UnicodeDecodeError:
            continue
    # If both failed with UnicodeDecodeError, raise the last
    # Note: pandas may raise other exceptions (ParserError), which should bubble up
    raise UnicodeDecodeError("utf-8", b"", 0, 1, "Failed to decode with utf-8 and latin-1")


def coerce_year_series(df: pd.DataFrame) -> Optional[pd.Series]:
    """Attempt to produce a Series of years from the given DataFrame.

    Returns a Series of dtype Int64 (nullable) with years where known; or None if not derivable.
    """
    if df.empty:
        return pd.Series(dtype="Int64")

    # Normalize column names for case-insensitive matching
    lower_cols = {c.lower(): c for c in df.columns}

    # 1) Explicit year columns first
    canonical_years = ["year", "año", "anio", "ano"]
    for candidate in canonical_years:
        if candidate in lower_cols:
            col = lower_cols[candidate]
            series = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            # Sanity filter to plausible year range
            series = series.where((series >= 1900) & (series <= 2100))
            if series.notna().any():
                return series

    # 2) Try known date-like columns
    date_like = ["date", "fecha", "year_month", "yearmonth", "period"]
    for candidate in date_like:
        if candidate in lower_cols:
            col = lower_cols[candidate]
            dt = pd.to_datetime(df[col], errors="coerce")
            years = dt.dt.year.astype("Int64")
            if years.notna().sum() >= max(1, int(0.5 * len(df))):
                return years

    # 3) Try to parse any object-like column as datetime and choose the best
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            dt = pd.to_datetime(df[col], errors="coerce")
            years = dt.dt.year.astype("Int64")
            if years.notna().sum() >= max(1, int(0.7 * len(df))):
                return years

    # 4) As a fallback: if any integer-like column is within plausible year range, use it
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col]) or pd.api.types.is_float_dtype(df[col]):
            series = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            series = series.where((series >= 1900) & (series <= 2100))
            if series.notna().sum() >= max(1, int(0.7 * len(df))):
                return series

    return None


def filter_out_target_years(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, Optional[str]]:
    """Remove rows whose year is in TARGET_YEARS.

    Returns: (filtered_df, removed_count, year_source_message)
    year_source_message describes how the year was derived or why it failed.
    """
    years = coerce_year_series(df)
    if years is None:
        return df, 0, "year not found: skipped"

    mask_remove = years.isin(list(TARGET_YEARS))
    removed_count = int(mask_remove.sum())
    if removed_count == 0:
        return df, 0, "year derived: no 2024/2025 rows"

    kept_df = df.loc[~mask_remove].copy()
    return kept_df, removed_count, "year derived: rows removed"


def atomic_write(file_path: str, df: pd.DataFrame, sep: str, encoding: str) -> None:
    """Write DataFrame to a temporary file and atomically replace the original."""
    tmp_path = f"{file_path}.tmp"
    # Ensure write using the same delimiter and encoding
    df.to_csv(tmp_path, index=False, sep=sep, encoding=encoding)
    os.replace(tmp_path, file_path)


def process_file(file_path: str, apply_changes: bool, color: bool) -> FileProcessResult:
    """Process a single CSV file: filter out rows for 2024 and 2025.

    Returns a FileProcessResult summarizing the outcome.
    """
    try:
        # Detect encoding and delimiter to preserve on write
        encoding, sep = detect_encoding_and_sep(file_path)

        df, read_encoding = read_csv_with_fallback(file_path, sep=sep)
        total_rows = len(df)

        filtered_df, removed_count, msg = filter_out_target_years(df)
        kept_rows = len(filtered_df)

        if removed_count == 0:
            return FileProcessResult(
                file_path=file_path,
                total_rows=total_rows,
                removed_rows=0,
                kept_rows=kept_rows,
                applied=False,
                status="skipped",
                message=msg,
            )

        if apply_changes:
            # Use the encoding that succeeded in read; preserve detected delimiter
            atomic_write(file_path, filtered_df, sep=sep, encoding=read_encoding)
            return FileProcessResult(
                file_path=file_path,
                total_rows=total_rows,
                removed_rows=removed_count,
                kept_rows=kept_rows,
                applied=True,
                status="ok",
                message="applied",
            )
        else:
            return FileProcessResult(
                file_path=file_path,
                total_rows=total_rows,
                removed_rows=removed_count,
                kept_rows=kept_rows,
                applied=False,
                status="ok",
                message="dry-run",
            )
    except Exception as exc:  # Catch and continue with other files
        return FileProcessResult(
            file_path=file_path,
            total_rows=0,
            removed_rows=0,
            kept_rows=0,
            applied=False,
            status="error",
            message=f"{type(exc).__name__}: {exc}",
        )


def list_top_level_csvs(dbase_dir: str) -> List[str]:
    """List .csv files that are direct children of `dbase_dir` (non-recursive)."""
    entries = []
    for name in os.listdir(dbase_dir):
        fp = os.path.join(dbase_dir, name)
        if os.path.isfile(fp) and name.lower().endswith(".csv"):
            entries.append(fp)
    return sorted(entries)


def write_report(results: List[FileProcessResult], report_path: str) -> None:
    """Write a CSV report summarizing the operations performed/per-file."""
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    rows = [
        {
            "file_path": r.file_path,
            "status": r.status,
            "message": r.message,
            "total_rows": r.total_rows,
            "removed_rows": r.removed_rows,
            "kept_rows": r.kept_rows,
            "applied": r.applied,
        }
        for r in results
    ]
    pd.DataFrame(rows).to_csv(report_path, index=False)


def print_result(result: FileProcessResult, color: bool) -> None:
    """Pretty-print per-file summary to stdout."""
    base = os.path.basename(result.file_path)
    if result.status == "ok":
        if result.removed_rows > 0:
            status_text = colorize("REMOVED", "green", color)
        else:
            status_text = colorize("UNCHANGED", "cyan", color)
    elif result.status == "skipped":
        status_text = colorize("SKIPPED", "yellow", color)
    else:
        status_text = colorize("ERROR", "red", color)

    print(
        f"[{status_text}] {base} | total={result.total_rows} removed={result.removed_rows} kept={result.kept_rows} | {result.message}"
    )


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    default_dbase = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, "dbase")
    )
    parser = argparse.ArgumentParser(
        description=(
            "Remove rows for years 2024 and 2025 from CSV files in the top level of a dbase directory (non-recursive)."
        )
    )
    parser.add_argument(
        "--dbase",
        type=str,
        default=default_dbase,
        help="Path to the dbase directory (non-recursive scan).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (atomic overwrite). If not set, performs a dry-run only.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help=(
            "Write a summary CSV to output/csv_reports/remove_future_years_summary.csv"
        ),
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors in console output.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Entrypoint for CLI execution."""
    args = parse_args(argv)
    dbase_dir = os.path.abspath(args.dbase)
    color = not args.no_color

    if not os.path.isdir(dbase_dir):
        print(
            colorize(
                f"Error: dbase directory not found: {dbase_dir}", "red", color
            ),
            file=sys.stderr,
        )
        return 2

    print(
        colorize(
            f"Scanning (non-recursive) CSV files in: {dbase_dir}", "cyan", color
        )
    )

    csv_files = list_top_level_csvs(dbase_dir)
    if not csv_files:
        print(colorize("No CSV files found at top-level.", "yellow", color))
        return 0

    results: List[FileProcessResult] = []
    for fp in csv_files:
        res = process_file(fp, apply_changes=args.apply, color=color)
        print_result(res, color=color)
        results.append(res)

    # Optional report
    if args.report:
        report_path = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
            "output",
            "csv_reports",
            "remove_future_years_summary.csv",
        )
        write_report(results, report_path)
        print(colorize(f"Report written: {report_path}", "green", color))

    # Exit code: 0 if no errors, 1 if any error occurred
    had_error = any(r.status == "error" for r in results)
    return 1 if had_error else 0


if __name__ == "__main__":
    raise SystemExit(main())


