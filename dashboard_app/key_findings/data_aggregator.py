"""
Data Aggregation Pipeline

Aggregates and synthesizes data from multiple dashboard sources
with emphasis on Principal Component Analysis for doctoral-level insights.
"""

import pandas as pd
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from scipy import stats
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataAggregator:
    """
    Aggregates and synthesizes data from multiple dashboard sources.
    
    Provides comprehensive data preparation for AI analysis with
    PCA emphasis, statistical summaries, and trend detection.
    """

    def __init__(self, db_manager, cache_manager):
        """
        Initialize data aggregator.
        
        Args:
            db_manager: Database manager instance
            cache_manager: Cache manager instance
        """
        self.db_manager = db_manager
        self.cache_manager = cache_manager

    def collect_analysis_data(self, tool_name: str, selected_sources: List[Any],
                            language: str = 'es', source_display_names: List[str] = None) -> Dict[str, Any]:
        """
        Collect all relevant data for AI analysis.

        Args:
            tool_name: Selected management tool
            selected_sources: List of selected data source IDs (integers)
            language: Analysis language
            source_display_names: Optional list of source display names (strings) for prompts

        Returns:
            Dictionary containing all analysis data
        """
        start_time = time.time()
        logging.info(f"🚀 Starting data collection for tool='{tool_name}', sources={selected_sources}, language={language}")
        
        # Handle bilingual tool name mapping - convert display name to database name
        # Import the necessary functions for tool name mapping
        try:
            from tools import get_tool_name
            from translations import TOOL_TRANSLATIONS
            
            logging.info(f"🔍 Original tool_name: '{tool_name}' (language: {language})")
            
            # If we're in English and the tool name is in English, translate it to Spanish for database query
            if language == 'en':
                # Find the Spanish key for this English value
                spanish_tool_name = None
                for spanish_name, english_name in TOOL_TRANSLATIONS['en'].items():
                    if english_name == tool_name:
                        spanish_tool_name = spanish_name
                        break
                
                if spanish_tool_name:
                    logging.info(f"🔄 Translated tool name from English to Spanish: '{tool_name}' -> '{spanish_tool_name}'")
                    tool_name = spanish_tool_name
                else:
                    logging.warning(f"⚠️ Could not find Spanish translation for tool '{tool_name}'")
            
            logging.info(f"🔍 Final tool_name for database query: '{tool_name}'")
            
        except ImportError as e:
            logging.warning(f"⚠️ Could not import translation functions: {e}")
        except Exception as e:
            logging.error(f"❌ Error in tool name translation: {e}")
        
        # Get raw data from database with timeout protection
        db_start_time = time.time()
        logging.info(f"📊 Querying database for tool='{tool_name}' with {len(selected_sources)} sources...")
        logging.info(f"🔍 Source list: {selected_sources}")

        # First check if tool exists in database
        try:
            logging.info(f"🔍 Checking if tool '{tool_name}' exists in database...")
            # Try to get a small sample first to validate the tool exists
            test_datasets, test_sl_sc = self.db_manager.get_data_for_keyword(tool_name, selected_sources[:1] if selected_sources else [])
            if not test_datasets:
                logging.warning(f"⚠️ Tool '{tool_name}' not found in database or no data available")
                available_tools = []
                try:
                    # Try to get a list of available tools from the database
                    cursor = self.db_manager.connection.execute("SELECT DISTINCT keyword FROM data_table LIMIT 10")
                    available_tools = [row[0] for row in cursor.fetchall()]
                    logging.info(f"📋 Available tools in database: {available_tools}")
                except Exception as e:
                    logging.error(f"❌ Could not retrieve available tools: {e}")

                raise Exception(f"Tool '{tool_name}' not found in database. Available tools: {available_tools[:5]}...")
        except Exception as e:
            if "not found in database" in str(e):
                raise e
            logging.info(f"✅ Tool exists, proceeding with full query...")

        try:
            # Add timeout protection for database queries
            import asyncio
            import concurrent.futures

            def db_query_with_timeout():
                return self.db_manager.get_data_for_keyword(tool_name, selected_sources)

            # Run database query with 30 second timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(db_query_with_timeout)
                try:
                    datasets_norm, sl_sc = future.result(timeout=30)  # 30 second timeout
                    db_time = time.time() - db_start_time
                    logging.info(f"✅ Database query completed in {db_time:.2f}s - retrieved {len(datasets_norm)} datasets")
                    logging.info(f"📋 Dataset keys: {list(datasets_norm.keys()) if datasets_norm else 'None'}")
                    logging.info(f"📋 Source list: {sl_sc}")
                except concurrent.futures.TimeoutError:
                    db_time = time.time() - db_start_time
                    logging.error(f"⏰ Database query timed out after {db_time:.2f}s")
                    raise Exception(f"Database query timed out after {db_time:.2f}s. The query may be hanging.")

        except Exception as e:
            db_time = time.time() - db_start_time
            if "timeout" in str(e).lower():
                logging.error(f"⏰ Database query timed out after {db_time:.2f}s")
            else:
                logging.error(f"❌ Database query failed after {db_time:.2f}s: {e}")
            import traceback
            traceback.print_exc()
            raise

        if not datasets_norm:
            logging.warning(f"⚠️ No data available for tool '{tool_name}' with selected sources")
            return {
                'error': f"No data available for tool '{tool_name}' with selected sources",
                'tool_name': tool_name,
                'selected_sources': selected_sources,
                'language': language,
                'data_points_analyzed': 0,
                'sources_count': len(selected_sources)
            }
        
        # Create combined dataset
        combine_start_time = time.time()
        logging.info(f"🔄 Creating combined dataset from {len(datasets_norm)} sources...")
        combined_dataset = self._create_combined_dataset(datasets_norm, sl_sc)
        combine_time = time.time() - combine_start_time
        logging.info(f"✅ Combined dataset created in {combine_time:.2f}s - shape: {combined_dataset.shape}")

        if combined_dataset.empty:
            logging.warning(f"⚠️ Combined dataset is empty for tool '{tool_name}'")
            return {
                'error': f"No combined data available for tool '{tool_name}'",
                'tool_name': tool_name,
                'selected_sources': selected_sources,
                'language': language,
                'data_points_analyzed': 0,
                'sources_count': len(selected_sources)
            }
        
        # Extract PCA insights
        pca_start_time = time.time()
        logging.info(f"🧮 Starting PCA analysis on {len(combined_dataset)} data points with {len(selected_sources)} sources...")
        pca_insights = self.extract_pca_insights(combined_dataset, selected_sources)
        pca_time = time.time() - pca_start_time
        pca_variance = pca_insights.get('total_variance_explained', 0) if 'error' not in pca_insights else 0
        logging.info(f"✅ PCA analysis completed in {pca_time:.2f}s - variance explained: {pca_variance:.1f}%")
        
        # Calculate statistical summaries
        stats_start_time = time.time()
        logging.info(f"📊 Starting statistical analysis...")
        statistical_summary = self.calculate_statistical_summaries(combined_dataset, selected_sources)
        stats_time = time.time() - stats_start_time
        logging.info(f"✅ Statistical analysis completed in {stats_time:.2f}s")

        # Identify trends and anomalies
        trends_start_time = time.time()
        logging.info(f"📈 Starting trends and anomalies analysis...")
        trends_analysis = self.identify_trends_and_anomalies(combined_dataset, selected_sources)
        trends_time = time.time() - trends_start_time
        logging.info(f"✅ Trends analysis completed in {trends_time:.2f}s")

        # Calculate data quality metrics
        quality_start_time = time.time()
        logging.info(f"🔍 Starting data quality assessment...")
        data_quality = self.assess_data_quality(combined_dataset, selected_sources)
        quality_time = time.time() - quality_start_time
        logging.info(f"✅ Data quality assessment completed in {quality_time:.2f}s")
        
        # Anonymize sensitive data
        anonymize_start_time = time.time()
        logging.info(f"🔒 Starting data anonymization...")
        anonymized_data = self.anonymize_sensitive_data(combined_dataset)
        anonymize_time = time.time() - anonymize_start_time
        logging.info(f"✅ Data anonymization completed in {anonymize_time:.2f}s")

        # Calculate total time
        total_time = time.time() - start_time

        # Log performance summary
        logging.info(f"📋 Data collection completed in {total_time:.2f}s total:")
        logging.info(f"   ├── Database query: {db_time:.2f}s")
        logging.info(f"   ├── Data combination: {combine_time:.2f}s")
        logging.info(f"   ├── PCA analysis: {pca_time:.2f}s")
        logging.info(f"   ├── Statistical analysis: {stats_time:.2f}s")
        logging.info(f"   ├── Trends analysis: {trends_time:.2f}s")
        logging.info(f"   ├── Data quality: {quality_time:.2f}s")
        logging.info(f"   └── Data anonymization: {anonymize_time:.2f}s")

        # Use display names for prompts if provided, otherwise use source IDs
        sources_for_prompts = source_display_names if source_display_names else selected_sources
        
        result = {
            'tool_name': tool_name,
            'selected_sources': sources_for_prompts,  # Use display names for prompts
            'selected_source_ids': selected_sources,  # Keep original IDs for reference
            'language': language,
            'data_points_analyzed': len(combined_dataset),
            'sources_count': len(selected_sources),
            'date_range_start': combined_dataset.index.min().strftime('%Y-%m-%d'),
            'date_range_end': combined_dataset.index.max().strftime('%Y-%m-%d'),
            'pca_insights': pca_insights,
            'statistical_summary': statistical_summary,
            'trends_analysis': trends_analysis,
            'data_quality': data_quality,
            'anonymized_data_summary': self._create_data_summary(anonymized_data),
            'analysis_timestamp': datetime.now().isoformat(),
            'performance_metrics': {
                'total_time_seconds': total_time,
                'database_query_time': db_time,
                'data_combination_time': combine_time,
                'pca_analysis_time': pca_time,
                'statistical_analysis_time': stats_time,
                'trends_analysis_time': trends_time,
                'data_quality_time': quality_time,
                'anonymization_time': anonymize_time
            }
        }

        logging.info(f"🎉 Data collection process completed successfully in {total_time:.2f}s")
        return result

    def extract_pca_insights(self, data: pd.DataFrame, selected_sources: List[str]) -> Dict[str, Any]:
        """
        Extract PCA-specific insights for emphasis.
        
        Args:
            data: Combined dataset
            selected_sources: List of selected sources
            
        Returns:
            Dictionary with PCA insights
        """
        if len(selected_sources) < 2:
            return {
                'error': 'PCA requires at least 2 data sources',
                'components_analyzed': 0,
                'variance_explained': 0,
                'dominant_patterns': []
            }
        
        try:
            # Prepare data for PCA
            pca_data = data.dropna()
            if len(pca_data) < 10:  # Need minimum data points
                return {
                    'error': 'Insufficient data for PCA analysis (need at least 10 data points)',
                    'components_analyzed': 0,
                    'variance_explained': 0,
                    'dominant_patterns': []
                }
            
            # Standardize data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(pca_data)
            
            # Perform PCA
            n_components = min(len(selected_sources), len(pca_data.columns))
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(scaled_data)
            
            # Calculate explained variance
            explained_variance = pca.explained_variance_ratio_
            cumulative_variance = np.cumsum(explained_variance)
            
            # Analyze component loadings
            loadings = pca.components_.T * np.sqrt(explained_variance)
            
            # Identify dominant patterns
            dominant_patterns = []
            for i in range(min(3, n_components)):  # Top 3 components
                component_loadings = loadings[:, i]
                
                # Find sources with highest loadings
                top_sources_idx = np.argsort(np.abs(component_loadings))[-3:][::-1]
                # Handle both string and integer indices
                if all(isinstance(idx, (int, np.integer)) for idx in top_sources_idx):
                    top_sources = [selected_sources[int(idx)] for idx in top_sources_idx]
                else:
                    top_sources = [str(idx) for idx in top_sources_idx]
                top_loadings = [component_loadings[idx] for idx in top_sources_idx]
                
                # Enhanced component analysis with detailed loadings interpretation
                component_analysis = self._analyze_component_detailed(
                    component_loadings, list(data.columns), i+1, explained_variance[i]
                )

                dominant_patterns.append({
                    'component': f'PC{i+1}',
                    'variance_explained': float(explained_variance[i]),
                    'cumulative_variance': float(cumulative_variance[i]),
                    'dominant_sources': top_sources,
                    'loadings': dict(zip(list(data.columns), component_loadings.tolist())),
                    'interpretation': component_analysis['interpretation'],
                    'loadings_analysis': component_analysis['loadings_analysis'],
                    'source_contributions': component_analysis['source_contributions'],
                    'pattern_type': component_analysis['pattern_type']
                })
            
            return {
                'components_analyzed': n_components,
                'total_variance_explained': float(np.sum(explained_variance)),
                'variance_by_component': explained_variance.tolist(),
                'cumulative_variance': cumulative_variance.tolist(),
                'dominant_patterns': dominant_patterns,
                'data_points_used': len(pca_data),
                'pca_success': True
            }
            
        except Exception as e:
            logging.error(f"PCA analysis failed: {e}")
            return {
                'error': f'PCA analysis error: {str(e)}',
                'components_analyzed': 0,
                'variance_explained': 0,
                'dominant_patterns': []
            }

    def calculate_statistical_summaries(self, data: pd.DataFrame, selected_sources: List[str]) -> Dict[str, Any]:
        """
        Calculate comprehensive statistical summaries.
        
        Args:
            data: Combined dataset
            selected_sources: List of selected sources
            
        Returns:
            Dictionary with statistical summaries
        """
        summaries = {}
        
        for source in selected_sources:
            if source not in data.columns:
                continue
                
            source_data = data[source].dropna()
            
            if len(source_data) == 0:
                continue
            
            # Basic statistics
            stats_dict = {
                'count': len(source_data),
                'mean': float(source_data.mean()),
                'median': float(source_data.median()),
                'std': float(source_data.std()),
                'min': float(source_data.min()),
                'max': float(source_data.max()),
                'range': float(source_data.max() - source_data.min()),
                'q25': float(source_data.quantile(0.25)),
                'q75': float(source_data.quantile(0.75)),
                'iqr': float(source_data.quantile(0.75) - source_data.quantile(0.25)),
                'skewness': float(stats.skew(source_data)),
                'kurtosis': float(stats.kurtosis(source_data)),
                'missing_percentage': float(data[source].isna().sum() / len(data) * 100)
            }
            
            # Advanced statistics
            if len(source_data) > 10:
                # Trend analysis (simple linear trend)
                x = np.arange(len(source_data))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, source_data)
                stats_dict['trend'] = {
                    'slope': float(slope),
                    'intercept': float(intercept),
                    'r_squared': float(r_value ** 2),
                    'p_value': float(p_value),
                    'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                    'significance': 'significant' if p_value < 0.05 else 'not_significant'
                }
            
            summaries[source] = stats_dict
        
        # Cross-correlation analysis
        correlations = {}
        if len(selected_sources) >= 2:
            for i, source1 in enumerate(selected_sources):
                for source2 in selected_sources[i+1:]:
                    if source1 in data.columns and source2 in data.columns:
                        corr_data = data[[source1, source2]].dropna()
                        if len(corr_data) > 1:
                            correlation, p_value = stats.pearsonr(corr_data[source1], corr_data[source2])
                            correlations[f"{source1}_vs_{source2}"] = {
                                'correlation': float(correlation),
                                'p_value': float(p_value),
                                'significance': 'significant' if p_value < 0.05 else 'not_significant',
                                'strength': self._interpret_correlation_strength(abs(correlation))
                            }
        
        return {
            'source_statistics': summaries,
            'correlations': correlations,
            'overall_data_quality': self._assess_overall_quality(data)
        }

    def identify_trends_and_anomalies(self, data: pd.DataFrame, selected_sources: List[str]) -> Dict[str, Any]:
        """
        Identify significant trends and anomalies.
        
        Args:
            data: Combined dataset
            selected_sources: List of selected sources
            
        Returns:
            Dictionary with trends and anomalies
        """
        trends = {}
        anomalies = {}
        
        for source in selected_sources:
            if source not in data.columns:
                continue
                
            source_data = data[source].dropna()
            
            if len(source_data) < 12:  # Need at least 1 year of monthly data
                continue
            
            # Moving averages for trend detection
            ma_3 = source_data.rolling(window=3, center=True).mean()
            ma_12 = source_data.rolling(window=12, center=True).mean()
            
            # Trend analysis
            recent_trend = ma_3.iloc[-3:].mean() - ma_3.iloc[-6:-3].mean() if len(ma_3) >= 6 else 0
            long_term_trend = ma_12.iloc[-1] - ma_12.iloc[-13] if len(ma_12) >= 13 else 0
            
            trends[source] = {
                'recent_trend': float(recent_trend),
                'long_term_trend': float(long_term_trend),
                'trend_direction': self._classify_trend(recent_trend, long_term_trend),
                'volatility': float(source_data.rolling(window=3).std().mean()),
                'momentum': float(source_data.pct_change(period=3).iloc[-1] if len(source_data) > 3 else 0)
            }
            
            # Anomaly detection using z-score
            z_scores = np.abs(stats.zscore(source_data))
            anomaly_threshold = 2.5  # 2.5 standard deviations
            
            anomaly_indices = np.where(z_scores > anomaly_threshold)[0]
            if len(anomaly_indices) > 0:
                anomalies[source] = {
                    'count': len(anomaly_indices),
                    'percentage': float(len(anomaly_indices) / len(source_data) * 100),
                    'max_z_score': float(np.max(z_scores)),
                    'recent_anomalies': [
                        {
                            'date': data.index[idx].strftime('%Y-%m-%d'),
                            'value': float(source_data.iloc[idx]),
                            'z_score': float(z_scores[idx])
                        }
                        for idx in anomaly_indices[-5:]  # Last 5 anomalies
                    ]
                }
        
        return {
            'trends': trends,
            'anomalies': anomalies,
            'overall_patterns': self._identify_overall_patterns(trends)
        }

    def assess_data_quality(self, data: pd.DataFrame, selected_sources: List[str]) -> Dict[str, Any]:
        """
        Assess data quality metrics.
        
        Args:
            data: Combined dataset
            selected_sources: List of selected sources
            
        Returns:
            Dictionary with data quality metrics
        """
        quality_metrics = {
            'completeness': {},
            'consistency': {},
            'timeliness': {},
            'overall_score': 0
        }
        
        total_data_points = len(data)
        completeness_scores = []
        
        for source in selected_sources:
            if source not in data.columns:
                continue
                
            source_data = data[source]
            
            # Completeness metrics
            missing_count = source_data.isna().sum()
            completeness_score = (total_data_points - missing_count) / total_data_points * 100
            completeness_scores.append(completeness_score)
            
            quality_metrics['completeness'][source] = {
                'completeness_percentage': float(completeness_score),
                'missing_count': int(missing_count),
                'missing_percentage': float(missing_count / total_data_points * 100)
            }
            
            # Consistency metrics (value ranges, outliers)
            if len(source_data.dropna()) > 0:
                q1, q3 = source_data.quantile([0.25, 0.75])
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = ((source_data < lower_bound) | (source_data > upper_bound)).sum()
                consistency_score = (total_data_points - outliers) / total_data_points * 100
                
                quality_metrics['consistency'][source] = {
                    'consistency_percentage': float(consistency_score),
                    'outlier_count': int(outliers),
                    'outlier_percentage': float(outliers / total_data_points * 100),
                    'value_range': {
                        'min': float(source_data.min()),
                        'max': float(source_data.max()),
                        'range': float(source_data.max() - source_data.min())
                    }
                }
        
        # Overall quality score
        if completeness_scores:
            quality_metrics['overall_score'] = np.mean(completeness_scores)
        
        # Timeliness (data recency)
        if len(data) > 0:
            latest_date = data.index.max()
            days_since_latest = (datetime.now() - latest_date).days
            quality_metrics['timeliness'] = {
                'latest_date': latest_date.strftime('%Y-%m-%d'),
                'days_since_latest': days_since_latest,
                'timeliness_score': max(0, 100 - days_since_latest / 365 * 100)  # Decay over year
            }
        
        return quality_metrics

    def anonymize_sensitive_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Remove or anonymize sensitive information before LLM processing.
        
        Args:
            data: Combined dataset
            
        Returns:
            Anonymized dataset
        """
        anonymized = data.copy()
        
        # Remove exact dates (keep only relative timing)
        if hasattr(anonymized.index, 'to_period'):
            anonymized.index = anonymized.index.to_period('M')  # Convert to monthly periods
        
        # Add noise to values (very small amount to prevent exact identification)
        noise_factor = 0.001  # 0.1% noise
        for col in anonymized.columns:
            if anonymized[col].dtype in ['float64', 'int64']:
                noise = np.random.normal(0, anonymized[col].std() * noise_factor, len(anonymized[col]))
                anonymized[col] = anonymized[col] + noise
        
        return anonymized

    def _create_combined_dataset(self, datasets_norm: Dict[int, pd.DataFrame], 
                              sl_sc: List[int]) -> pd.DataFrame:
        """Create combined dataset from normalized data."""
        combined_data = pd.DataFrame()
        
        # Get all unique dates from all datasets
        all_dates = set()
        for source_data in datasets_norm.values():
            if source_data is not None and not source_data.empty:
                all_dates.update(source_data.index)
        
        if not all_dates:
            return pd.DataFrame()
        
        # Sort dates
        all_dates = sorted(list(all_dates))
        
        # Create DataFrame with all dates
        combined_data = pd.DataFrame(index=all_dates)
        
        # Add data from each source
        from tools import tool_file_dic
        dbase_options = {}
        for tool_list in tool_file_dic.values():
            for i, source_key in enumerate([1, 2, 3, 4, 5]):
                if i < len(tool_list) and i < len(tool_list[1]):
                    dbase_options[source_key] = tool_list[i]
        
        for source_id in sl_sc:
            if source_id in datasets_norm and source_id in dbase_options:
                source_name = dbase_options[source_id]
                source_data = datasets_norm[source_id]
                
                # Reindex to match all dates
                aligned_data = source_data.reindex(all_dates)
                combined_data[source_name] = aligned_data.iloc[:, 0] if len(aligned_data.columns) > 0 else aligned_data
        
        return combined_data.dropna(how='all')  # Remove rows where all sources are NaN

    def _create_data_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Create summary of anonymized data for AI analysis."""
        if data.empty:
            return {}
        
        summary = {
            'shape': data.shape,
            'columns': list(data.columns),
            'date_range': {
                'start': data.index.min().strftime('%Y-%m-%d'),
                'end': data.index.max().strftime('%Y-%m-%d'),
                'total_days': (data.index.max() - data.index.min()).days if hasattr(data.index.max() - data.index.min(), 'days') else 0
            },
            'basic_statistics': {}
        }
        
        for col in data.columns:
            col_data = data[col].dropna()
            if len(col_data) > 0:
                summary['basic_statistics'][col] = {
                    'mean': float(col_data.mean()),
                    'std': float(col_data.std()),
                    'min': float(col_data.min()),
                    'max': float(col_data.max())
                }
        
        return summary

    def _interpret_component(self, loadings: np.ndarray, sources: List[str], component_num: int) -> str:
        """Interpret PCA component based on loadings."""
        # Find sources with highest absolute loadings
        top_indices = np.argsort(np.abs(loadings))[-3:][::-1]
        top_sources = [sources[i] for i in top_indices]
        top_loadings = [loadings[i] for i in top_indices]

        # Determine interpretation based on loading signs and magnitudes
        positive_sources = [sources[i] for i, loading in enumerate(loadings) if loading > 0.3]
        negative_sources = [sources[i] for i, loading in enumerate(loadings) if loading < -0.3]

        interpretation = f"Component {component_num} represents "

        if positive_sources and negative_sources:
            interpretation += f"a contrast between {', '.join(positive_sources)} (positive) and {', '.join(negative_sources)} (negative)"
        elif positive_sources:
            interpretation += f"strong alignment of {', '.join(positive_sources)}"
        elif negative_sources:
            interpretation += f"inverse relationship of {', '.join(negative_sources)}"
        else:
            interpretation += "a balanced combination of all sources"

        return interpretation

    def _analyze_component_detailed(self, loadings: np.ndarray, sources: List[str], component_num: int, variance_explained: float) -> Dict[str, Any]:
        """Provide detailed analysis of a PCA component with focus on loadings and source differences."""
        # Classify sources by loading magnitude
        source_contributions = []
        for i, (source, loading) in enumerate(zip(sources, loadings)):
            abs_loading = abs(loading)

            if abs_loading >= 0.6:
                contribution_level = "high"
                role = "dominant driver"
            elif abs_loading >= 0.3:
                contribution_level = "medium"
                role = "significant contributor"
            else:
                contribution_level = "low"
                role = "minor contributor"

            source_contributions.append({
                'source': source,
                'loading': float(loading),
                'abs_loading': float(abs_loading),
                'contribution_level': contribution_level,
                'role': role,
                'direction': 'positive' if loading > 0 else 'negative' if loading < 0 else 'neutral'
            })

        # Sort by absolute loading (most important first)
        source_contributions.sort(key=lambda x: x['abs_loading'], reverse=True)

        # Determine component pattern type
        positive_loadings = [loading for loading in loadings if loading > 0.3]
        negative_loadings = [loading for loading in loadings if loading < -0.3]

        if len(positive_loadings) > 1 and len(negative_loadings) > 1:
            pattern_type = "contrast_pattern"
            interpretation = f"Component {component_num} reveals contrasting patterns between different source types"
        elif len(positive_loadings) >= 2:
            pattern_type = "alignment_pattern"
            interpretation = f"Component {component_num} shows alignment and synergy between multiple sources"
        elif len(negative_loadings) >= 2:
            pattern_type = "inverse_pattern"
            interpretation = f"Component {component_num} demonstrates inverse relationships between sources"
        else:
            pattern_type = "mixed_pattern"
            interpretation = f"Component {component_num} represents a complex interaction pattern between sources"

        # Create detailed loadings analysis
        loadings_analysis = {
            'component_magnitude': float(variance_explained),
            'dominant_sources': [contrib for contrib in source_contributions if contrib['contribution_level'] == 'high'],
            'supporting_sources': [contrib for contrib in source_contributions if contrib['contribution_level'] == 'medium'],
            'minor_sources': [contrib for contrib in source_contributions if contrib['contribution_level'] == 'low'],
            'positive_contributors': [contrib for contrib in source_contributions if contrib['direction'] == 'positive'],
            'negative_contributors': [contrib for contrib in source_contributions if contrib['direction'] == 'negative']
        }

        # Generate business interpretation
        if pattern_type == "contrast_pattern":
            pos_sources = [contrib['source'] for contrib in loadings_analysis['positive_contributors']]
            neg_sources = [contrib['source'] for contrib in loadings_analysis['negative_contributors']]
            interpretation += f", where {', '.join(pos_sources)} show positive correlation while {', '.join(neg_sources)} show inverse correlation with the main pattern"
        elif pattern_type == "alignment_pattern":
            dom_sources = [contrib['source'] for contrib in loadings_analysis['dominant_sources'][:2]]
            interpretation += f", with {', '.join(dom_sources)} working in synergy to define this pattern"
        elif pattern_type == "inverse_pattern":
            neg_sources = [contrib['source'] for contrib in loadings_analysis['negative_contributors']]
            interpretation += f", characterized by inverse relationships among {', '.join(neg_sources)}"

        return {
            'interpretation': interpretation,
            'loadings_analysis': loadings_analysis,
            'source_contributions': source_contributions,
            'pattern_type': pattern_type
        }

    def _interpret_correlation_strength(self, correlation: float) -> str:
        """Interpret correlation strength."""
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            return 'very_strong'
        elif abs_corr >= 0.6:
            return 'strong'
        elif abs_corr >= 0.4:
            return 'moderate'
        elif abs_corr >= 0.2:
            return 'weak'
        else:
            return 'very_weak'

    def _classify_trend(self, recent_trend: float, long_term_trend: float) -> str:
        """Classify trend based on recent and long-term movements."""
        if recent_trend > 0.1 and long_term_trend > 0.1:
            return 'strong_upward'
        elif recent_trend > 0.05 and long_term_trend > 0.05:
            return 'moderate_upward'
        elif recent_trend < -0.1 and long_term_trend < -0.1:
            return 'strong_downward'
        elif recent_trend < -0.05 and long_term_trend < -0.05:
            return 'moderate_downward'
        elif abs(recent_trend) < 0.05 and abs(long_term_trend) < 0.05:
            return 'stable'
        elif recent_trend * long_term_trend < 0:  # Opposite directions
            return 'reversing'
        else:
            return 'mixed'

    def _identify_overall_patterns(self, trends: Dict[str, Any]) -> List[str]:
        """Identify overall patterns across all sources."""
        patterns = []
        
        if not trends:
            return patterns
        
        # Common trend directions
        trend_directions = [trend.get('trend_direction', 'stable') for trend in trends.values()]
        upward_count = trend_directions.count('strong_upward') + trend_directions.count('moderate_upward')
        downward_count = trend_directions.count('strong_downward') + trend_directions.count('moderate_downward')
        
        if upward_count > len(trend_directions) * 0.6:
            patterns.append("Majority of sources showing upward trends")
        elif downward_count > len(trend_directions) * 0.6:
            patterns.append("Majority of sources showing downward trends")
        elif trend_directions.count('stable') > len(trend_directions) * 0.5:
            patterns.append("Most sources showing stable patterns")
        
        # Volatility patterns
        volatilities = [trend.get('volatility', 0) for trend in trends.values()]
        avg_volatility = np.mean(volatilities)
        
        if avg_volatility > np.std(volatilities) * 1.5:
            patterns.append("High volatility detected across sources")
        
        return patterns

    def _assess_overall_quality(self, data: pd.DataFrame) -> Dict[str, float]:
        """Assess overall data quality."""
        if data.empty:
            return {'score': 0, 'completeness': 0, 'consistency': 0}
        
        # Overall completeness
        total_cells = len(data) * len(data.columns)
        missing_cells = data.isna().sum().sum()
        completeness = (total_cells - missing_cells) / total_cells * 100
        
        # Overall consistency (based on outliers)
        outlier_count = 0
        for col in data.columns:
            col_data = data[col].dropna()
            if len(col_data) > 0:
                q1, q3 = col_data.quantile([0.25, 0.75])
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outlier_count += ((col_data < lower_bound) | (col_data > upper_bound)).sum()
        
        consistency = (total_cells - outlier_count) / total_cells * 100
        
        return {
            'score': (completeness + consistency) / 2,
            'completeness': float(completeness),
            'consistency': float(consistency)
        }