"""
OpenRouter.ai Integration Service

Handles AI model interactions with fallback support for generating
doctoral-level analysis of management tools data.
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class AIModelConfig:
    """Configuration for AI models."""
    name: str
    max_tokens: int
    temperature: float
    timeout: int = 30
    cost_per_1k_tokens: float = 0.001

class OpenRouterService:
    """
    Service for interacting with OpenRouter.ai API with fallback models.
    
    Provides robust AI analysis with multiple model options, retry logic,
    and performance monitoring.
    """

    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        """
        Initialize OpenRouter service.
        
        Args:
            api_key: OpenRouter.ai API key
            config: Configuration dictionary with model settings
        """
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Default configuration
        default_config = {
            'models': [
                'openai/gpt-4o-mini',
                'nvidia/llama-3.1-nemotron-70b-instruct',
                'meta-llama/llama-3.1-8b-instruct:free'
            ],
            'timeout': 30,
            'max_retries': 3,
            'retry_delay': 1.0,
            'max_tokens': 4000,
            'temperature': 0.7
        }
        
        # Merge with provided config
        self.config = {**default_config, **(config or {})}
        
        # Model configurations
        self.model_configs = {
            'openai/gpt-4o-mini': AIModelConfig(
                name='openai/gpt-4o-mini',
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                cost_per_1k_tokens=0.00015
            ),
            'nvidia/llama-3.1-nemotron-70b-instruct': AIModelConfig(
                name='nvidia/llama-3.1-nemotron-70b-instruct',
                max_tokens=4000,
                temperature=0.7,
                timeout=45,
                cost_per_1k_tokens=0.0009
            ),
            'meta-llama/llama-3.1-8b-instruct:free': AIModelConfig(
                name='meta-llama/llama-3.1-8b-instruct:free',
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                cost_per_1k_tokens=0.0
            )
        }
        
        # Performance tracking
        self.performance_stats = {}

    async def generate_analysis(self, prompt: str, model: str = None, 
                              language: str = 'es') -> Dict[str, Any]:
        """
        Generate AI analysis with fallback models.
        
        Args:
            prompt: Analysis prompt for the AI
            model: Specific model to use (optional)
            language: Analysis language ('es' or 'en')
            
        Returns:
            Dictionary containing analysis results and metadata
        """
        start_time = time.time()
        
        # Determine model order
        if model and model in self.config['models']:
            models_to_try = [model] + [m for m in self.config['models'] if m != model]
        else:
            models_to_try = self.config['models']
        
        last_error = None
        successful_model = None
        response_content = None
        token_count = 0
        
        # Try each model in order
        for attempt_model in models_to_try:
            try:
                logging.info(f"Attempting analysis with model: {attempt_model}")
                
                result = await self._call_model(prompt, attempt_model, language)
                
                if result and 'choices' in result and len(result['choices']) > 0:
                    response_content = result['choices'][0]['message']['content']
                    token_count = result.get('usage', {}).get('total_tokens', 0)
                    successful_model = attempt_model
                    break
                    
            except Exception as e:
                last_error = e
                logging.warning(f"Model {attempt_model} failed: {e}")
                continue
        
        # Calculate performance metrics
        response_time_ms = int((time.time() - start_time) * 1000)
        success = response_content is not None
        
        # Log performance
        self._log_performance(successful_model or models_to_try[-1], response_time_ms, 
                            token_count, success, str(last_error) if last_error else None)
        
        if not success:
            raise Exception(f"All models failed. Last error: {last_error}")
        
        # Parse and validate response
        try:
            parsed_response = self._parse_ai_response(response_content)
        except Exception as e:
            logging.error(f"Failed to parse AI response: {e}")
            # Return raw response if parsing fails
            parsed_response = {
                'principal_findings': [{
                    'bullet_point': response_content[:200] + "..." if len(response_content) > 200 else response_content,
                    'reasoning': "Raw AI response due to parsing error",
                    'data_source': ["AI Analysis"],
                    'confidence': "medium"
                }],
                'pca_insights': {},
                'executive_summary': response_content[:500] + "..." if len(response_content) > 500 else response_content
            }
        
        return {
            'content': parsed_response,
            'model_used': successful_model,
            'response_time_ms': response_time_ms,
            'token_count': token_count,
            'success': success,
            'language': language
        }

    async def _call_model(self, prompt: str, model: str, language: str) -> Dict[str, Any]:
        """
        Call specific AI model with retry logic.
        
        Args:
            prompt: Analysis prompt
            model: Model name
            language: Analysis language
            
        Returns:
            Raw API response
        """
        model_config = self.model_configs.get(model, self.model_configs[self.config['models'][0]])
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://management-tools-analysis.com",
            "X-Title": "Management Tools Analysis Dashboard"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt(language)
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": model_config.max_tokens,
            "temperature": model_config.temperature,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
        
        # Retry logic
        for attempt in range(self.config['max_retries']):
            try:
                timeout = aiohttp.ClientTimeout(total=model_config.timeout)
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:
                        
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:
                            # Rate limited - wait and retry
                            retry_after = int(response.headers.get('Retry-After', self.config['retry_delay']))
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            error_text = await response.text()
                            raise Exception(f"API error {response.status}: {error_text}")
                            
            except asyncio.TimeoutError:
                logging.warning(f"Timeout for model {model}, attempt {attempt + 1}")
                if attempt < self.config['max_retries'] - 1:
                    await asyncio.sleep(self.config['retry_delay'])
                    continue
                else:
                    raise
            except Exception as e:
                if attempt < self.config['max_retries'] - 1:
                    await asyncio.sleep(self.config['retry_delay'])
                    continue
                else:
                    raise
        
        raise Exception(f"Model {model} failed after {self.config['max_retries']} attempts")

    def _get_system_prompt(self, language: str) -> str:
        """
        Get system prompt based on language.
        
        Args:
            language: Analysis language ('es' or 'en')
            
        Returns:
            System prompt string
        """
        if language == 'es':
            return """
