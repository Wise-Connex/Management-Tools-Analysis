"""
Key Findings Service

Main service that integrates all components for AI-powered
doctoral-level analysis with intelligent caching and performance monitoring.
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
from pathlib import Path

# Import Key Findings components
from .database_manager import KeyFindingsDBManager
from .ai_service import OpenRouterService, get_openrouter_service
from .data_aggregator import DataAggregator
from .prompt_engineer import PromptEngineer
from .modal_component import KeyFindingsModal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KeyFindingsService:
    """
    Main service for Key Findings functionality.
    
    Integrates data aggregation, AI analysis, caching, and performance monitoring
    to provide doctoral-level insights with optimal performance.
    """

    def __init__(self, db_manager, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize Key Findings service.
        
        Args:
            db_manager: Main database manager instance
            api_key: OpenRouter API key (optional)
            config: Configuration dictionary
        """
        self.db_manager = db_manager
        
        # Initialize Key Findings database
        db_path = config.get('key_findings_db_path', '/app/data/key_findings.db') if config else '/app/data/key_findings.db'
        self.kf_db_manager = KeyFindingsDBManager(db_path)
        
        # Initialize AI service
        self.ai_service = get_openrouter_service(api_key, config)
        
        # Initialize data aggregator
        self.data_aggregator = DataAggregator(db_manager, self.kf_db_manager)
        
        # Initialize prompt engineer
        self.prompt_engineer = PromptEngineer()
        
        # Initialize modal component (will be set later with app instance)
        self.modal_component = None
        
        # Configuration
        self.config = {
            'cache_ttl': config.get('cache_ttl', 86400) if config else 86400,  # 24 hours
            'max_retries': config.get('max_retries', 3) if config else 3,
            'enable_pca_emphasis': config.get('enable_pca_emphasis', True) if config else True,
            'confidence_threshold': config.get('confidence_threshold', 0.7) if config else 0.7
        }
        
        # Performance tracking
        self.performance_metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_response_time_ms': 0,
            'error_count': 0
        }
    
    def set_modal_component(self, app, language_store):
        """
        Set the modal component for this service.
        
        Args:
            app: Dash application instance
            language_store: Language state store
        """
        self.modal_component = KeyFindingsModal(app, language_store)
    
    def get_modal_component(self):
        """
        Get the modal component instance.
        
        Returns:
            KeyFindingsModal instance or None
        """
        return self.modal_component

    async def generate_key_findings(self, tool_name: str, selected_sources: List[str], 
                                  language: str = 'es', force_refresh: bool = False) -> Dict[str, Any]:
        """
        Generate Key Findings analysis with intelligent caching.
        
        Args:
            tool_name: Selected management tool
            selected_sources: List of selected data sources
            language: Analysis language ('es' or 'en')
            force_refresh: Force regeneration even if cached
            
        Returns:
            Dictionary containing analysis results and metadata
        """
        start_time = time.time()
        self.performance_metrics['total_requests'] += 1
        
        try:
            # Generate scenario hash for caching - use display names for consistency
            scenario_hash = self.kf_db_manager.generate_scenario_hash(
                tool_name, selected_sources, language=language
            )
            
            # Check cache first (unless force refresh)
            if not force_refresh:
                cached_report = self.kf_db_manager.get_cached_report(scenario_hash)
                if cached_report:
                    self.performance_metrics['cache_hits'] += 1
                    response_time_ms = int((time.time() - start_time) * 1000)
                    
                    # Update cache statistics
                    today = date.today().strftime('%Y-%m-%d')
                    self.kf_db_manager.update_cache_statistics(today, True, response_time_ms)
                    
                    logging.info(f"Cache hit for scenario {scenario_hash[:8]}...")
                    
                    return {
                        'success': True,
                        'data': cached_report,
                        'cache_hit': True,
                        'response_time_ms': response_time_ms,
                        'scenario_hash': scenario_hash
                    }
            
            # Cache miss - generate new analysis
            self.performance_metrics['cache_misses'] += 1
            logging.info(f"Cache miss for scenario {scenario_hash[:8]}... Generating new analysis")
            
            # Collect analysis data - convert display names to source IDs
            from fix_source_mapping import map_display_names_to_source_ids
            selected_source_ids = map_display_names_to_source_ids(selected_sources)
            
            analysis_data = self.data_aggregator.collect_analysis_data(
                tool_name, selected_source_ids, language
            )
            
            # Update analysis data with original display names for consistency
            if 'error' not in analysis_data:
                analysis_data['selected_sources'] = selected_sources
            
            if 'error' in analysis_data:
                raise Exception(f"Data collection failed: {analysis_data['error']}")
            
            # Generate AI analysis
            ai_result = await self._generate_ai_analysis(analysis_data, language)
            
            if not ai_result['success']:
                raise Exception(f"AI analysis failed: {ai_result.get('error', 'Unknown error')}")
            
            # Prepare report data for caching
            report_data = {
                'tool_name': tool_name,
                'selected_sources': selected_sources,
                'language': language,
                'principal_findings': ai_result['content'].get('principal_findings', []),
                'pca_insights': ai_result['content'].get('pca_insights', {}),
                'executive_summary': ai_result['content'].get('executive_summary', ''),
                'model_used': ai_result['model_used'],
                'api_latency_ms': ai_result['response_time_ms'],
                'confidence_score': self._calculate_confidence_score(ai_result['content']),
                'data_points_analyzed': analysis_data.get('data_points_analyzed', 0),
                'sources_count': len(selected_sources),
                'analysis_depth': 'comprehensive'
            }
            
            # Cache the report
            report_id = self.kf_db_manager.cache_report(scenario_hash, report_data)
            
            # Get cached report with all metadata
            cached_report = self.kf_db_manager.get_cached_report(scenario_hash)
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Update cache statistics
            today = date.today().strftime('%Y-%m-%d')
            self.kf_db_manager.update_cache_statistics(today, False, response_time_ms)
            
            # Log model performance
            self.kf_db_manager.log_model_performance(
                ai_result['model_used'],
                ai_result['response_time_ms'],
                ai_result['token_count'],
                True,
                None,
                None  # User satisfaction to be provided later
            )
            
            logging.info(f"Generated new analysis for scenario {scenario_hash[:8]}... in {response_time_ms}ms")
            
            return {
                'success': True,
                'data': cached_report,
                'cache_hit': False,
                'response_time_ms': response_time_ms,
                'scenario_hash': scenario_hash,
                'report_id': report_id
            }
            
        except Exception as e:
            self.performance_metrics['error_count'] += 1
            response_time_ms = int((time.time() - start_time) * 1000)
            
            logging.error(f"Key Findings generation failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'response_time_ms': response_time_ms,
                'cache_hit': False
            }

    async def _generate_ai_analysis(self, analysis_data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """
        Generate AI analysis using prompt engineering.
        
        Args:
            analysis_data: Collected analysis data
            language: Analysis language
            
        Returns:
            AI analysis result
        """
        try:
            # Update prompt engineer language
            self.prompt_engineer.language = language
            
            # Create comprehensive analysis prompt
            prompt = self.prompt_engineer.create_analysis_prompt(analysis_data, {
                'analysis_type': 'comprehensive',
                'emphasis': 'pca' if self.config['enable_pca_emphasis'] else 'balanced'
            })
            
            # Generate AI analysis
            ai_result = await self.ai_service.generate_analysis(prompt, language=language)
            
            return ai_result
            
        except Exception as e:
            logging.error(f"AI analysis generation failed: {e}")
            raise

    def _calculate_confidence_score(self, ai_content: Dict[str, Any]) -> float:
        """
        Calculate confidence score for AI-generated content.
        
        Args:
            ai_content: AI-generated content
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            # Base confidence on content quality indicators
            confidence_factors = []
            
            # Principal findings quality
            principal_findings = ai_content.get('principal_findings', [])
            if principal_findings:
                # Check for detailed reasoning
                detailed_findings = sum(1 for f in principal_findings 
                                      if len(f.get('reasoning', '')) > 50)
                confidence_factors.append(min(detailed_findings / len(principal_findings), 1.0))
            
            # PCA insights quality
            pca_insights = ai_content.get('pca_insights', {})
            if pca_insights and not pca_insights.get('error'):
                # Check for variance explanation
                variance = pca_insights.get('variance_explained', 0)
                if isinstance(variance, (int, float)) and variance > 0:
                    confidence_factors.append(min(variance / 100, 1.0))
                elif isinstance(variance, str):
                    # Handle string variance like "73%"
                    try:
                        variance_num = float(variance.replace('%', ''))
                        confidence_factors.append(min(variance_num / 100, 1.0))
                    except ValueError:
                        pass
            
            # Executive summary quality
            executive_summary = ai_content.get('executive_summary', '')
            if executive_summary:
                # Check length and completeness
                summary_quality = min(len(executive_summary) / 200, 1.0)  # Target 200+ chars
                confidence_factors.append(summary_quality)
            
            # Calculate overall confidence
            if confidence_factors:
                return sum(confidence_factors) / len(confidence_factors)
            else:
                return 0.5  # Default confidence
                
        except Exception as e:
            logging.error(f"Confidence score calculation failed: {e}")
            return 0.5

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics.
        
        Returns:
            Performance metrics dictionary
        """
        # Calculate cache hit rate
        total_requests = self.performance_metrics['total_requests']
        cache_hit_rate = (self.performance_metrics['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        # Get database statistics
        db_stats = self.kf_db_manager.get_cache_stats()
        
        # Get AI service performance
        ai_performance = self.ai_service.get_performance_stats()
        
        return {
            'service_metrics': {
                'total_requests': total_requests,
                'cache_hits': self.performance_metrics['cache_hits'],
                'cache_misses': self.performance_metrics['cache_misses'],
                'cache_hit_rate': round(cache_hit_rate, 2),
                'error_count': self.performance_metrics['error_count'],
                'error_rate': round(self.performance_metrics['error_count'] / total_requests * 100, 2) if total_requests > 0 else 0
            },
            'database_metrics': db_stats,
            'ai_performance': ai_performance,
            'database_size_mb': round(self.kf_db_manager.get_database_size() / 1024 / 1024, 2)
        }

    def update_user_feedback(self, scenario_hash: str, rating: int, feedback: str = None):
        """
        Update user feedback for a report.
        
        Args:
            scenario_hash: Report scenario hash
            rating: User rating (1-5)
            feedback: Optional user feedback text
        """
        try:
            # Get current report
            report = self.kf_db_manager.get_cached_report(scenario_hash)
            if not report:
                logging.warning(f"Report not found for feedback: {scenario_hash}")
                return
            
            # Update report with feedback
            with self.kf_db_manager.get_connection() as conn:
                conn.execute("""
                    UPDATE key_findings_reports 
                    SET user_rating = ?, user_feedback = ?
                    WHERE scenario_hash = ?
                """, (rating, feedback, scenario_hash))
            
            # Log model performance with user satisfaction
            model_used = report.get('model_used')
            if model_used:
                self.kf_db_manager.log_model_performance(
                    model_used,
                    0,  # No response time for feedback
                    0,  # No token count for feedback
                    True,
                    None,
                    rating
                )
            
            logging.info(f"Updated user feedback for scenario {scenario_hash[:8]}... Rating: {rating}")
            
        except Exception as e:
            logging.error(f"Failed to update user feedback: {e}")

    def cleanup_old_cache(self, days_to_keep: int = 90) -> Dict[str, int]:
        """
        Clean up old cache entries.
        
        Args:
            days_to_keep: Number of days to keep cache entries
            
        Returns:
            Dictionary with cleanup results
        """
        try:
            return self.kf_db_manager.cleanup_old_cache(days_to_keep)
        except Exception as e:
            logging.error(f"Cache cleanup failed: {e}")
            return {'error': str(e)}

    def export_report(self, scenario_hash: str, format_type: str = 'json') -> Dict[str, Any]:
        """
        Export a report in specified format.
        
        Args:
            scenario_hash: Report scenario hash
            format_type: Export format ('json', 'pdf', 'csv')
            
        Returns:
            Export result with file path or content
        """
        try:
            # Get report data
            report = self.kf_db_manager.get_cached_report(scenario_hash)
            if not report:
                return {'success': False, 'error': 'Report not found'}
            
            if format_type == 'json':
                # Export as JSON
                export_data = {
                    'report': report,
                    'export_timestamp': datetime.now().isoformat(),
                    'export_format': 'json'
                }
                
                return {
                    'success': True,
                    'content': json.dumps(export_data, indent=2, ensure_ascii=False),
                    'filename': f"key_findings_{scenario_hash[:8]}.json"
                }
            
            elif format_type == 'csv':
                # Export findings as CSV
                findings = report.get('principal_findings', [])
                if findings:
                    df = pd.DataFrame(findings)
                    csv_content = df.to_csv(index=False)
                    
                    return {
                        'success': True,
                        'content': csv_content,
                        'filename': f"key_findings_{scenario_hash[:8]}.csv"
                    }
                else:
                    return {'success': False, 'error': 'No findings to export'}
            
            elif format_type == 'pdf':
                # PDF export would require additional dependencies
                return {'success': False, 'error': 'PDF export not implemented yet'}
            
            else:
                return {'success': False, 'error': f'Unsupported format: {format_type}'}
                
        except Exception as e:
            logging.error(f"Report export failed: {e}")
            return {'success': False, 'error': str(e)}

    def verify_service_health(self) -> Dict[str, Any]:
        """
        Verify service health and connectivity.
        
        Returns:
            Health check results
        """
        health_status = {
            'overall_status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        try:
            # Check database connectivity
            db_healthy = self.kf_db_manager.verify_persistence()
            health_status['components']['database'] = {
                'status': 'healthy' if db_healthy else 'unhealthy',
                'details': 'Database accessible and schema valid' if db_healthy else 'Database connection failed'
            }
            
            # Check AI service availability
            try:
                # This would be an async call in a real implementation
                # For now, just check if API key is configured
                api_key_configured = bool(self.ai_service.api_key)
                health_status['components']['ai_service'] = {
                    'status': 'healthy' if api_key_configured else 'unhealthy',
                    'details': 'API key configured' if api_key_configured else 'API key not configured'
                }
            except Exception as e:
                health_status['components']['ai_service'] = {
                    'status': 'unhealthy',
                    'details': f'AI service error: {str(e)}'
                }
            
            # Check data aggregator
            try:
                # Test with a simple query
                keywords = self.db_manager.get_keywords_list()
                health_status['components']['data_aggregator'] = {
                    'status': 'healthy',
                    'details': f'Data accessible, {len(keywords)} keywords available'
                }
            except Exception as e:
                health_status['components']['data_aggregator'] = {
                    'status': 'unhealthy',
                    'details': f'Data aggregator error: {str(e)}'
                }
            
            # Determine overall status
            component_statuses = [comp['status'] for comp in health_status['components'].values()]
            if all(status == 'healthy' for status in component_statuses):
                health_status['overall_status'] = 'healthy'
            elif any(status == 'healthy' for status in component_statuses):
                health_status['overall_status'] = 'degraded'
            else:
                health_status['overall_status'] = 'unhealthy'
            
        except Exception as e:
            health_status['overall_status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status

    def reset_performance_metrics(self):
        """Reset performance metrics."""
        self.performance_metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_response_time_ms': 0,
            'error_count': 0
        }
        self.ai_service.reset_performance_stats()

# Global service instance
_key_findings_service = None

def get_key_findings_service(db_manager, api_key: str = None, config: Dict[str, Any] = None) -> KeyFindingsService:
    """
    Get or create global Key Findings service instance.
    
    Args:
        db_manager: Database manager instance
        api_key: OpenRouter API key (optional)
        config: Configuration dictionary (optional)
        
    Returns:
        Key Findings service instance
    """
    global _key_findings_service
    
    if _key_findings_service is None:
        _key_findings_service = KeyFindingsService(db_manager, api_key, config)
    
    return _key_findings_service

def reset_key_findings_service():
    """Reset global Key Findings service instance."""
    global _key_findings_service
    _key_findings_service = None