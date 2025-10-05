"""
Data processing module for the Management Tools Analysis Dashboard.
Contains interpolation logic and data processing functions for database population.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import os
from datetime import datetime

from config import get_config
from tools import tool_file_dic


class DataProcessor:
    """
    Data processor for interpolating and preparing data for database storage.

    Handles all interpolation methods (cubic, linear, Google Books patterns)
    and data normalization for consistent storage.
    """

    def __init__(self):
        """Initialize data processor with configuration."""
        self.config = get_config()

        # Caches for performance
        self._raw_data_cache = {}
        self._pattern_cache = {}
        self._interpolation_cache = {}

        # Keyword to CSV mapping
        self.keyword_to_csv = self._build_keyword_mapping()

    def _build_keyword_mapping(self) -> Dict[str, str]:
        """Build mapping from keywords to CSV pattern files."""
        return {
            'Alianzas y Capital de Riesgo': 'CR_AlianzasyCapitaldeRiesgo_monthly_relative.csv',
            'Benchmarking': 'CR_Benchmarking_monthly_relative.csv',
            'Calidad Total': 'CR_CalidadTotal_monthly_relative.csv',
            'Competencias Centrales': 'CR_CompetenciasCentrales_monthly_relative.csv',
            'Cuadro de Mando Integral': 'CR_CuadrodeMandoIntegral_monthly_relative.csv',
            'Estrategias de Crecimiento': 'CR_EstrategiasdeCrecimiento_monthly_relative.csv',
            'Experiencia del Cliente': 'CR_ExperienciadelCliente_monthly_relative.csv',
            'Fusiones y Adquisiciones': 'CR_FusionesyAdquisiciones_monthly_relative.csv',
            'Gestión de Costos': 'CR_GestióndeCostos_monthly_relative.csv',
            'Gestión de la Cadena de Suministro': 'CR_GestióndelaCadenadeSuministro_monthly_relative.csv',
            'Gestión del Cambio': 'CR_GestióndelCambio_monthly_relative.csv',
            'Gestión del Conocimiento': 'CR_GestióndelConocimiento_monthly_relative.csv',
            'Innovación Colaborativa': 'CR_InnovaciónColaborativa_monthly_relative.csv',
            'Lealtad del Cliente': 'CR_LealtaddelCliente_monthly_relative.csv',
            'Optimización de Precios': 'CR_OptimizacióndePrecios_monthly_relative.csv',
            'Outsourcing': 'CR_Outsourcing_monthly_relative.csv',
            'Planificación Estratégica': 'CR_PlanificaciónEstratégica_monthly_relative.csv',
            'Planificación de Escenarios': 'CR_PlanificacióndeEscenarios_monthly_relative.csv',
            'Presupuesto Base Cero': 'CR_PresupuestoBaseCero_monthly_relative.csv',
            'Propósito y Visión': 'CR_PropósitoyVisión_monthly_relative.csv',
            'Reingeniería de Procesos': 'CR_ReingenieríadeProcesos_monthly_relative.csv',
            'Segmentación de Clientes': 'CR_SegmentacióndeClientes_monthly_relative.csv',
            'Talento y Compromiso': 'CR_TalentoyCompromiso_monthly_relative.csv'
        }

    def process_all_data(self, force: bool = False, verbose: bool = False) -> Dict[str, int]:
        """
        Process all raw data and prepare for database insertion.

        Args:
            force: Force reprocessing of all data
            verbose: Enable verbose output

        Returns:
            Dictionary with processing statistics
        """
        from database import get_database_manager

        db = get_database_manager()
        stats = {"processed": 0, "skipped": 0, "errors": 0}

        # Get all keywords from tool_file_dic
        all_keywords = []
        for tool_list in tool_file_dic.values():
            for keyword in tool_list[1]:
                if keyword not in all_keywords:
                    all_keywords.append(keyword)

        if verbose:
            print(f"Processing {len(all_keywords)} keywords...")

        for keyword in all_keywords:
            try:
                if verbose:
                    print(f"Processing keyword: {keyword}")

                # Process data for this keyword
                processed_data = self.process_keyword_data(keyword, verbose=verbose)

                if processed_data:
                    # Insert into database
                    for table_name, data_batch in processed_data.items():
                        if data_batch:
                            db.insert_data_batch(table_name, data_batch)
                            stats["processed"] += len(data_batch)
                        else:
                            stats["skipped"] += 1
                else:
                    stats["skipped"] += 1

            except Exception as e:
                if verbose:
                    print(f"Error processing keyword {keyword}: {e}")
                stats["errors"] += 1

        # Update metadata
        db.update_metadata("last_updated", datetime.now().isoformat())
        db.update_metadata("total_records", stats["processed"])

        if verbose:
            print(f"Processing complete: {stats}")

        return stats

    def process_keyword_data(self, keyword: str, verbose: bool = False) -> Dict[str, List[Tuple[str, str, float]]]:
        """
        Process data for a specific keyword.

        Args:
            keyword: The keyword to process
            verbose: Enable verbose output

        Returns:
            Dictionary mapping table names to data batches
        """
        # Map source IDs to table names
        source_to_table = {
            1: "google_trends",
            2: "google_books",
            3: "bain_usability",
            4: "crossref",
            5: "bain_satisfaction"
        }

        # Get filenames for this keyword
        filenames = {}
        for source in [1, 2, 3, 4, 5]:  # All sources
            index = {1: 0, 2: 2, 3: 3, 4: 4, 5: 5}[source]
            for key, value in tool_file_dic.items():
                if keyword in value[1]:
                    filenames[source] = value[index]
                    break

        processed_data = {}

        # Process each source
        for source_id, filename in filenames.items():
            try:
                table_name = source_to_table[source_id]

                # Load and process raw data
                df = self.load_raw_data(source_id, filename)
                if df is None or df.empty:
                    continue

                # Apply interpolation based on source type
                if source_id in [3, 5]:  # Bain sources - cubic interpolation
                    interpolated_df = self.apply_cubic_interpolation(df)
                elif source_id == 2:  # Google Books - pattern-based interpolation
                    interpolated_df = self.interpolate_gb_data(df, keyword)
                else:  # Other sources - keep as-is (already monthly)
                    interpolated_df = df

                # Normalize to 0-100 scale
                normalized_df = self.normalize_data(interpolated_df)

                # Convert to database format
                data_batch = self.convert_to_batch_format(normalized_df, keyword)
                processed_data[table_name] = data_batch

                if verbose:
                    print(f"  Processed {len(data_batch)} records for {table_name}")

            except Exception as e:
                if verbose:
                    print(f"  Error processing source {source_id}: {e}")
                continue

        return processed_data

    def load_raw_data(self, source: int, filename: str) -> Optional[pd.DataFrame]:
        """
        Load raw CSV data for a specific source.

        Args:
            source: Source ID (1=Google Trends, 2=Google Books, etc.)
            filename: CSV filename

        Returns:
            DataFrame with loaded data or None if error
        """
        cache_key = f"{source}_{filename}"
        if cache_key in self._raw_data_cache:
            return self._raw_data_cache[cache_key].copy()

        file_path = self.config.data_sources_path / filename

        if not file_path.exists():
            print(f"Warning: File not found: {file_path}")
            return None

        try:
            # Read CSV file
            df = pd.read_csv(file_path, index_col=0)
            df.index = df.index.str.strip()

            # Convert index to datetime based on source type
            if source == 2:  # Google Books Ngrams - keep as annual for now
                df.index = pd.to_datetime(df.index.str.split('-').str[0], format='%Y')
            else:  # Other sources
                df.index = pd.to_datetime(df.index + '-01', format='%Y-%m-%d')

            # Cache the raw data
            self._raw_data_cache[cache_key] = df.copy()

            # Limit cache size
            if len(self._raw_data_cache) > 20:
                oldest_key = next(iter(self._raw_data_cache))
                del self._raw_data_cache[oldest_key]

            return df

        except Exception as e:
            print(f"Error loading data for source {source}: {e}")
            return None

    def apply_cubic_interpolation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply cubic interpolation to Bain data.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with interpolated monthly data
        """
        interpolated_data = pd.DataFrame()

        for column in df.columns:
            interpolated = self.cubic_interpolation(df, column)
            interpolated_data[column] = interpolated

        return interpolated_data

    def cubic_interpolation(self, df: pd.DataFrame, kw: str) -> pd.Series:
        """
        Perform cubic interpolation for a specific column.

        Args:
            df: Input DataFrame
            kw: Column name

        Returns:
            Series with interpolated values
        """
        # Create cache key
        cache_key = f"cubic_{kw}_{hash(str(df[kw].values.tobytes()) if hasattr(df[kw].values, 'tobytes') else str(df[kw].values))}_{df.index.min()}_{df.index.max()}"

        # Check cache first
        if cache_key in self._interpolation_cache:
            return self._interpolation_cache[cache_key].copy()

        # Extract actual data points (non-NaN values)
        actual_data = df[~df[kw].isna()]

        if actual_data.empty or len(actual_data) < 4:
            # Fall back to linear interpolation
            result = self.linear_interpolation(df, kw)
            self._interpolation_cache[cache_key] = result.copy()
            return result

        # Get min and max values for clipping
        original_min = actual_data[kw].min()
        original_max = actual_data[kw].max()
        clip_min = original_min
        clip_max = original_max

        # Ensure index is sorted and datetime
        actual_data = actual_data.sort_index()
        actual_data.index = pd.to_datetime(actual_data.index)

        # Convert dates to numerical values
        x = (actual_data.index - pd.Timestamp('1970-01-01')).days.values.astype(float)
        y = actual_data[kw].values

        # Create Cubic Spline
        from scipy.interpolate import CubicSpline
        cs = CubicSpline(x, y, bc_type='natural')

        # Interpolate at monthly frequency
        monthly_date_range = pd.date_range(
            start=actual_data.index.min(),
            end=actual_data.index.max(),
            freq='MS'
        )

        if monthly_date_range.empty:
            monthly_date_range = pd.date_range(start=actual_data.index.min(), periods=1, freq='MS')

        x_interp_monthly = (monthly_date_range - pd.Timestamp('1970-01-01')).days.values.astype(float)
        y_interp_monthly = cs(x_interp_monthly)

        # Clip values
        y_interp_monthly_clipped = np.clip(y_interp_monthly, clip_min, clip_max)
        df_monthly = pd.Series(y_interp_monthly_clipped, index=monthly_date_range, name=kw)

        # Force original points into monthly data
        for idx, val in actual_data[kw].items():
            idx_ts = pd.Timestamp(idx).normalize()
            if idx_ts in df_monthly.index:
                df_monthly.loc[idx_ts] = val

        df_monthly = df_monthly.sort_index()

        # Cache the result
        self._interpolation_cache[cache_key] = df_monthly.copy()

        return df_monthly

    def linear_interpolation(self, df: pd.DataFrame, kw: str) -> pd.Series:
        """
        Perform linear interpolation for a specific column.

        Args:
            df: Input DataFrame
            kw: Column name

        Returns:
            Series with interpolated values
        """
        # Create cache key
        cache_key = f"linear_{kw}_{hash(str(df[kw].values.tobytes()) if hasattr(df[kw].values, 'tobytes') else str(df[kw].values))}_{df.index.min()}_{df.index.max()}"

        # Check cache first
        if cache_key in self._interpolation_cache:
            return self._interpolation_cache[cache_key].copy()

        # Extract actual data points
        actual_data = df[~df[kw].isna()]

        if actual_data.empty:
            # Return original if no actual data
            result = pd.Series(df[kw].values, index=df.index, name=kw)
            self._interpolation_cache[cache_key] = result.copy()
            return result

        # Create date range for interpolation
        x_interp = pd.date_range(actual_data.index.min().date(), actual_data.index.max().date(), freq='MS')
        y_interp = np.interp(x_interp, actual_data.index, actual_data[kw].values)

        # Create interpolated series
        df_interpolated = pd.Series(y_interp, index=x_interp, name=kw)

        # Preserve original values
        for idx in actual_data.index:
            if idx in df_interpolated.index:
                df_interpolated.loc[idx] = actual_data.loc[idx, kw]

        # Cache the result
        self._interpolation_cache[cache_key] = df_interpolated.copy()

        return df_interpolated

    def interpolate_gb_data(self, gb_df: pd.DataFrame, keyword: str) -> pd.DataFrame:
        """
        Interpolate Google Books annual data to monthly using keyword-specific patterns.

        Args:
            gb_df: Google Books DataFrame
            keyword: Keyword for pattern lookup

        Returns:
            DataFrame with monthly interpolated data
        """
        if gb_df.empty:
            return gb_df

        # Get the column name
        gb_col = gb_df.columns[0]

        # Create monthly index for all years in GB data
        gb_years = gb_df.index.year.unique()
        monthly_index = pd.date_range(start=f'{gb_years.min()}-01-01',
                                      end=f'{gb_years.max()}-12-31',
                                      freq='MS')

        # Get CSV filename for this keyword
        csv_filename = self.keyword_to_csv.get(keyword)

        monthly_percentages = None
        if csv_filename:
            monthly_percentages = self.load_pattern_file(csv_filename)

        # Use even distribution if no pattern found
        if monthly_percentages is None:
            monthly_percentages = np.full(12, 100/12)

        # Initialize monthly data
        monthly_data = []

        for year in gb_years:
            annual_value = gb_df.loc[gb_df.index.year == year, gb_col].iloc[0] if not gb_df.loc[gb_df.index.year == year].empty else 0

            # Apply monthly percentages
            monthly_values = (monthly_percentages / 100) * annual_value

            # Add monthly values for this year
            year_start = pd.Timestamp(f'{year}-01-01')
            for month in range(12):
                monthly_data.append({
                    'date': year_start + pd.DateOffset(months=month),
                    gb_col: monthly_values[month]
                })

        # Create DataFrame
        result_df = pd.DataFrame(monthly_data)
        result_df = result_df.set_index('date')
        result_df.index.name = gb_df.index.name

        return result_df

    def load_pattern_file(self, csv_filename: str) -> Optional[np.ndarray]:
        """
        Load and cache CSV pattern files.

        Args:
            csv_filename: Name of the pattern file

        Returns:
            Array of monthly percentages or None
        """
        if csv_filename in self._pattern_cache:
            return self._pattern_cache[csv_filename]

        pattern_file = self.config.interpolation_profiles_path / csv_filename

        if pattern_file.exists():
            try:
                pattern_df = pd.read_csv(pattern_file)
                if 'PercentageDistribution' in pattern_df.columns and len(pattern_df) >= 12:
                    # Extract and normalize monthly percentages
                    monthly_percentages = pattern_df['PercentageDistribution'].values[:12]
                    monthly_percentages = monthly_percentages / monthly_percentages.sum() * 100

                    # Cache the result
                    self._pattern_cache[csv_filename] = monthly_percentages
                    return monthly_percentages
            except Exception as e:
                print(f"Warning: Could not load pattern file {csv_filename}: {e}")

        return None

    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data to 0-100 scale.

        Args:
            df: Input DataFrame

        Returns:
            Normalized DataFrame
        """
        df_norm = df.copy()
        for col in df_norm.columns:
            min_val = df_norm[col].min()
            max_val = df_norm[col].max()
            if max_val != min_val:
                df_norm[col] = 100 * (df_norm[col] - min_val) / (max_val - min_val)
            else:
                df_norm[col] = 50  # Default value if no variation

        return df_norm

    def convert_to_batch_format(self, df: pd.DataFrame, keyword: str) -> List[Tuple[str, str, float]]:
        """
        Convert DataFrame to database batch format.

        Args:
            df: Input DataFrame
            keyword: Keyword for this data

        Returns:
            List of tuples (date, keyword, value)
        """
        batch_data = []

        # Reset index to get dates as column
        df_reset = df.reset_index()
        date_col = df_reset.columns[0]
        value_col = df_reset.columns[1]

        for _, row in df_reset.iterrows():
            date_str = pd.to_datetime(row[date_col]).strftime('%Y-%m-%d')
            value = float(row[value_col])
            batch_data.append((date_str, keyword, value))

        return batch_data

    def clear_caches(self):
        """Clear all internal caches."""
        self._raw_data_cache.clear()
        self._pattern_cache.clear()
        self._interpolation_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'raw_data_cache': len(self._raw_data_cache),
            'pattern_cache': len(self._pattern_cache),
            'interpolation_cache': len(self._interpolation_cache),
            'total_cached_items': len(self._raw_data_cache) + len(self._pattern_cache) + len(self._interpolation_cache)
        }


# Global data processor instance
_data_processor_instance = None

def get_data_processor() -> DataProcessor:
    """
    Get the global data processor instance (singleton pattern).

    Returns:
        The global DataProcessor instance
    """
    global _data_processor_instance
    if _data_processor_instance is None:
        _data_processor_instance = DataProcessor()
    return _data_processor_instance

def reset_data_processor():
    """
    Reset the global data processor instance.
    """
    global _data_processor_instance
    _data_processor_instance = None