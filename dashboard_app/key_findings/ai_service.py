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
import re
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
        
        # Default configuration - only available models, optimized for speed
        default_config = {
            'models': [
                'nvidia/nemotron-nano-9b-v2:free',
                'openai/gpt-oss-20b:free',
                'mistralai/mistral-small-3.2-24b-instruct:free',
                'cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
                'google/gemma-3-27b-it:free'
            ],
            'timeout': 8,  # Aggressive timeout for faster responses
            'max_retries': 1,  # Minimal retries for speed
            'retry_delay': 0.1,  # Very fast retries
            'max_tokens': 1500,  # Reduced for faster generation
            'temperature': 0.7
        }
        
        # Merge with provided config
        self.config = {**default_config, **(config or {})}
        
        # Model configurations - only available models, optimized for speed
        self.model_configs = {
            'nvidia/nemotron-nano-9b-v2:free': AIModelConfig(
                name='nvidia/nemotron-nano-9b-v2:free',
                max_tokens=2000,
                temperature=0.7,
                timeout=6,  # Very fast timeout
                cost_per_1k_tokens=0.0
            ),
            'openai/gpt-oss-20b:free': AIModelConfig(
                name='openai/gpt-oss-20b:free',
                max_tokens=2000,
                temperature=0.7,
                timeout=8,
                cost_per_1k_tokens=0.0
            ),
            'mistralai/mistral-small-3.2-24b-instruct:free': AIModelConfig(
                name='mistralai/mistral-small-3.2-24b-instruct:free',
                max_tokens=2000,
                temperature=0.7,
                timeout=8,  # Good balance of speed and capability
                cost_per_1k_tokens=0.0
            ),
            'cognitivecomputations/dolphin-mistral-24b-venice-edition:free': AIModelConfig(
                name='cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
                max_tokens=2000,
                temperature=0.7,
                timeout=10,
                cost_per_1k_tokens=0.0
            ),
            'google/gemma-3-27b-it:free': AIModelConfig(
                name='google/gemma-3-27b-it:free',
                max_tokens=2000,
                temperature=0.7,
                timeout=12,  # Largest model, slightly longer timeout
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
        logging.info(f"🚀 Starting AI analysis generation - prompt length: {len(prompt)} characters")
        
        # Determine model order
        if model and model in self.config['models']:
            models_to_try = [model] + [m for m in self.config['models'] if m != model]
        else:
            models_to_try = self.config['models']
        
        last_error = None
        successful_model = None
        response_content = None
        token_count = 0
        
        # Show prompt details before starting
        prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
        logging.info(f"📝 Prompt preview: {prompt_preview}")

        # Try each model in order
        for i, attempt_model in enumerate(models_to_try):
            model_start_time = time.time()
            logging.info(f"🔄 Attempting analysis with model: {attempt_model} (attempt {i+1}/{len(models_to_try)})")

            try:
                logging.info(f"📡 Sending request to {attempt_model}...")
                result = await self._call_model(prompt, attempt_model, language)

                if result and 'choices' in result and len(result['choices']) > 0:
                    response_content = result['choices'][0]['message']['content']
                    token_count = result.get('usage', {}).get('total_tokens', 0)
                    successful_model = attempt_model
                    model_time = time.time() - model_start_time

                    # Show response preview
                    response_preview = response_content[:100] + "..." if len(response_content) > 100 else response_content
                    logging.info(f"✅ Model {attempt_model} succeeded in {model_time:.2f}s with {token_count} tokens")
                    logging.info(f"📥 Response preview: {response_preview}")
                    break
                else:
                    model_time = time.time() - model_start_time
                    logging.warning(f"⚠️ Model {attempt_model} returned invalid response after {model_time:.2f}s")

            except Exception as e:
                model_time = time.time() - model_start_time
                last_error = e
                logging.warning(f"❌ Model {attempt_model} failed after {model_time:.2f}s: {e}")
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
        logging.info(f"🔍 Parsing AI response from {successful_model} ({len(response_content)} characters)")
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
        logging.info(f"📡 Calling model {model} with timeout {model_config.timeout}s and {model_config.max_tokens} max tokens")
        
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
            "top_p": 0.9
            # Removed frequency_penalty and presence_penalty for faster processing
        }
        
        # Show request details
        logging.info(f"📤 API Request: {model} -> {self.base_url}/chat/completions")
        logging.info(f"📊 Payload: model={payload['model']}, max_tokens={payload['max_tokens']}, temp={payload['temperature']}")

        # Optimized retry logic for faster responses
        for attempt in range(self.config['max_retries']):
            request_start = time.time()
            try:
                timeout = aiohttp.ClientTimeout(total=model_config.timeout)
                logging.info(f"⏱️ Attempt {attempt + 1}/{self.config['max_retries']} for {model} (timeout: {model_config.timeout}s)")

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:
                        request_time = time.time() - request_start
                        logging.info(f"🌐 HTTP {response.status} in {request_time:.2f}s for {model}")

                        if response.status == 200:
                            response_start = time.time()
                            result = await response.json()
                            response_time = time.time() - response_start
                            logging.info(f"📥 JSON parsed in {response_time:.2f}s for {model}")
                            return result
                        elif response.status == 429:
                            # Rate limited - minimal wait and retry
                            logging.warning(f"🚦 Rate limited for {model}, waiting {self.config['retry_delay']}s")
                            await asyncio.sleep(self.config['retry_delay'])
                            continue
                        else:
                            error_text = await response.text()
                            logging.error(f"❌ API error {response.status} for {model}: {error_text}")
                            raise Exception(f"API error {response.status}: {error_text}")

            except asyncio.TimeoutError:
                request_time = time.time() - request_start
                logging.warning(f"⏰ Timeout for model {model} after {request_time:.2f}s (attempt {attempt + 1})")
                if attempt < self.config['max_retries'] - 1:
                    await asyncio.sleep(self.config['retry_delay'])
                    continue
                else:
                    raise
            except Exception as e:
                request_time = time.time() - request_start
                logging.error(f"💥 Exception for {model} after {request_time:.2f}s (attempt {attempt + 1}): {e}")
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
        Parse and validate AI response, handling multiple formats including markdown sections.

        Args:
            response_content: Raw AI response content

        Returns:
            Parsed response dictionary
        """
        try:
            # First, try to parse as pure JSON
            cleaned_content = response_content.strip()

            # Remove markdown code blocks if present
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]  # Remove ```json
            if cleaned_content.startswith('```'):
                cleaned_content = cleaned_content[3:]  # Remove ```
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]  # Remove trailing ```

            cleaned_content = cleaned_content.strip()

            # Try direct JSON parsing first
            if cleaned_content.startswith('{') and cleaned_content.endswith('}'):
                try:
                    parsed = json.loads(cleaned_content)
                    return self._normalize_parsed_response(parsed)
                except json.JSONDecodeError:
                    pass

            # Handle specific malformed patterns from the key findings report
            # Pattern 1: JSON that gets cut off mid-principal_findings array
            if self._is_incomplete_json_pattern(cleaned_content):
                fixed_response = self._fix_incomplete_json_pattern(cleaned_content)
                if fixed_response:
                    return fixed_response

            # Pattern 2: Bullet point containing JSON fragment
            if self._is_bullet_with_json_pattern(cleaned_content):
                extracted_response = self._extract_from_bullet_json_pattern(cleaned_content)
                if extracted_response:
                    return extracted_response

            # If direct parsing fails, try to extract from markdown sections
            sections = self._extract_markdown_sections(response_content)

            if sections:
                # Try to combine sections into a complete response
                combined_response = self._combine_section_responses(sections)
                if combined_response:
                    return combined_response

            # Fallback: extract JSON fragments from the entire response
            json_fragments = self._extract_json_fragments(response_content)
            if json_fragments:
                combined = self._combine_json_fragments(json_fragments)
                if combined:
                    return combined

            # Final fallback: create structured response from text
            return self._create_fallback_response(response_content)

        except Exception as e:
            logging.error(f"Response parsing failed: {e}")
            return self._create_fallback_response(response_content)

    def _normalize_parsed_response(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parsed response to expected format.

        Args:
            parsed: Raw parsed JSON

        Returns:
            Normalized response dictionary
        """
        result = {
            'executive_summary': parsed.get('executive_summary', ''),
            'principal_findings': parsed.get('principal_findings', []),
            'pca_insights': parsed.get('pca_insights', {}),
            'original_structure': 'direct_json'
        }

        # Handle pca_analysis field
        if 'pca_analysis' in parsed:
            result['pca_analysis'] = parsed['pca_analysis']
            result['pca_insights'] = {'analysis': parsed['pca_analysis']}

        # Ensure principal_findings is in correct format
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

    def _is_incomplete_json_pattern(self, content: str) -> bool:
        """
        Check if content matches the incomplete JSON pattern from key findings report.

        Args:
            content: Content to check

        Returns:
            True if matches incomplete JSON pattern
        """
        return (
            content.startswith('{"executive_summary":') and
            '"principal_findings":' in content and
            ('"•' in content or content.count('"') % 2 == 1) and
            not content.strip().endswith('}')
        )

    def _fix_incomplete_json_pattern(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Fix incomplete JSON pattern by completing the structure.

        Args:
            content: Incomplete JSON content

        Returns:
            Fixed response dictionary or None
        """
        try:
            # Extract executive summary
            exec_summary_match = re.search(r'"executive_summary":\s*"([^"]*(?:\\.[^"]*)*)"', content)
            if not exec_summary_match:
                return None

            executive_summary = exec_summary_match.group(1).replace('\\"', '"')

            # Look for the start of principal_findings
            pf_start = content.find('"principal_findings":')
            if pf_start == -1:
                return None

            # Extract everything after principal_findings as a truncated finding
            pf_content_start = content.find('[', pf_start)
            if pf_content_start == -1:
                return None

            # Find the actual finding content (after the opening bracket)
            finding_start = pf_content_start + 1
            remaining_content = content[finding_start:].strip()

            # Clean up the finding content
            if remaining_content.startswith('"•'):
                # Remove the opening quote and bullet point
                finding_content = remaining_content[2:].strip()
                # Remove trailing quote and comma if present
                if finding_content.endswith('",'):
                    finding_content = finding_content[:-2]
                elif finding_content.endswith('"'):
                    finding_content = finding_content[:-1]

                # Create the finding object
                principal_findings = [{
                    'bullet_point': finding_content.replace('\\"', '"'),
                    'reasoning': 'Extracted from truncated AI response',
                    'data_source': ['AI Analysis'],
                    'confidence': 'low'
                }]
            else:
                # Fallback: use the remaining content as a finding
                principal_findings = [{
                    'bullet_point': remaining_content.replace('\\"', '"').strip('"'),
                    'reasoning': 'Extracted from truncated AI response',
                    'data_source': ['AI Analysis'],
                    'confidence': 'low'
                }]

            return {
                'executive_summary': executive_summary,
                'principal_findings': principal_findings,
                'pca_insights': {},
                'original_structure': 'incomplete_json_fixed'
            }

        except Exception as e:
            logging.error(f"Failed to fix incomplete JSON pattern: {e}")
            return None

    def _is_bullet_with_json_pattern(self, content: str) -> bool:
        """
        Check if content matches bullet point with JSON fragment pattern.

        Args:
            content: Content to check

        Returns:
            True if matches bullet + JSON pattern
        """
        content_str = str(content)
        return (
            content_str.strip().startswith('•') and
            '"executive_summary":' in content_str
        )

    def _extract_from_bullet_json_pattern(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract content from bullet point containing JSON fragment.

        Args:
            content: Bullet point with JSON content

        Returns:
            Extracted response dictionary or None
        """
        try:
            # Remove the bullet point marker and clean up
            json_content = content.strip()[1:].strip()

            # If it starts with a quote, remove it
            if json_content.startswith('"'):
                json_content = json_content[1:]
            if json_content.endswith('"'):
                json_content = json_content[:-1]

            # Try to parse as JSON
            if json_content.startswith('{'):
                try:
                    parsed = json.loads(json_content)
                    return self._normalize_parsed_response(parsed)
                except json.JSONDecodeError as e:
                    logging.warning(f"JSON parsing failed for bullet content: {e}")
                    # Try to fix common JSON issues
                    if not json_content.endswith('}'):
                        json_content += '}'
                    if not json_content.endswith('"'):
                        json_content += '"'

                    try:
                        parsed = json.loads(json_content)
                        return self._normalize_parsed_response(parsed)
                    except json.JSONDecodeError:
                        pass

            # If JSON parsing fails, extract components manually
            # Try to find executive summary with more flexible pattern
            exec_summary_match = re.search(r'"executive_summary":\s*"(.*?)"', json_content, re.DOTALL)
            if exec_summary_match:
                executive_summary = exec_summary_match.group(1).replace('\\"', '"')

                return {
                    'executive_summary': executive_summary,
                    'principal_findings': [{
                        'bullet_point': 'Analysis extracted from malformed response',
                        'reasoning': 'Content extracted from bullet point with JSON fragment',
                        'data_source': ['AI Analysis'],
                        'confidence': 'low'
                    }],
                    'pca_insights': {},
                    'original_structure': 'bullet_json_pattern'
                }

            # If that doesn't work, try an even more flexible approach
            # Look for the text after "executive_summary":"
            exec_summary_start = json_content.find('"executive_summary":')
            if exec_summary_start != -1:
                start_pos = json_content.find('"', exec_summary_start + 20)
                if start_pos != -1:
                    # Find the next quote (end of executive summary)
                    end_pos = json_content.find('"', start_pos + 1)
                    if end_pos != -1:
                        executive_summary = json_content[start_pos + 1:end_pos].replace('\\"', '"')

                        return {
                            'executive_summary': executive_summary,
                            'principal_findings': [{
                                'bullet_point': 'Analysis extracted from malformed response',
                                'reasoning': 'Content extracted from bullet point with JSON fragment',
                                'data_source': ['AI Analysis'],
                                'confidence': 'low'
                            }],
                            'pca_insights': {},
                            'original_structure': 'bullet_json_pattern'
                        }

        except Exception as e:
            logging.error(f"Failed to extract from bullet JSON pattern: {e}")

        return None

    def _extract_markdown_sections(self, content: str) -> Dict[str, str]:
        """
        Extract content from markdown sections with emoji headers, handling malformed responses.

        Args:
            content: Raw response content

        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}

        # Define section patterns (Spanish and English)
        section_patterns = {
            'executive_summary': [
                '📋 Resumen Ejecutivo',
                '📋 Executive Summary',
                'Resumen Ejecutivo',
                'Executive Summary'
            ],
            'principal_findings': [
                '🔍 Hallazgos Principales',
                '🔍 Principal Findings',
                'Hallazgos Principales',
                'Principal Findings'
            ],
            'pca_analysis': [
                '📊 Análisis PCA',
                '📊 PCA Analysis',
                'Análisis PCA',
                'PCA Analysis'
            ]
        }

        lines = content.split('\n')
        current_section = None
        section_content = []

        for line in lines:
            line = line.strip()

            # Check if this line starts a new section
            section_started = False
            for section_key, patterns in section_patterns.items():
                if any(pattern in line for pattern in patterns):
                    # Save previous section if exists
                    if current_section and section_content:
                        sections[current_section] = '\n'.join(section_content).strip()
                        section_content = []

                    current_section = section_key
                    section_content = []
                    section_started = True
                    break

            if not section_started and current_section:
                # Continue accumulating content for current section
                section_content.append(line)

        # Save the last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content).strip()

        return sections

    def _combine_section_responses(self, sections: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Combine content from different sections into a complete response, handling malformed sections.

        Args:
            sections: Dictionary of section content

        Returns:
            Combined response dictionary or None if unsuccessful
        """
        result = {}

        # First pass: extract executive summary (usually the most reliable)
        if 'executive_summary' in sections:
            section_content = sections['executive_summary']
            json_content = self._extract_json_from_section(section_content)
            if json_content and 'executive_summary' in json_content:
                result['executive_summary'] = json_content['executive_summary']
            else:
                # Try direct extraction - look for the complete summary
                summary_start = section_content.find('"executive_summary":')
                if summary_start != -1:
                    summary_start += len('"executive_summary":')
                    # Skip whitespace and quotes
                    while summary_start < len(section_content) and section_content[summary_start] in [' ', '"', '\n']:
                        summary_start += 1

                    # Find the end of the summary (before next field or end)
                    summary_end = section_content.find('", "principal_findings"', summary_start)
                    if summary_end == -1:
                        summary_end = section_content.find('",', summary_start)
                    if summary_end == -1:
                        summary_end = len(section_content)

                    if summary_end > summary_start:
                        summary = section_content[summary_start:summary_end].strip()
                        # Clean up escaped quotes
                        summary = summary.replace('\\"', '"')
                        result['executive_summary'] = summary

        # Second pass: handle principal findings (often malformed)
        if 'principal_findings' in sections:
            section_content = sections['principal_findings']
            json_content = self._extract_json_from_section(section_content)

            if json_content and 'principal_findings' in json_content:
                result['principal_findings'] = json_content['principal_findings']
            else:
                # The principal findings section is completely malformed
                # Look for any actual bullet points that aren't JSON fragments
                lines = section_content.split('\n')
                actual_findings = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('•') and len(line) > 2:
                        bullet_content = line[1:].strip()
                        # Skip if it's just JSON fragments, markdown, or repeated executive summary
                        if (not bullet_content.startswith('{') and
                            not bullet_content.startswith('"executive_summary":') and
                            not bullet_content.startswith('```') and
                            not bullet_content == '{' and
                            not bullet_content.startswith('"•') and  # Avoid nested bullet points
                            len(bullet_content) > 10):  # Must be substantial content
                            actual_findings.append({
                                'bullet_point': bullet_content,
                                'reasoning': 'Extracted from malformed AI response',
                                'data_source': ['AI Analysis'],
                                'confidence': 'low'
                            })

                # NEW: Also check for bullet points that contain JSON fragments
                for line in lines:
                    line = line.strip()
                    if line.startswith('•') and '"executive_summary":' in line:
                        # This is a bullet point containing JSON - extract it
                        extracted = self._extract_from_bullet_json_pattern(line)
                        if extracted and extracted.get('principal_findings'):
                            actual_findings.extend(extracted['principal_findings'])

                if actual_findings:
                    result['principal_findings'] = actual_findings

        # Third pass: handle PCA analysis (often contains repeated executive summary)
        if 'pca_analysis' in sections:
            section_content = sections['pca_analysis']
            json_content = self._extract_json_from_section(section_content)

            if json_content and 'pca_analysis' in json_content:
                result['pca_analysis'] = json_content['pca_analysis']
                result['pca_insights'] = {'analysis': json_content['pca_analysis']}
            else:
                # Extract PCA content, filtering out repeated executive summary
                pca_content = self._extract_pca_content(section_content)
                if pca_content:
                    # Remove repeated executive summary content if present
                    if '"executive_summary":' in pca_content:
                        # Try to extract only the PCA-specific content
                        lines = pca_content.split('\n')
                        pca_lines = []
                        in_pca_content = False
                        for line in lines:
                            if 'Análisis adicional no disponible' in line:
                                break
                            if not line.strip().startswith('"executive_summary":') and line.strip() != '{':
                                if line.strip() and not line.strip().startswith('📈'):
                                    pca_lines.append(line)
                        if pca_lines:
                            pca_content = '\n'.join(pca_lines).strip()

                    result['pca_analysis'] = pca_content
                    result['pca_insights'] = {'analysis': pca_content}

        # Validate we have the required fields
        if 'executive_summary' in result or 'principal_findings' in result or 'pca_analysis' in result:
            # Fill in missing fields with defaults
            result.setdefault('executive_summary', '')
            result.setdefault('principal_findings', [])
            result.setdefault('pca_insights', {})
            result['original_structure'] = 'sections_combined'
            return result

        return None

    def _extract_json_from_section(self, section_content: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON object from section content, handling markdown code blocks.

        Args:
            section_content: Content of a single section

        Returns:
            Parsed JSON dictionary or None
        """
        # First, try to extract from markdown code blocks
        if '```json' in section_content:
            # Find the JSON within the code block
            start_marker = section_content.find('```json')
            if start_marker != -1:
                start_json = section_content.find('{', start_marker)
                end_marker = section_content.find('```', start_marker + 7)
                if end_marker != -1:
                    end_json = section_content.rfind('}', start_marker, end_marker) + 1
                    if start_json != -1 and end_json > start_json:
                        json_str = section_content[start_json:end_json]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            pass

        # Fallback: Find JSON boundaries directly
        start_idx = section_content.find('{')
        end_idx = section_content.rfind('}') + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = section_content[start_idx:end_idx]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        return None

    def _extract_json_fragments(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract all JSON fragments from content.

        Args:
            content: Full response content

        Returns:
            List of parsed JSON fragments
        """
        fragments = []
        import re

        # Find all JSON-like structures
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, content, re.DOTALL)

        for match in matches:
            try:
                parsed = json.loads(match)
                fragments.append(parsed)
            except json.JSONDecodeError:
                continue

        return fragments

    def _combine_json_fragments(self, fragments: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Combine multiple JSON fragments into a single response.

        Args:
            fragments: List of JSON fragments

        Returns:
            Combined response dictionary or None
        """
        if not fragments:
            return None

        combined = {}

        for fragment in fragments:
            for key, value in fragment.items():
                if key in ['executive_summary', 'principal_findings', 'pca_analysis']:
                    combined[key] = value

        if combined:
            # Fill missing fields
            combined.setdefault('executive_summary', '')
            combined.setdefault('principal_findings', [])
            combined.setdefault('pca_insights', {'analysis': combined.get('pca_analysis', '')})
            combined['original_structure'] = 'fragments_combined'
            return combined

        return None

    def _extract_pca_content(self, text: str) -> str:
        """
        Extract PCA analysis content from text, handling various formats.

        Args:
            text: Text containing PCA analysis

        Returns:
            Cleaned PCA content
        """
        # Remove any leading/trailing JSON markers
        text = text.strip()

        # If it starts with {, try to extract JSON content
        if text.startswith('{'):
            # Try to extract just the content
            start_content = text.find('"pca_analysis":') or text.find('"analysis":')
            if start_content != -1:
                start_quote = text.find('"', start_content + 10)
                if start_quote != -1:
                    end_quote = text.find('"', start_quote + 1)
                    if end_quote != -1:
                        content = text[start_quote + 1:end_quote]
                        return content.replace('\\n', '\n').replace('\\"', '"')

        # If it looks like raw text (contains multiple paragraphs separated by double newlines)
        if '\n\n' in text:
            return text.replace('\\n', '\n').strip()

        # If it contains "Análisis adicional no disponible", clean it up
        if 'Análisis adicional no disponible' in text:
            # Extract everything before this marker
            marker_pos = text.find('Análisis adicional no disponible')
            if marker_pos > 0:
                return text[:marker_pos].strip().replace('\\n', '\n')

        # Return cleaned text
        return text.replace('\\n', '\n').strip()

    def _create_fallback_response(self, response_content: str) -> Dict[str, Any]:
        """
        Create a fallback response when parsing fails.

        Args:
            response_content: Original response content

        Returns:
            Fallback response dictionary
        """
        return {
            'principal_findings': [{
                'bullet_point': response_content[:300] + "..." if len(response_content) > 300 else response_content,
                'reasoning': "Parsing failed, using raw response",
                'data_source': ["AI Analysis"],
                'confidence': "low"
            }],
            'pca_insights': {'analysis': response_content[:400] + "..." if len(response_content) > 400 else response_content},
            'executive_summary': response_content[:500] + "..." if len(response_content) > 500 else response_content,
            'pca_analysis': response_content[:400] + "..." if len(response_content) > 400 else response_content,
            'original_structure': 'fallback'
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
                logging.info(f"✅ Model {model} is available and working")
            except Exception as e:
                logging.warning(f"❌ Model {model} unavailable: {e}")
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