Eres un analista de investigación doctoral especializado en herramientas de gestión empresarial. 
Tu tarea es analizar datos multi-fuente y generar insights de nivel ejecutivo con énfasis en 
análisis de componentes principales (PCA).

Proporciona análisis que:
1. Sinteticen información de múltiples fuentes de datos
2. Identifiquen patrones temporales y tendencias significativas
3. Destaquen insights de PCA con explicaciones claras
4. Generen conclusiones ejecutivas accionables
5. Mantengan rigor académico doctoral

Responde siempre en formato JSON estructurado con:
- principal_findings: array de objetos con bullet_point, reasoning, data_source, confidence
- pca_insights: objeto con análisis de componentes principales
- executive_summary: resumen ejecutivo conciso
"""
        else:
            return """
You are a doctoral-level research analyst specializing in business management tools. 
Your task is to analyze multi-source data and generate executive-level insights with 
emphasis on Principal Component Analysis (PCA).

Provide analysis that:
1. Synthesizes information from multiple data sources
2. Identifies temporal patterns and significant trends
3. Highlights PCA insights with clear explanations
4. Generates actionable executive conclusions
5. Maintains doctoral academic rigor

Always respond in structured JSON format with:
- principal_findings: array of objects with bullet_point, reasoning, data_source, confidence
- pca_insights: object with principal component analysis
- executive_summary: concise executive summary
"""

    def _parse_ai_response(self, response_content: str) -> Dict[str, Any]:
        """
        Parse and validate AI response.
        
        Args:
            response_content: Raw AI response content
            
        Returns:
            Parsed response dictionary
        """
        try:
            # Try to extract JSON from response
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_content[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Validate required fields
                if 'principal_findings' not in parsed:
                    parsed['principal_findings'] = []
                if 'pca_insights' not in parsed:
                    parsed['pca_insights'] = {}
                if 'executive_summary' not in parsed:
                    parsed['executive_summary'] = ""
                
                return parsed
            else:
                # Fallback: create structured response from text
                return {
                    'principal_findings': [{
                        'bullet_point': response_content[:300] + "..." if len(response_content) > 300 else response_content,
                        'reasoning': "Extracted from AI response",
                        'data_source': ["AI Analysis"],
                        'confidence': "medium"
                    }],
                    'pca_insights': {},
                    'executive_summary': response_content[:500] + "..." if len(response_content) > 500 else response_content
                }
                
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing failed: {e}")
            # Fallback response
            return {
                'principal_findings': [{
                    'bullet_point': response_content[:300] + "..." if len(response_content) > 300 else response_content,
                    'reasoning': "JSON parsing failed, using raw response",
                    'data_source': ["AI Analysis"],
                    'confidence': "low"
                }],
                'pca_insights': {},
                'executive_summary': response_content[:500] + "..." if len(response_content) > 500 else response_content
            }

    async def test_model_availability(self) -> Dict[str, bool]:
        """
        Test which models are currently available.
        
        Returns:
            Dictionary mapping model names to availability status
        """
        availability = {}
        test_prompt = "Respond with 'OK' to confirm availability."
        
        for model in self.config['models']:
            try:
                result = await self._call_model(test_prompt, model, 'en')
                availability[model] = True
            except Exception as e:
                logging.warning(f"Model {model} unavailable: {e}")
                availability[model] = False
        
        return availability

    def calculate_cost(self, tokens: int, model: str) -> float:
        """
        Calculate API cost for request.
        
        Args:
            tokens: Number of tokens processed
            model: Model name
            
        Returns:
            Estimated cost in USD
        """
        model_config = self.model_configs.get(model)
        if not model_config:
            return 0.0
        
        return (tokens / 1000) * model_config.cost_per_1k_tokens

    def _log_performance(self, model: str, response_time_ms: int, 
                        token_count: int, success: bool, error_message: str = None):
        """
        Log model performance for monitoring.
        
        Args:
            model: Model name
            response_time_ms: Response time in milliseconds
            token_count: Number of tokens processed
            success: Whether request was successful
            error_message: Error message if failed
        """
        if model not in self.performance_stats:
            self.performance_stats[model] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_response_time_ms': 0,
                'total_tokens': 0,
                'avg_response_time_ms': 0,
                'success_rate': 0
            }
        
        stats = self.performance_stats[model]
        stats['total_requests'] += 1
        stats['total_response_time_ms'] += response_time_ms
        stats['total_tokens'] += token_count
        
        if success:
            stats['successful_requests'] += 1
        else:
            stats['failed_requests'] += 1
        
        # Update averages
        stats['avg_response_time_ms'] = stats['total_response_time_ms'] / stats['total_requests']
        stats['success_rate'] = (stats['successful_requests'] / stats['total_requests']) * 100
        
        logging.info(f"Model {model} performance: {response_time_ms}ms, {token_count} tokens, "
                    f"success: {success}, success_rate: {stats['success_rate']:.1f}%")

    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance statistics for all models.
        
        Returns:
            Dictionary with performance stats for each model
        """
        return self.performance_stats.copy()

    def reset_performance_stats(self):
        """Reset performance statistics."""
        self.performance_stats.clear()

# Global service instance
_openrouter_service = None

def get_openrouter_service(api_key: str = None, config: Dict[str, Any] = None) -> OpenRouterService:
    """
    Get or create global OpenRouter service instance.
    
    Args:
        api_key: OpenRouter API key (optional if already set)
        config: Configuration dictionary (optional)
        
    Returns:
        OpenRouter service instance
    """
    global _openrouter_service
    
    if _openrouter_service is None:
        if not api_key:
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                raise ValueError("OpenRouter API key not provided")
        
        _openrouter_service = OpenRouterService(api_key, config)
    
    return _openrouter_service

def reset_openrouter_service():
    """Reset global OpenRouter service instance."""
    global _openrouter_service
    _openrouter_service = None