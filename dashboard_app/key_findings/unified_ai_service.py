"""
Unified AI Service with Groq Primary and OpenRouter Fallback

Handles AI model interactions with multiple providers:
- Primary: Groq with specified models
- Fallback: OpenRouter with existing models

Provides robust AI analysis with provider switching, retry logic,
and performance monitoring.
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
    provider: str  # 'groq' or 'openrouter'
    max_tokens: int
    temperature: float
    timeout: int = 30
    cost_per_1k_tokens: float = 0.001

class UnifiedAIService:
    """
    Unified service for interacting with multiple AI providers.
    
    Primary provider: Groq
    Fallback provider: OpenRouter
    
    Provides robust AI analysis with multiple model options, retry logic,
    and performance monitoring.
    """

    def __init__(self, groq_api_key: str = None, openrouter_api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize Unified AI service.
        
        Args:
            groq_api_key: Groq API key
            openrouter_api_key: OpenRouter API key
            config: Configuration dictionary with model settings
        """
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        self.openrouter_api_key = openrouter_api_key or os.getenv('OPENROUTER_API_KEY')
        
        # Base URLs
        self.groq_base_url = "https://api.groq.com/openai/v1"
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        
        # Default configuration
        default_config = {
            'primary_provider': 'groq',
            'fallback_provider': 'openrouter',
            'timeout': 15,
            'max_retries': 2,
            'retry_delay': 0.5,
            'max_tokens': 4000,
            'temperature': 0.7
        }
        
        # Merge with provided config
        self.config = {**default_config, **(config or {})}
        
        # Groq models (primary) - optimized based on comparison test results
        # Order: fastest + highest quality → slower alternatives
        self.groq_models = [
            'meta-llama/llama-4-scout-17b-16e-instruct',  # Fastest (1.6s) + highest quality (0.97)
            'llama-3.3-70b-versatile',                  # Good speed (2.9s) + highest quality (0.97)
            'moonshotai/kimi-k2-instruct',              # Good quality (0.97) + moderate speed (3.5s)
            'openai/gpt-oss-120b'                       # Slowest (4.7s) + good quality (0.94)
        ]
        
        # OpenRouter models (fallback)
        self.openrouter_models = [
            'nvidia/nemotron-nano-9b-v2:free',
            'openai/gpt-oss-20b:free',
            'mistralai/mistral-small-3.2-24b-instruct:free',
            'cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
            'google/gemma-3-27b-it:free'
        ]
        
        # Model configurations
        self.model_configs = {
            # Groq models
            'openai/gpt-oss-120b': AIModelConfig(
                name='openai/gpt-oss-120b',
                provider='groq',
                max_tokens=4000,
                temperature=0.7,
                timeout=12,
                cost_per_1k_tokens=0.0
            ),
            'meta-llama/llama-4-scout-17b-16e-instruct': AIModelConfig(
                name='meta-llama/llama-4-scout-17b-16e-instruct',
                provider='groq',
                max_tokens=4000,
                temperature=0.7,
                timeout=10,
                cost_per_1k_tokens=0.0
            ),
            'llama-3.3-70b-versatile': AIModelConfig(
                name='llama-3.3-70b-versatile',
                provider='groq',
                max_tokens=4000,
                temperature=0.7,
                timeout=15,
                cost_per_1k_tokens=0.0
            ),
            'moonshotai/kimi-k2-instruct': AIModelConfig(
                name='moonshotai/kimi-k2-instruct',
                provider='groq',
                max_tokens=4000,
                temperature=0.7,
                timeout=12,
                cost_per_1k_tokens=0.0
            ),
            # OpenRouter models
            'nvidia/nemotron-nano-9b-v2:free': AIModelConfig(
                name='nvidia/nemotron-nano-9b-v2:free',
                provider='openrouter',
                max_tokens=2000,
                temperature=0.7,
                timeout=6,
                cost_per_1k_tokens=0.0
            ),
            'openai/gpt-oss-20b:free': AIModelConfig(
                name='openai/gpt-oss-20b:free',
                provider='openrouter',
                max_tokens=2000,
                temperature=0.7,
                timeout=8,
                cost_per_1k_tokens=0.0
            ),
            'mistralai/mistral-small-3.2-24b-instruct:free': AIModelConfig(
                name='mistralai/mistral-small-3.2-24b-instruct:free',
                provider='openrouter',
                max_tokens=2000,
                temperature=0.7,
                timeout=8,
                cost_per_1k_tokens=0.0
            ),
            'cognitivecomputations/dolphin-mistral-24b-venice-edition:free': AIModelConfig(
                name='cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
                provider='openrouter',
                max_tokens=2000,
                temperature=0.7,
                timeout=10,
                cost_per_1k_tokens=0.0
            ),
            'google/gemma-3-27b-it:free': AIModelConfig(
                name='google/gemma-3-27b-it:free',
                provider='openrouter',
                max_tokens=2000,
                temperature=0.7,
                timeout=12,
                cost_per_1k_tokens=0.0
            )
        }
        
        # Performance tracking
        self.performance_stats = {}

    async def generate_analysis(self, prompt: str, model: str = None,
                               language: str = 'es') -> Dict[str, Any]:
        """
        Generate AI analysis with provider fallback.

        Args:
            prompt: Analysis prompt for the AI
            model: Specific model to use (optional)
            language: Analysis language ('es' or 'en')

        Returns:
            Dictionary containing analysis results and metadata
        """
        start_time = time.time()
        logging.info(f"🚀 Starting AI analysis generation - prompt length: {len(prompt)} characters")
        
        # Determine provider and model order
        if model and model in self.model_configs:
            model_config = self.model_configs[model]
            if model_config.provider == 'groq':
                providers_to_try = [('groq', [model] + [m for m in self.groq_models if m != model])]
                providers_to_try.append(('openrouter', self.openrouter_models))
            else:
                providers_to_try = [('openrouter', [model] + [m for m in self.openrouter_models if m != model])]
        else:
            # Default: try Groq first, then OpenRouter
            providers_to_try = [
                ('groq', self.groq_models),
                ('openrouter', self.openrouter_models)
            ]
        
        last_error = None
        successful_provider = None
        successful_model = None
        response_content = None
        token_count = 0
        
        # Show prompt details before starting
        prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
        logging.info(f"📝 Prompt preview: {prompt_preview}")

        # Try each provider and models in order
        for provider_idx, (provider, models_to_try) in enumerate(providers_to_try):
            logging.info(f"🔄 Trying provider: {provider} (attempt {provider_idx + 1}/{len(providers_to_try)})")
            
            # Check if API key is available for this provider
            if provider == 'groq' and not self.groq_api_key:
                logging.warning("⚠️ Groq API key not available, skipping to next provider")
                continue
            elif provider == 'openrouter' and not self.openrouter_api_key:
                logging.warning("⚠️ OpenRouter API key not available, skipping to next provider")
                continue
            
            for i, attempt_model in enumerate(models_to_try):
                model_start_time = time.time()
                logging.info(f"🔄 Attempting analysis with model: {attempt_model} (attempt {i+1}/{len(models_to_try)})")

                try:
                    logging.info(f"📡 Sending request to {provider}/{attempt_model}...")
                    result = await self._call_model(prompt, attempt_model, provider, language)

                    if result and 'choices' in result and len(result['choices']) > 0:
                        response_content = result['choices'][0]['message']['content']
                        token_count = result.get('usage', {}).get('total_tokens', 0)
                        successful_provider = provider
                        successful_model = attempt_model
                        model_time = time.time() - model_start_time

                        # Show response preview
                        response_preview = response_content[:100] + "..." if len(response_content) > 100 else response_content
                        logging.info(f"✅ Model {attempt_model} ({provider}) succeeded in {model_time:.2f}s with {token_count} tokens")
                        logging.info(f"📥 Response preview: {response_preview}")
                        break
                    else:
                        model_time = time.time() - model_start_time
                        logging.warning(f"⚠️ Model {attempt_model} ({provider}) returned invalid response after {model_time:.2f}s")

                except Exception as e:
                    model_time = time.time() - model_start_time
                    last_error = e
                    logging.warning(f"❌ Model {attempt_model} ({provider}) failed after {model_time:.2f}s: {e}")
                    continue
            
            # If we got a successful response from this provider, break
            if successful_provider:
                break
        
        # Calculate performance metrics
        response_time_ms = int((time.time() - start_time) * 1000)
        success = response_content is not None
        
        # Log performance
        self._log_performance(successful_model or "unknown", response_time_ms, 
                            token_count, success, str(last_error) if last_error else None)
        
        if not success:
            raise Exception(f"All providers and models failed. Last error: {last_error}")
        
        # Parse and validate response
        logging.info(f"🔍 Parsing AI response from {successful_model} ({successful_provider}) ({len(response_content)} characters)")
        try:
            parsed_response = self._parse_ai_response(response_content)
            logging.info(f"✅ Response parsed successfully - findings: {len(parsed_response.get('principal_findings', []))}")
        except Exception as e:
            logging.error(f"❌ Failed to parse AI response: {e}")
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
            'provider_used': successful_provider,
            'response_time_ms': response_time_ms,
            'token_count': token_count,
            'success': success,
            'language': language
        }

    async def _call_model(self, prompt: str, model: str, provider: str, language: str) -> Dict[str, Any]:
        """
        Call specific AI model with retry logic.

        Args:
            prompt: Analysis prompt
            model: Model name
            provider: Provider name ('groq' or 'openrouter')
            language: Analysis language

        Returns:
            Raw API response
        """
        model_config = self.model_configs.get(model)
        if not model_config:
            raise ValueError(f"Model configuration not found for {model}")
        
        logging.info(f"📡 Calling model {model} via {provider} with timeout {model_config.timeout}s and {model_config.max_tokens} max tokens")
        
        # Set up headers and payload based on provider
        if provider == 'groq':
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            base_url = self.groq_base_url
        else:  # openrouter
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://management-tools-analysis.com",
                "X-Title": "Management Tools Analysis Dashboard"
            }
            base_url = self.openrouter_base_url
        
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
            "top_p": 0.9
        }
        
        # Show request details
        logging.info(f"📤 API Request: {model} -> {base_url}/chat/completions")
        logging.info(f"📊 Payload: model={payload['model']}, max_tokens={payload['max_tokens']}, temp={payload['temperature']}")

        # Retry logic
        for attempt in range(self.config['max_retries']):
            request_start = time.time()
            try:
                timeout = aiohttp.ClientTimeout(total=model_config.timeout)
                logging.info(f"⏱️ Attempt {attempt + 1}/{self.config['max_retries']} for {model} via {provider} (timeout: {model_config.timeout}s)")

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:
                        request_time = time.time() - request_start
                        logging.info(f"🌐 HTTP {response.status} in {request_time:.2f}s for {model} via {provider}")

                        if response.status == 200:
                            response_start = time.time()
                            result = await response.json()
                            response_time = time.time() - response_start
                            logging.info(f"📥 JSON parsed in {response_time:.2f}s for {model} via {provider}")
                            return result
                        elif response.status == 429:
                            # Rate limited
                            logging.warning(f"🚦 Rate limited for {model} via {provider}, waiting {self.config['retry_delay']}s")
                            await asyncio.sleep(self.config['retry_delay'])
                            continue
                        else:
                            error_text = await response.text()
                            logging.error(f"❌ API error {response.status} for {model} via {provider}: {error_text}")
                            raise Exception(f"API error {response.status}: {error_text}")

            except asyncio.TimeoutError:
                request_time = time.time() - request_start
                logging.warning(f"⏰ Timeout for model {model} via {provider} after {request_time:.2f}s (attempt {attempt + 1})")
                if attempt < self.config['max_retries'] - 1:
                    await asyncio.sleep(self.config['retry_delay'])
                    continue
                else:
                    raise
            except Exception as e:
                request_time = time.time() - request_start
                logging.error(f"💥 Exception for {model} via {provider} after {request_time:.2f}s (attempt {attempt + 1}): {e}")
                if attempt < self.config['max_retries'] - 1:
                    await asyncio.sleep(self.config['retry_delay'])
                    continue
                else:
                    raise
        
        raise Exception(f"Model {model} via {provider} failed after {self.config['max_retries']} attempts")

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

