#!/usr/bin/env python3
"""
Groq Model Comparison Tool for Key Findings

Compares the 4 Groq models using real Key Findings data and prompts
to determine the optimal preference order for fallback configuration.

Models to compare:
- openai/gpt-oss-120b
- meta-llama/llama-4-scout-17b-16e-instruct
- llama-3.3-70b-versatile
- moonshotai/kimi-k2-instruct
"""

import asyncio
import json
import time
import logging
import os
import sys
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add dashboard_app to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard_app'))

from key_findings.unified_ai_service import UnifiedAIService
from key_findings.prompt_engineer import PromptEngineer
from key_findings.data_aggregator import DataAggregator
from key_findings.database_manager import KeyFindingsDBManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('groq_model_comparison.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ModelResult:
    """Results from a single model test."""
    model: str
    tool_name: str
    success: bool
    response_time_ms: int
    token_count: int
    response_content: str
    parsed_content: Dict[str, Any]
    quality_score: float
    error_message: str = None

@dataclass
class QualityMetrics:
    """Quality metrics for model evaluation."""
    completeness_score: float  # Has all required sections
    coherence_score: float     # Logical flow and consistency
    depth_score: float         # Analytical depth
    structure_score: float     # JSON structure validity
    relevance_score: float     # Relevance to business analysis
    overall_score: float       # Weighted combination

class GroqModelComparator:
    """Comprehensive model comparison tool using real Key Findings data."""
    
    def __init__(self):
        """Initialize the comparator with API keys and real system components."""
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        # Initialize AI service with only Groq
        self.ai_service = UnifiedAIService(groq_api_key=self.groq_api_key)
        
        # Models to compare
        self.models_to_test = [
            'openai/gpt-oss-120b',
            'meta-llama/llama-4-scout-17b-16e-instruct',
            'llama-3.3-70b-versatile',
            'moonshotai/kimi-k2-instruct'
        ]
        
        # Test scenarios with real tools
        self.test_scenarios = [
            {
                'tool_name': 'Gestión de Costos',
                'sources': [1, 3, 4],  # Google Trends, Bain Usability, Crossref
                'language': 'es',
                'description': 'Cost Management with multi-source data'
            },
            {
                'tool_name': 'Gestión del Cambio',
                'sources': [1, 2, 5],  # Google Trends, Google Books, Bain Satisfaction
                'language': 'es',
                'description': 'Change Management with academic and satisfaction data'
            },
            {
                'tool_name': 'Innovación Colaborativa',
                'sources': [1, 3, 5],  # Google Trends, Bain Usability, Bain Satisfaction
                'language': 'es',
                'description': 'Collaborative Innovation with usability focus'
            }
        ]
        
        # Initialize system components
        self._initialize_system_components()
        
        # Results storage
        self.results = []

    def _initialize_system_components(self):
        """Initialize Key Findings system components for real data access."""
        try:
            logging.info("🔧 Initializing Key Findings system components...")
            
            # Import dashboard components
            from dashboard import get_database_manager
            
            # Get main database manager
            self.db_manager = get_database_manager()
            logging.info("✅ Main database manager initialized")
            
            # Initialize Key Findings database manager
            kf_db_path = './data/key_findings/key_findings.db'
            self.kf_db_manager = KeyFindingsDBManager(kf_db_path)
            logging.info("✅ Key Findings database manager initialized")
            
            # Initialize data aggregator
            self.data_aggregator = DataAggregator(self.db_manager, self.kf_db_manager)
            logging.info("✅ Data aggregator initialized")
            
            # Initialize prompt engineer
            self.prompt_engineer = PromptEngineer(language='es')
            logging.info("✅ Prompt engineer initialized")
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize system components: {e}")
            raise

    async def run_comparison(self) -> Dict[str, Any]:
        """Run comprehensive model comparison."""
        logging.info("🚀 Starting Groq model comparison with real Key Findings data")
        
        comparison_start = time.time()
        
        # Test each model with each scenario
        for model in self.models_to_test:
            logging.info(f"\n📊 Testing model: {model}")
            
            for scenario in self.test_scenarios:
                logging.info(f"  🎯 Scenario: {scenario['description']}")
                
                try:
                    # Collect real data for this scenario
                    analysis_data = await self._collect_scenario_data(scenario)
                    
                    if 'error' in analysis_data:
                        logging.warning(f"⚠️ Skipping scenario due to data error: {analysis_data['error']}")
                        continue
                    
                    # Generate real Key Findings prompt
                    prompt = self.prompt_engineer.create_analysis_prompt(
                        analysis_data, 
                        {'analysis_type': 'comprehensive', 'emphasis': 'pca'}
                    )
                    
                    # Test model with real prompt
                    result = await self._test_model_with_prompt(model, prompt, scenario)
                    
                    if result:
                        self.results.append(result)
                        logging.info(f"  ✅ Model {model} completed for {scenario['tool_name']}")
                    
                except Exception as e:
                    logging.error(f"  ❌ Model {model} failed for {scenario['tool_name']}: {e}")
                    # Add failure result
                    self.results.append(ModelResult(
                        model=model,
                        tool_name=scenario['tool_name'],
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

    async def _collect_scenario_data(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Collect real data for a test scenario."""
        try:
            logging.info(f"📊 Collecting data for {scenario['tool_name']} with sources {scenario['sources']}")
            
            # Use the real data aggregation pipeline
            analysis_data = self.data_aggregator.collect_analysis_data(
                tool_name=scenario['tool_name'],
                selected_sources=scenario['sources'],
                language=scenario['language']
            )
            
            if 'error' in analysis_data:
                logging.warning(f"⚠️ Data collection error: {analysis_data['error']}")
                return analysis_data
            
            logging.info(f"✅ Data collected: {analysis_data.get('data_points_analyzed', 0)} points, "
                        f"{analysis_data.get('sources_count', 0)} sources")
            
            return analysis_data
            
        except Exception as e:
            logging.error(f"❌ Data collection failed: {e}")
            return {'error': str(e)}

    async def _test_model_with_prompt(self, model: str, prompt: str, scenario: Dict[str, Any]) -> ModelResult:
        """Test a specific model with a real Key Findings prompt."""
        start_time = time.time()
        
        try:
            logging.info(f"🔄 Testing model {model} with prompt length {len(prompt)}")
            
            # Call the model directly using the unified service
            result = await self.ai_service._call_model(
                prompt=prompt,
                model=model,
                provider='groq',
                language=scenario['language']
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if result and 'choices' in result and len(result['choices']) > 0:
                response_content = result['choices'][0]['message']['content']
                token_count = result.get('usage', {}).get('total_tokens', 0)
                
                # Parse the response
                parsed_content = self.ai_service._parse_ai_response(response_content)
                
                # Calculate quality score
                quality_metrics = self._calculate_quality_metrics(parsed_content, scenario)
                
                logging.info(f"✅ Model {model} responded in {response_time_ms}ms with {token_count} tokens")
                
                return ModelResult(
                    model=model,
                    tool_name=scenario['tool_name'],
                    success=True,
                    response_time_ms=response_time_ms,
                    token_count=token_count,
                    response_content=response_content,
                    parsed_content=parsed_content,
                    quality_score=quality_metrics.overall_score
                )
            else:
                logging.warning(f"⚠️ Model {model} returned invalid response")
                return ModelResult(
                    model=model,
                    tool_name=scenario['tool_name'],
                    success=False,
                    response_time_ms=response_time_ms,
                    token_count=0,
                    response_content="",
                    parsed_content={},
                    quality_score=0.0,
                    error_message="Invalid response format"
                )
                
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            logging.error(f"❌ Model {model} failed: {e}")
            
            return ModelResult(
                model=model,
                tool_name=scenario['tool_name'],
                success=False,
                response_time_ms=response_time_ms,
                token_count=0,
                response_content="",
                parsed_content={},
                quality_score=0.0,
                error_message=str(e)
            )

    def _calculate_quality_metrics(self, parsed_content: Dict[str, Any], scenario: Dict[str, Any]) -> QualityMetrics:
        """Calculate comprehensive quality metrics for model response."""
        
        # Completeness: Check all required sections are present
        required_sections = ['executive_summary', 'principal_findings', 'pca_analysis']
        completeness_score = sum(1 for section in required_sections 
                               if section in parsed_content and parsed_content[section]) / len(required_sections)
        
        # Structure: Check JSON structure validity
        structure_score = 1.0 if all(section in parsed_content for section in required_sections) else 0.5
        
        # Coherence: Evaluate logical flow and consistency
        coherence_score = self._evaluate_coherence(parsed_content)
        
        # Depth: Analytical depth based on content length and complexity
        depth_score = self._evaluate_depth(parsed_content)
        
        # Relevance: Business analysis relevance
        relevance_score = self._evaluate_relevance(parsed_content, scenario)
        
        # Overall weighted score
        overall_score = (
            completeness_score * 0.25 +
            structure_score * 0.20 +
            coherence_score * 0.20 +
            depth_score * 0.20 +
            relevance_score * 0.15
        )
        
        return QualityMetrics(
            completeness_score=completeness_score,
            structure_score=structure_score,
            coherence_score=coherence_score,
            depth_score=depth_score,
            relevance_score=relevance_score,
            overall_score=overall_score
        )

    def _evaluate_coherence(self, content: Dict[str, Any]) -> float:
        """Evaluate logical flow and consistency."""
        score = 0.5  # Base score
        
        try:
            # Check if executive summary aligns with findings
            exec_summary = content.get('executive_summary', '').lower()
            findings = content.get('principal_findings', '')
            
            if isinstance(findings, list):
                findings_text = ' '.join(str(f) for f in findings).lower()
            else:
                findings_text = str(findings).lower()
            
            # Simple coherence check: common keywords
            exec_keywords = set(exec_summary.split()[:10])  # First 10 words
            findings_keywords = set(findings_text.split())
            
            if exec_keywords and findings_keywords:
                overlap = len(exec_keywords.intersection(findings_keywords))
                coherence_bonus = min(overlap / 5, 0.5)  # Max 0.5 bonus
                score += coherence_bonus
            
            # Check PCA analysis coherence
            pca_analysis = content.get('pca_analysis', '').lower()
            if 'componente' in pca_analysis or 'varianza' in pca_analysis:
                score += 0.2  # Bonus for relevant PCA content
            
        except Exception as e:
            logging.warning(f"Coherence evaluation failed: {e}")
        
        return min(score, 1.0)

    def _evaluate_depth(self, content: Dict[str, Any]) -> float:
        """Evaluate analytical depth."""
        score = 0.0
        
        try:
            # Executive summary depth
            exec_summary = content.get('executive_summary', '')
            if len(exec_summary) > 100:
                score += 0.2
            if any(term in exec_summary.lower() for term in ['análisis', 'estratégico', 'implicaciones']):
                score += 0.1
            
            # Principal findings depth
            findings = content.get('principal_findings', [])
            if isinstance(findings, list):
                if len(findings) >= 3:
                    score += 0.3
                # Check for quantitative data in findings
                for finding in findings:
                    finding_str = str(finding).lower()
                    if any(char.isdigit() for char in finding_str):
                        score += 0.1
                        break
            else:
                if len(str(findings)) > 200:
                    score += 0.2
            
            # PCA analysis depth
            pca_analysis = content.get('pca_analysis', '')
            if len(pca_analysis) > 150:
                score += 0.2
            # Check for technical terms
            technical_terms = ['carga', 'varianza', 'componente', 'análisis', 'correlación']
            term_count = sum(1 for term in technical_terms if term in pca_analysis.lower())
            score += min(term_count * 0.05, 0.2)
            
        except Exception as e:
            logging.warning(f"Depth evaluation failed: {e}")
        
        return min(score, 1.0)

    def _evaluate_relevance(self, content: Dict[str, Any], scenario: Dict[str, Any]) -> float:
        """Evaluate business analysis relevance."""
        score = 0.3  # Base score for attempting analysis
        
        try:
            tool_name = scenario['tool_name'].lower()
            all_content = (
                str(content.get('executive_summary', '')) + ' ' +
                str(content.get('principal_findings', '')) + ' ' +
                str(content.get('pca_analysis', ''))
            ).lower()
            
            # Check for tool-specific relevance
            if any(word in all_content for word in tool_name.split()):
                score += 0.3
            
            # Check for business relevance terms
            business_terms = ['gestión', 'organización', 'estratégico', 'negocio', 'implementación']
            business_count = sum(1 for term in business_terms if term in all_content)
            score += min(business_count * 0.1, 0.4)
            
        except Exception as e:
            logging.warning(f"Relevance evaluation failed: {e}")
        
        return min(score, 1.0)

    def _analyze_results(self) -> Dict[str, Any]:
        """Analyze comprehensive results and determine preference order."""
        if not self.results:
            return {'error': 'No results to analyze'}
        
        logging.info("📊 Analyzing model comparison results...")
        
        # Group results by model
        model_results = {}
        for result in self.results:
            if result.model not in model_results:
                model_results[result.model] = []
            model_results[result.model].append(result)
        
        # Calculate model statistics
        model_stats = {}
        for model, results in model_results.items():
            successful_results = [r for r in results if r.success]
            
            if successful_results:
                avg_quality = sum(r.quality_score for r in successful_results) / len(successful_results)
                avg_response_time = sum(r.response_time_ms for r in successful_results) / len(successful_results)
                avg_tokens = sum(r.token_count for r in successful_results) / len(successful_results)
                success_rate = len(successful_results) / len(results)
            else:
                avg_quality = 0
                avg_response_time = 0
                avg_tokens = 0
                success_rate = 0
            
            model_stats[model] = {
                'total_tests': len(results),
                'successful_tests': len(successful_results),
                'success_rate': success_rate,
                'avg_quality_score': avg_quality,
                'avg_response_time_ms': avg_response_time,
                'avg_token_count': avg_tokens,
                'results': results
            }
        
        # Determine preference order (quality-weighted with speed)
        preference_scores = {}
        for model, stats in model_stats.items():
            # Quality is most important (50%), speed matters (30%), reliability (20%)
            quality_component = stats['avg_quality_score'] * 0.5
            
            # Speed component (faster is better, normalized)
            max_time = max(s['avg_response_time_ms'] for s in model_stats.values() if s['avg_response_time_ms'] > 0)
            speed_component = (1 - stats['avg_response_time_ms'] / max_time) * 0.3 if max_time > 0 else 0
            
            # Reliability component
            reliability_component = stats['success_rate'] * 0.2
            
            preference_scores[model] = quality_component + speed_component + reliability_component
        
        # Sort models by preference score
        ranked_models = sorted(preference_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(model_stats, ranked_models)
        
        # Create comprehensive report
        analysis_result = {
            'test_summary': {
                'total_tests': len(self.results),
                'models_tested': len(model_results),
                'scenarios_tested': len(self.test_scenarios)
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
        
        # Save results to file
        self._save_results(analysis_result)
        
        return analysis_result

    def _generate_recommendations(self, model_stats: Dict[str, Any], 
                                ranked_models: List[Tuple[str, float]]) -> Dict[str, Any]:
        """Generate specific recommendations for fallback configuration."""
        
        top_model = ranked_models[0][0]
        second_model = ranked_models[1][0] if len(ranked_models) > 1 else None
        
        recommendations = {
            'primary_recommendation': {
                'model': top_model,
                'reasoning': f"Highest preference score ({ranked_models[0][1]:.3f}) with best balance of quality, speed, and reliability"
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
            
            if stats['avg_quality_score'] > 0.8:
                insights.append("Excellent response quality")
            elif stats['avg_quality_score'] > 0.6:
                insights.append("Good response quality")
            else:
                insights.append("Needs quality improvement")
            
            if stats['avg_response_time_ms'] < 1000:
                insights.append("Very fast response times")
            elif stats['avg_response_time_ms'] < 2000:
                insights.append("Good response speed")
            else:
                insights.append("Slower response times")
            
            if stats['success_rate'] > 0.9:
                insights.append("Highly reliable")
            elif stats['success_rate'] > 0.7:
                insights.append("Generally reliable")
            else:
                insights.append("Reliability concerns")
            
            recommendations['model_insights'][model] = insights
        
        # Add configuration code snippet
        if second_model:
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
        with open(f'groq_model_analysis_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
        
        # Save summary report
        summary = self._create_summary_report(analysis_result)
        with open(f'groq_model_summary_{timestamp}.md', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logging.info(f"📄 Results saved to groq_model_analysis_{timestamp}.json and groq_model_summary_{timestamp}.md")

    def _create_summary_report(self, analysis_result: Dict[str, Any]) -> str:
        """Create a markdown summary report."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""# Groq Model Comparison Summary Report
Generated: {timestamp}

## Executive Summary

This report compares the performance of 4 Groq models using real Key Findings data and prompts from the Management Tools Analysis dashboard.

### Test Configuration
- **Models Tested**: {len(analysis_result['test_summary']['models_tested'])}
- **Scenarios**: {analysis_result['test_summary']['scenarios_tested']}
- **Total Tests**: {analysis_result['test_summary']['total_tests']}

## Model Ranking (Recommended Fallback Order)

"""
        
        for rank_info in analysis_result['preference_ranking']:
            model = rank_info['model']
            score = rank_info['preference_score']
            metrics = rank_info['key_metrics']
            
            report += f"""### {rank_info['rank']}. {model}

**Preference Score**: {score:.3f}

**Key Metrics**:
- Success Rate: {metrics['success_rate']:.1%}
- Average Quality: {metrics['avg_quality_score']:.3f}
- Average Response Time: {metrics['avg_response_time_ms']:.0f}ms
- Average Tokens: {metrics['avg_token_count']:.0f}

**Insights**: {', '.join(analysis_result['recommendations']['model_insights'][model])}

"""
        
        report += f"""## Recommendations

### Primary Model
**{analysis_result['recommendations']['primary_recommendation']['model']}**
- {analysis_result['recommendations']['primary_recommendation']['reasoning']}

### Recommended Fallback Order
1. {analysis_result['recommendations']['fallback_order'][0]}
2. {analysis_result['recommendations']['fallback_order'][1] if len(analysis_result['recommendations']['fallback_order']) > 1 else 'N/A'}
3. {analysis_result['recommendations']['fallback_order'][2] if len(analysis_result['recommendations']['fallback_order']) > 2 else 'N/A'}
4. {analysis_result['recommendations']['fallback_order'][3] if len(analysis_result['recommendations']['fallback_order']) > 3 else 'N/A'}

### Implementation
{analysis_result['recommendations'].get('code_update', 'No code changes needed')}

## Detailed Results

For complete detailed results, see the accompanying JSON file.

---
*Report generated by Groq Model Comparator*
"""
        
        return report

async def main():
    """Main execution function."""
    try:
        # Initialize comparator
        comparator = GroqModelComparator()
        
        # Run comparison
        results = await comparator.run_comparison()
        
        # Display summary
        if 'error' not in results:
            print("\n" + "="*60)
            print("GROQ MODEL COMPARISON COMPLETED")
            print("="*60)
            
            print("\nRECOMMENDED FALLBACK ORDER:")
            for i, model_info in enumerate(results['preference_ranking']):
                print(f"{i+1}. {model_info['model']} (Score: {model_info['preference_score']:.3f})")
            
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