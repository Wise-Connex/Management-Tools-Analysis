"""
Key Findings Module

AI-powered doctoral-level analysis system for the Management Tools Analysis Dashboard.
Provides intelligent caching, multi-source data synthesis, and executive insights.
"""

from .database_manager import KeyFindingsDBManager
from .ai_service import OpenRouterService, get_openrouter_service
from .data_aggregator import DataAggregator
from .prompt_engineer import PromptEngineer
from .modal_component import KeyFindingsModal
from .key_findings_service import KeyFindingsService, get_key_findings_service

__version__ = "1.0.0"
__author__ = "Dimar Anez"
__description__ = "AI-powered doctoral-level analysis for management tools"

# Export main classes
__all__ = [
    'KeyFindingsDBManager',
    'OpenRouterService',
    'get_openrouter_service',
    'DataAggregator',
    'PromptEngineer',
    'KeyFindingsModal',
    'KeyFindingsService',
    'get_key_findings_service'
]

# Module configuration
DEFAULT_CONFIG = {
    'cache_ttl': 86400,  # 24 hours
    'max_retries': 3,
    'enable_pca_emphasis': True,
    'confidence_threshold': 0.7,
    'key_findings_db_path': '/app/data/key_findings.db',
    'models': [
        'openai/gpt-4o-mini',
        'nvidia/llama-3.1-nemotron-70b-instruct',
        'meta-llama/llama-3.1-8b-instruct:free'
    ],
    'timeout': 30,
    'max_tokens': 4000,
    'temperature': 0.7
}

def get_module_info():
    """Get module information."""
    return {
        'name': 'Key Findings',
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'config': DEFAULT_CONFIG
    }