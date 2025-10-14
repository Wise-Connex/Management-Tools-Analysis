#!/usr/bin/env python3
"""
Simple Groq Model Comparison Tool

Tests the 4 Groq models with a standardized Key Findings prompt
to determine the optimal preference order for fallback configuration.
"""

import asyncio
import json
import time
import logging
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_groq_comparison.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ModelResult:
    """Results from a single model test."""
    model: str
    success: bool
    response_time_ms: int
    token_count: int
    response_content: str
    parsed_content: Dict[str, Any]
    quality_score: float
    error_message: str = None

class SimpleGroqComparator:
    """Simple model comparison tool using direct API calls."""
    
    def __init__(self):
        """Initialize the comparator with API key."""
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        # Models to compare
        self.models_to_test = [
            'openai/gpt-oss-120b',
            'meta-llama/llama-4-scout-17b-16e-instruct',
            'llama-3.3-70b-versatile',
            'moonshotai/kimi-k2-instruct'
        ]
        
        # Standardized Key Findings test prompt (based on real prompt structure)
        self.test_prompt = """
Analiza los siguientes datos multi-fuente para la herramienta "Gestión de Costos":

### CONTEXTO DEL ANÁLISIS

**Herramienta de Gestión:** Gestión de Costos
**Fuentes de Datos Seleccionadas:** Google Trends, Bain Usabilidad, Crossref
**Rango Temporal:** del 2020-01-01 al 2023-12-31
**Puntos de Datos Analizados:** 1,247

### ANÁLISIS DE COMPONENTES PRINCIPALES (PCA)

**Datos PCA Adjuntos:**
- Herramienta de Gestión Analizada: Gestión de Costos
- Varianza Total Explicada: 67.3%
- Componentes Principales Identificados: 3
- Fuentes de Datos Disponibles: 3

**ANÁLISIS NUMÉRICO DETALLADO DE COMPONENTES:**

**Componente 1 (42.1% varianza explicada):**
Representa una dinámica de adopción popular vs satisfacción real

**Cargas Específicas:**
- Google Trends: carga positiva fuerte de 0.387
- Bain Usabilidad: carga positiva moderada de 0.292
- Crossref: carga negativa fuerte de -0.412

**Relación de Oposición en PC1:**
- Fuentes con influencia positiva: Google Trends, Bain Usabilidad
- Fuentes con influencia negativa: Crossref
- Esto sugiere una tensión entre popularidad/acceso y rigor académico

**Componente 2 (15.8% varianza explicada):**
Representa factores académicos independientes

**Cargas Específicas:**
- Crossref: carga positiva fuerte de 0.445
- Google Trends: carga negativa débil de -0.189
- Bain Usabilidad: carga negativa moderada de -0.276

**ANÁLISIS COMBINADO DE PRIMEROS DOS COMPONENTES:**
- Varianza combinada explicada: 57.9%
- Poder explicativo bueno para insights significativos

### ANÁLISIS ESTADÍSTICO COMPRENSIVO

**Estadísticas por Fuente de Datos:**

**Google Trends:**
- Media: 67.23
- Desviación Estándar: 12.45
- Tendencia: increasing
- Significancia: significant

**Bain Usabilidad:**
- Media: 54.89
- Desviación Estándar: 8.92
- Tendencia: stable
- Significancia: not_significant

**Crossref:**
- Media: 23.41
- Desviación Estándar: 6.78
- Tendencia: increasing
- Significancia: significant

**Correlaciones Significativas Entre Fuentes:**
- Google Trends_vs_Bain Usabilidad: Correlación moderate (0.342)
- Google Trends_vs_Crossref: Correlación weak (0.156)

### ANÁLISIS TEMPORAL INTEGRADO PARA HALLAZGOS PRINCIPALES

**Datos Temporales para Integrar en Hallazgos Principales:**

**Tendencias Temporales Clave:**

**Google Trends:** tendencia increasing con momento de 0.234 y volatilidad de 0.145
→ Integrar este crecimiento con cargas PCA positivas de Google Trends

**Bain Usabilidad:** tendencia stable con momento de 0.045 y volatilidad de 0.089
→ Analizar estabilidad de Bain Usabilidad en contexto multivariado

**Crossref:** tendencia increasing con momento de 0.178 y volatilidad de 0.123
→ Integrar este crecimiento con cargas PCA positivas de Crossref

### REQUISITOS DEL ANÁLISIS

Por favor, proporciona un análisis doctoral-level que:

1. **Sintetice Información Multi-fuente**: Integre insights de todas las fuentes de datos incluyendo análisis temporal, de heatmap y PCA
2. **Énfasis en PCA**: Destaque insights de componentes principales con explicaciones claras integradas en una narrativa fluida
3. **Identifique Patrones Temporales**: Detecte tendencias, ciclos y anomalías significativas e integrelas en los hallazgos principales
4. **Genere Conclusiones Ejecutivas**: Proporcione insights accionables para tomadores de decisiones
5. **Mantenga Rigor Académico**: Use terminología apropiada y metodología sistemática

**ESTRUCTURA REQUERIDA DEL ANÁLISIS:**

Genera un análisis doctoral con las siguientes tres secciones principales:

**1. Resumen Ejecutivo:**
- Un párrafo conciso que capture los insights más críticos
- Enfoque en el "gap teoría-práctica" y sus implicaciones estratégicas
- Mencione específicamente el porcentaje de varianza explicada por los primeros dos componentes

**2. Hallazgos Principales:**
- MÚLTIPLES viñetas concisas y accionables (3-5 viñetas diferentes)
- Cada viñeta debe ser un hallazgo específico y diferente con datos cuantitativos
- Integre insights de PCA, análisis temporal, y heatmap en cada viñeta
- Conecte los patrones temporales con los hallazgos de PCA en diferentes viñetas
- Mencione fuentes específicas y valores numéricos exactos en cada viñeta

**3. Análisis PCA:**
- Un ensayo analítico detallado (NO datos estadísticos)
- Interprete las cargas específicas con valores numéricos exactos
- Explique las relaciones de oposición entre fuentes
- Conecte con conceptos académicos como "brecha teoría-práctica"
- Use el porcentaje de varianza explicada

**Formato de Salida Requerido:**
Responde únicamente en formato JSON con la siguiente estructura:
```json
{
  "executive_summary": "Resumen ejecutivo conciso y accionable como párrafo fluido",
  "principal_findings": ["Viñeta 1 con hallazgo específico y datos cuantitativos", "Viñeta 2 con otro hallazgo específico", "Viñeta 3 con insight integrado", "Viñeta 4 con patrón temporal", "Viñeta 5 con conclusión cuantitativa"],
  "pca_analysis": "Ensayo analítico detallado sobre PCA con interpretación de cargas y relaciones"
}
```

### FORMATO DE SALIDA

**IMPORTANTE**: Responde ÚNICAMENTE con el objeto JSON. No incluyas explicaciones,
introducciones, o texto fuera del JSON.

El JSON debe contener exactamente:
- `executive_summary`: Párrafo fluido con resumen ejecutivo
- `principal_findings`: Ensayo doctoral narrativo integrando todos los análisis
- `pca_analysis`: Ensayo analítico detallado sobre componentes principales
"""
        
        # Results storage
        self.results = []

    async def run_comparison(self) -> Dict[str, Any]:
        """Run comprehensive model comparison."""
        logging.info("🚀 Starting Simple Groq model comparison")
        
        comparison_start = time.time()
        
        # Test each model
        for model in self.models_to_test:
            logging.info(f"\n📊 Testing model: {model}")
            
            try:
                result = await self._test_model(model)
                if result:
                    self.results.append(result)
                    logging.info(f"  ✅ Model {model} completed successfully")
                else:
                    logging.warning(f"  ⚠️ Model {model} failed to produce result")
                    
            except Exception as e:
                logging.error(f"  ❌ Model {model} failed: {e}")
                # Add failure result
                self.results.append(ModelResult(
                    model=model,
                    success=False,
                    response_time_ms=0,
                    token_count=0,
                    response_content="",
                    parsed_content={},
                    quality_score=0.0,
                    error_message=str(e)
                ))
        
        total_time = time.time() - comparison_start
        logging.info(f"\n🎉 Model comparison completed in {total_time:.2f}s")
        
        # Analyze results
        return self._analyze_results()

    async def _test_model(self, model: str) -> ModelResult:
        """Test a specific model with the standard prompt."""
        import aiohttp
        
        start_time = time.time()
        
        try:
            logging.info(f"🔄 Testing model {model}")
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un analista de investigación doctoral especializado en herramientas de gestión empresarial. Tu tarea es analizar datos multi-fuente y generar insights de nivel ejecutivo con énfasis en análisis de componentes principales (PCA)."
                    },
                    {
                        "role": "user",
                        "content": self.test_prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            # Make API call
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    response_time_ms = int((time.time() - start_time) * 1000)
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if 'choices' in result and len(result['choices']) > 0:
                            response_content = result['choices'][0]['message']['content']
                            token_count = result.get('usage', {}).get('total_tokens', 0)
                            
                            # Parse the response
                            parsed_content = self._parse_ai_response(response_content)
                            
                            # Calculate quality score
                            quality_score = self._calculate_quality_score(parsed_content)
                            
                            logging.info(f"✅ Model {model} responded in {response_time_ms}ms with {token_count} tokens")
                            
                            return ModelResult(
                                model=model,
                                success=True,
                                response_time_ms=response_time_ms,
                                token_count=token_count,
                                response_content=response_content,
                                parsed_content=parsed_content,
                                quality_score=quality_score
                            )
                        else:
                            logging.warning(f"⚠️ Model {model} returned invalid response format")
                            return ModelResult(
                                model=model,
                                success=False,
                                response_time_ms=response_time_ms,
                                token_count=0,
                                response_content="",
                                parsed_content={},
                                quality_score=0.0,
                                error_message="Invalid response format"
                            )
                    else:
                        error_text = await response.text()
                        logging.error(f"❌ API error {response.status} for {model}: {error_text}")
                        return ModelResult(
                            model=model,
                            success=False,
                            response_time_ms=response_time_ms,
                            token_count=0,
                            response_content="",
                            parsed_content={},
                            quality_score=0.0,
                            error_message=f"API error {response.status}: {error_text}"
                        )
                        
        except asyncio.TimeoutError:
            response_time_ms = int((time.time() - start_time) * 1000)
            logging.error(f"⏰ Model {model} timed out after {response_time_ms}ms")
            
            return ModelResult(
                model=model,
                success=False,
                response_time_ms=response_time_ms,
                token_count=0,
                response_content="",
                parsed_content={},
                quality_score=0.0,
                error_message="Request timeout"
            )
            
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            logging.error(f"❌ Model {model} failed: {e}")
            
            return ModelResult(
                model=model,
                success=False,
                response_time_ms=response_time_ms,
                token_count=0,
                response_content="",
                parsed_content={},
                quality_score=0.0,
                error_message=str(e)
            )

    def _parse_ai_response(self, response_content: str) -> Dict[str, Any]:
        """Parse and validate AI response."""
        try:
            # Try to extract JSON from response
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_content[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['executive_summary', 'principal_findings', 'pca_analysis']
                for field in required_fields:
                    if field not in parsed:
                        parsed[field] = ""
                
                return parsed
            else:
                # Fallback response
                return {
                    'executive_summary': response_content[:300] + "..." if len(response_content) > 300 else response_content,
                    'principal_findings': [response_content[:200] + "..." if len(response_content) > 200 else response_content],
                    'pca_analysis': response_content[:250] + "..." if len(response_content) > 250 else response_content
                }
                
        except json.JSONDecodeError as e:
            logging.warning(f"JSON parsing failed: {e}")
            # Fallback response
            return {
                'executive_summary': response_content[:300] + "..." if len(response_content) > 300 else response_content,
                'principal_findings': [response_content[:200] + "..." if len(response_content) > 200 else response_content],
                'pca_analysis': response_content[:250] + "..." if len(response_content) > 250 else response_content
            }

    def _calculate_quality_score(self, parsed_content: Dict[str, Any]) -> float:
        """Calculate quality score for model response."""
        score = 0.0
        
        try:
            # Executive summary quality (25%)
            exec_summary = parsed_content.get('executive_summary', '')
            if len(exec_summary) > 100:
                score += 0.15
            if any(term in exec_summary.lower() for term in ['gestión', 'análisis', 'estratégico']):
                score += 0.10
            
            # Principal findings quality (35%)
            findings = parsed_content.get('principal_findings', [])
            if isinstance(findings, list):
                if len(findings) >= 3:
                    score += 0.20
                # Check for quantitative data
                for finding in findings:
                    finding_str = str(finding).lower()
                    if any(char.isdigit() for char in finding_str):
                        score += 0.15
                        break
            else:
                # Handle non-list findings (convert to list if it's a string)
                if isinstance(findings, str):
                    findings_list = [findings]
                    if len(findings) > 200:
                        score += 0.20
                elif findings is None:
                    findings_list = []
                else:
                    # Convert other types to string and wrap in list
                    findings_list = [str(findings)]
                    if len(str(findings)) > 200:
                        score += 0.20
            
            # PCA analysis quality (30%)
            pca_analysis = parsed_content.get('pca_analysis', '')
            if len(pca_analysis) > 150:
                score += 0.15
            # Check for technical terms
            technical_terms = ['componente', 'varianza', 'carga', 'análisis', 'correlación']
            term_count = sum(1 for term in technical_terms if term in pca_analysis.lower())
            score += min(term_count * 0.03, 0.15)
            
            # Structure validity (10%)
            if all(field in parsed_content for field in ['executive_summary', 'principal_findings', 'pca_analysis']):
                score += 0.10
            
        except Exception as e:
            logging.warning(f"Quality score calculation failed: {e}")
        
        return min(score, 1.0)

    def _analyze_results(self) -> Dict[str, Any]:
        """Analyze results and determine preference order."""
        try:
            if not self.results:
                return {'error': 'No results to analyze'}
            
            logging.info("📊 Analyzing model comparison results...")
            logging.info(f"📊 Results collected: {len(self.results)}")
            
            # Debug: Print result details
            for i, result in enumerate(self.results):
                logging.info(f"📊 Result {i}: model={result.model}, success={result.success}, quality_score={result.quality_score}")
            
            # Calculate model statistics
            model_stats = {}
            for result in self.results:
                model_stats[result.model] = {
                    'success': result.success,
                    'response_time_ms': result.response_time_ms,
                    'token_count': result.token_count,
                    'quality_score': result.quality_score,
                    'error_message': result.error_message
                }
            
            # Determine preference order (quality-weighted with speed)
            preference_scores = {}
            for model, stats in model_stats.items():
                logging.info(f"📊 Calculating preference score for {model}: success={stats['success']}")
                
                if not stats['success']:
                    preference_scores[model] = 0.0
                    continue
                
                # Quality is most important (60%), speed matters (40%)
                quality_component = stats['quality_score'] * 0.6
                logging.info(f"📊 {model} quality_component: {quality_component}")
                
                # Speed component (faster is better, normalized)
                successful_times = [s['response_time_ms'] for s in model_stats.values() if s['success'] and s['response_time_ms'] > 0]
                if successful_times:
                    max_time = max(successful_times)
                    speed_component = (1 - stats['response_time_ms'] / max_time) * 0.4
                    logging.info(f"📊 {model} speed_component: {speed_component} (time: {stats['response_time_ms']}ms, max: {max_time}ms)")
                else:
                    speed_component = 0
                    logging.info(f"📊 {model} speed_component: 0 (no successful times)")
                
                preference_scores[model] = quality_component + speed_component
                logging.info(f"📊 {model} total preference_score: {preference_scores[model]}")
            
            # Sort models by preference score
            ranked_models = sorted(preference_scores.items(), key=lambda x: x[1], reverse=True)
            logging.info(f"📊 Models ranked: {len(ranked_models)}")
            
            # Generate recommendations
            logging.info("📊 Generating recommendations...")
            recommendations = self._generate_recommendations(model_stats, ranked_models)
            logging.info("📊 Recommendations generated")
            
            # Create comprehensive report
            logging.info("📊 Creating analysis result...")
            analysis_result = {
                'test_summary': {
                    'total_tests': len(self.results),
                    'models_tested': len(model_stats),
                    'successful_tests': sum(1 for r in self.results if r.success)
                },
                'model_statistics': model_stats,
                'preference_ranking': [
                    {
                        'rank': i + 1,
                        'model': model,
                        'preference_score': score,
                        'key_metrics': model_stats[model]
                    }
                    for i, (model, score) in enumerate(ranked_models)
                ],
                'recommendations': recommendations,
                'detailed_results': self.results
            }
            logging.info("📊 Analysis result created")
            
            # Save results to file
            logging.info("📊 Saving results...")
            self._save_results(analysis_result)
            logging.info("📊 Results saved")
            
            return analysis_result
            
        except Exception as e:
            import traceback
            logging.error(f"📊 Error in _analyze_results: {e}")
            logging.error(f"📊 Traceback: {traceback.format_exc()}")
            return {'error': f'Analysis error: {str(e)}'}

    def _generate_recommendations(self, model_stats: Dict[str, Any], 
                                ranked_models: List[Tuple[str, float]]) -> Dict[str, Any]:
        """Generate specific recommendations for fallback configuration."""
        
        top_model = ranked_models[0][0]
        
        recommendations = {
            'primary_recommendation': {
                'model': top_model,
                'reasoning': f"Highest preference score ({ranked_models[0][1]:.3f}) with best balance of quality and speed"
            },
            'fallback_order': [model for model, _ in ranked_models],
            'configuration_updates': {
                'current_order': self.models_to_test,
                'recommended_order': [model for model, _ in ranked_models]
            },
            'model_insights': {}
        }
        
        # Add specific insights for each model
        for model, _ in ranked_models:
            stats = model_stats[model]
            insights = []
            
            if not stats['success']:
                insights.append("Model failed to respond")
            else:
                if stats['quality_score'] > 0.8:
                    insights.append("Excellent response quality")
                elif stats['quality_score'] > 0.6:
                    insights.append("Good response quality")
                else:
                    insights.append("Needs quality improvement")
                
                if stats['response_time_ms'] < 2000:
                    insights.append("Fast response times")
                elif stats['response_time_ms'] < 5000:
                    insights.append("Good response speed")
                else:
                    insights.append("Slower response times")
            
            recommendations['model_insights'][model] = insights
        
        # Add configuration code snippet
        recommended_list = [model for model, _ in ranked_models]
        recommendations['code_update'] = f"""
# Update in dashboard_app/key_findings/unified_ai_service.py
self.groq_models = {recommended_list}
"""
        
        return recommendations

    def _save_results(self, analysis_result: Dict[str, Any]):
        """Save detailed results to files."""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Save full analysis
        with open(f'simple_groq_analysis_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
        
        # Save summary report
        summary = self._create_summary_report(analysis_result)
        with open(f'simple_groq_summary_{timestamp}.md', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logging.info(f"📄 Results saved to simple_groq_analysis_{timestamp}.json and simple_groq_summary_{timestamp}.md")

    def _create_summary_report(self, analysis_result: Dict[str, Any]) -> str:
        """Create a markdown summary report."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""# Simple Groq Model Comparison Summary Report
Generated: {timestamp}

## Executive Summary

This report compares the performance of 4 Groq models using a standardized Key Findings prompt based on real management tools analysis.

### Test Configuration
- **Models Tested**: {analysis_result['test_summary']['models_tested']}
- **Total Tests**: {analysis_result['test_summary']['total_tests']}
- **Successful Tests**: {analysis_result['test_summary']['successful_tests']}

## Model Ranking (Recommended Fallback Order)

"""
        
        for rank_info in analysis_result['preference_ranking']:
            model = rank_info['model']
            score = rank_info['preference_score']
            metrics = rank_info['key_metrics']
            
            logging.info(f"📊 Processing model {model} for report")
            
            report += f"""### {rank_info['rank']}. {model}

**Preference Score**: {score:.3f}

**Key Metrics**:
- Success: {metrics['success']}
- Quality Score: {metrics['quality_score']:.3f}
- Response Time: {metrics['response_time_ms']:.0f}ms
- Token Count: {metrics['token_count']:.0f}

"""
            
            # Safely get insights
            try:
                insights = analysis_result['recommendations']['model_insights'].get(model, [])
                insights_str = ', '.join(insights) if insights else 'No insights available'
                logging.info(f"📊 Insights for {model}: {insights_str}")
                report += f"**Insights**: {insights_str}\n\n"
            except Exception as e:
                logging.error(f"📊 Error processing insights for {model}: {e}")
                report += f"**Insights**: Error processing insights\n\n"
        
        report += f"""## Recommendations

### Primary Model
**{analysis_result['recommendations']['primary_recommendation']['model']}**
- {analysis_result['recommendations']['primary_recommendation']['reasoning']}

### Recommended Fallback Order
"""
        for i, model in enumerate(analysis_result['recommendations']['fallback_order']):
            report += f"{i+1}. {model}\n"
        
        report += f"""
### Implementation
{analysis_result['recommendations'].get('code_update', 'No code changes needed')}

## Test Details

**Test Prompt**: Standardized Key Findings analysis prompt for "Gestión de Costos" with:
- Multi-source data (Google Trends, Bain Usability, Crossref)
- PCA analysis with specific component loadings
- Statistical summaries and temporal trends
- Required JSON output format

**Evaluation Criteria**:
- Response quality (content completeness, analytical depth)
- Response speed (time to first token)
- Structure validity (proper JSON format)
- Technical accuracy (PCA interpretation, quantitative analysis)

For complete detailed results, see the accompanying JSON file.

---
*Report generated by Simple Groq Model Comparator*
"""
        
        return report

async def main():
    """Main execution function."""
    try:
        # Initialize comparator
        comparator = SimpleGroqComparator()
        
        # Run comparison
        results = await comparator.run_comparison()
        
        # Display summary
        if 'error' not in results:
            print("\n" + "="*60)
            print("SIMPLE GROQ MODEL COMPARISON COMPLETED")
            print("="*60)
            
            print("\nRECOMMENDED FALLBACK ORDER:")
            for i, model_info in enumerate(results['preference_ranking']):
                status = "✅" if model_info['key_metrics']['success'] else "❌"
                print(f"{i+1}. {model_info['model']} (Score: {model_info['preference_score']:.3f}) {status}")
            
            print(f"\nPRIMARY RECOMMENDATION: {results['recommendations']['primary_recommendation']['model']}")
            print(f"REASONING: {results['recommendations']['primary_recommendation']['reasoning']}")
            
            print("\n" + "="*60)
        else:
            print(f"Comparison failed: {results['error']}")
            
    except Exception as e:
        logging.error(f"Comparison execution failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())