INSTRUCCIÓN IMPORTANTE: Menciona explícitamente el nombre de la herramienta de gestión analizada en tu respuesta.
Usa el nombre de la herramienta proporcionado en el contexto del análisis para personalizar tus hallazgos.

Proporciona análisis que:
1. Sinteticen información de múltiples fuentes de datos
2. Identifiquen patrones temporales y tendencias significativas
3. Destaquen insights de PCA con explicaciones claras
4. Generen conclusiones ejecutivas accionables
5. Mantengan rigor académico doctoral
6. Mencionen específicamente el nombre de la herramienta de gestión en el análisis

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

IMPORTANT INSTRUCTION: Explicitly mention the name of the management tool being analyzed in your response.
Use the tool name provided in the analysis context to personalize your findings.

Provide analysis that:
1. Synthesizes information from multiple data sources
2. Identifies temporal patterns and significant trends
3. Highlights PCA insights with clear explanations
4. Generates actionable executive conclusions
5. Maintains doctoral academic rigor
6. Specifically mentions the management tool name in the analysis

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
            # Strip markdown code block formatting first
            cleaned_content = response_content.strip()

            # Remove markdown code blocks (```json ... ```)
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]  # Remove ```json
            if cleaned_content.startswith('```'):
                cleaned_content = cleaned_content[3:]  # Remove ```
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]  # Remove trailing ```

            # Clean up any remaining whitespace
            cleaned_content = cleaned_content.strip()

            # Try to extract JSON from response
            start_idx = cleaned_content.find('{')
            end_idx = cleaned_content.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = cleaned_content[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Handle new JSON structure with direct fields
                if 'pca_analysis' in parsed and isinstance(parsed['pca_analysis'], str):
                    # New structure detected, convert to expected format
                    result = {
                        'principal_findings': parsed.get('principal_findings', []),
                        'pca_insights': {'analysis': parsed.get('pca_analysis', '')},
                        'executive_summary': parsed.get('executive_summary', ''),
                        # Keep original fields for direct access
                        'pca_analysis': parsed.get('pca_analysis', ''),
                        'original_structure': 'new'
                    }
                    
                    # Convert principal_findings to array of objects if it's a simple array
                    if isinstance(result['principal_findings'], list) and result['principal_findings']:
                        if isinstance(result['principal_findings'][0], str):
                            # Convert string array to object array
                            result['principal_findings'] = [
                                {
                                    'bullet_point': item,
                                    'reasoning': "Generated by AI",
                                    'data_source': ["AI Analysis"],
                                    'confidence': "medium"
                                }
                                for item in result['principal_findings']
                            ]
                    
                    return result
                else:
                    # Handle old structure
                    if 'principal_findings' not in parsed:
                        parsed['principal_findings'] = []
                    if 'pca_insights' not in parsed:
                        parsed['pca_insights'] = {}
                    if 'executive_summary' not in parsed:
                        parsed['executive_summary'] = ""
                    
                    parsed['original_structure'] = 'old'
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
                    'pca_insights': {'analysis': response_content[:400] + "..." if len(response_content) > 400 else response_content},
                    'executive_summary': response_content[:500] + "..." if len(response_content) > 500 else response_content,
                    'pca_analysis': response_content[:400] + "..." if len(response_content) > 400 else response_content,
                    'original_structure': 'fallback'
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
                'pca_insights': {'analysis': response_content[:400] + "..." if len(response_content) > 400 else response_content},
                'executive_summary': response_content[:500] + "..." if len(response_content) > 500 else response_content,
                'pca_analysis': response_content[:400] + "..." if len(response_content) > 400 else response_content,
                'original_structure': 'error'
            }

    async def test_model_availability(self) -> Dict[str, bool]:
        """
        Test which models are currently available across all providers.

        Returns:
            Dictionary mapping model names to availability status
        """
        availability = {}
        test_prompt = "Respond with 'OK' to confirm availability."

        # Test Groq models
        if self.groq_api_key:
            for model in self.groq_models:
                try:
                    result = await self._call_model(test_prompt, model, 'groq', 'en')
                    availability[model] = True
                    logging.info(f"✅ Groq model {model} is available and working")
                except Exception as e:
                    logging.warning(f"❌ Groq model {model} unavailable: {e}")
                    availability[model] = False
        else:
            logging.warning("⚠️ Groq API key not configured, skipping Groq models")
            for model in self.groq_models:
                availability[model] = False

        # Test OpenRouter models
        if self.openrouter_api_key:
            for model in self.openrouter_models:
                try:
                    result = await self._call_model(test_prompt, model, 'openrouter', 'en')
                    availability[model] = True
                    logging.info(f"✅ OpenRouter model {model} is available and working")
                except Exception as e:
                    logging.warning(f"❌ OpenRouter model {model} unavailable: {e}")
                    availability[model] = False
        else:
            logging.warning("⚠️ OpenRouter API key not configured, skipping OpenRouter models")
            for model in self.openrouter_models:
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
_unified_ai_service = None

def get_unified_ai_service(groq_api_key: str = None, openrouter_api_key: str = None, config: Dict[str, Any] = None) -> UnifiedAIService:
    """
    Get or create global Unified AI service instance.
    
    Args:
        groq_api_key: Groq API key (optional if already set)
        openrouter_api_key: OpenRouter API key (optional if already set)
        config: Configuration dictionary (optional)
        
    Returns:
        Unified AI service instance
    """
    global _unified_ai_service
    
    if _unified_ai_service is None:
        _unified_ai_service = UnifiedAIService(groq_api_key, openrouter_api_key, config)
    
    return _unified_ai_service

def reset_unified_ai_service():
    """Reset global Unified AI service instance."""
    global _unified_ai_service
    _unified_ai_service = None
