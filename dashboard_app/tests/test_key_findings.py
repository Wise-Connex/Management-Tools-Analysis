"""
Comprehensive test suite for Key Findings module
"""

import pytest
import asyncio
import os
import tempfile
import json
from unittest.mock import Mock, patch, AsyncMock
import pandas as pd
import numpy as np

# Import Key Findings modules
from key_findings.database_manager import KeyFindingsDBManager
from key_findings.ai_service import OpenRouterService
from key_findings.data_aggregator import DataAggregator
from key_findings.prompt_engineer import PromptEngineer
from key_findings.modal_component import KeyFindingsModal
from key_findings.key_findings_service import KeyFindingsService


class TestKeyFindingsDBManager:
    """Test database manager functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def db_manager(self, temp_db):
        """Create database manager instance"""
        return KeyFindingsDBManager(temp_db)
    
    def test_database_initialization(self, temp_db):
        """Test database initialization"""
        db = KeyFindingsDBManager(temp_db)
        assert os.path.exists(temp_db)
        assert db.verify_persistence() == True
    
    def test_scenario_hash_generation(self, db_manager):
        """Test scenario hash generation"""
        hash1 = db_manager.generate_scenario_hash("tool1", ["source1", "source2"], "es")
        hash2 = db_manager.generate_scenario_hash("tool1", ["source1", "source2"], "es")
        hash3 = db_manager.generate_scenario_hash("tool2", ["source1", "source2"], "es")
        
        assert hash1 == hash2  # Same scenario should generate same hash
        assert hash1 != hash3  # Different tool should generate different hash
        assert len(hash1) == 64  # SHA256 should be 64 characters
    
    def test_cache_report_storage_and_retrieval(self, db_manager):
        """Test caching and retrieving reports"""
        scenario_hash = "test_hash_123"
        report_data = {
            "principal_findings": [{"bullet_point": "Test finding", "reasoning": "Test reasoning"}],
            "pca_insights": {"dominant_components": "PC1"},
            "executive_summary": "Test summary",
            "generation_metadata": {"model_used": "test-model", "api_latency_ms": 1000}
        }
        
        # Test caching
        success = db_manager.cache_report(scenario_hash, "test_tool", ["source1"], report_data)
        assert success == True
        
        # Test retrieval
        cached_report = db_manager.get_cached_report(scenario_hash)
        assert cached_report is not None
        assert cached_report["executive_summary"] == "Test summary"
        assert cached_report["generation_metadata"]["model_used"] == "test-model"
    
    def test_performance_metrics_tracking(self, db_manager):
        """Test performance metrics tracking"""
        # Test recording model performance
        db_manager.record_model_performance(
            model_name="test-model",
            response_time_ms=1500,
            token_count=1000,
            success=True,
            user_satisfaction=4
        )
        
        # Test getting performance metrics
        metrics = db_manager.get_performance_metrics()
        assert len(metrics) > 0
        assert metrics[0]["model_name"] == "test-model"
        assert metrics[0]["response_time_ms"] == 1500
        assert metrics[0]["success"] == True


class TestOpenRouterService:
    """Test AI service functionality"""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance with test config"""
        config = {
            'models': ['openai/gpt-4o-mini', 'nvidia/llama-3.1-nemotron-70b-instruct'],
            'timeout': 30,
            'max_retries': 3
        }
        return OpenRouterService("test-api-key", config)
    
    def test_service_initialization(self, ai_service):
        """Test service initialization"""
        assert ai_service.api_key == "test-api-key"
        assert len(ai_service.models) == 2
        assert ai_service.timeout == 30
        assert ai_service.max_retries == 3
    
    @pytest.mark.asyncio
    async def test_generate_analysis_success(self, ai_service):
        """Test successful AI analysis generation"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "principal_findings": [{"bullet_point": "Test finding", "reasoning": "Test reasoning"}],
                        "pca_insights": {"dominant_components": "PC1"},
                        "executive_summary": "Test summary"
                    })
                }
            }]
        }
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            result = await ai_service.generate_analysis("Test prompt", "openai/gpt-4o-mini")
            
            assert result["success"] == True
            assert "principal_findings" in result["content"]
            assert result["model_used"] == "openai/gpt-4o-mini"
    
    @pytest.mark.asyncio
    async def test_generate_analysis_with_fallback(self, ai_service):
        """Test AI analysis with fallback model"""
        # Mock primary model failure, fallback success
        mock_primary_response = Mock()
        mock_primary_response.status_code = 500
        
        mock_fallback_response = Mock()
        mock_fallback_response.status_code = 200
        mock_fallback_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "principal_findings": [{"bullet_point": "Fallback finding", "reasoning": "Fallback reasoning"}],
                        "executive_summary": "Fallback summary"
                    })
                }
            }]
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = [mock_primary_response, mock_fallback_response]
            
            result = await ai_service.generate_analysis("Test prompt", "openai/gpt-4o-mini")
            
            assert result["success"] == True
            assert result["model_used"] == "nvidia/llama-3.1-nemotron-70b-instruct"
    
    def test_cost_calculation(self, ai_service):
        """Test API cost calculation"""
        cost = ai_service.calculate_cost(1000, "openai/gpt-4o-mini")
        assert cost >= 0  # Cost should be non-negative
        assert isinstance(cost, float)


class TestDataAggregator:
    """Test data aggregation functionality"""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Create mock database manager"""
        mock_db = Mock()
        mock_db.get_data_for_keyword.return_value = (
            {
                "source1": pd.DataFrame({
                    'date': pd.date_range('2020-01-01', periods=12, freq='M'),
                    'value': np.random.randn(12)
                }).set_index('date'),
                "source2": pd.DataFrame({
                    'date': pd.date_range('2020-01-01', periods=12, freq='M'),
                    'value': np.random.randn(12)
                }).set_index('date')
            },
            ["Source 1", "Source 2"]
        )
        return mock_db
    
    @pytest.fixture
    def data_aggregator(self, mock_db_manager):
        """Create data aggregator instance"""
        return DataAggregator(mock_db_manager, Mock())
    
    def test_collect_analysis_data(self, data_aggregator):
        """Test data collection for analysis"""
        data = data_aggregator.collect_analysis_data("test_tool", ["source1", "source2"])
        
        assert "raw_data" in data
        assert "statistical_summary" in data
        assert "pca_insights" in data
        assert "trend_analysis" in data
        assert len(data["raw_data"]) > 0
    
    def test_extract_pca_insights(self, data_aggregator):
        """Test PCA insights extraction"""
        # Create sample data
        sample_data = pd.DataFrame({
            'source1': np.random.randn(100),
            'source2': np.random.randn(100),
            'source3': np.random.randn(100)
        })
        
        pca_insights = data_aggregator.extract_pca_insights({"combined_data": sample_data})
        
        assert "explained_variance_ratio" in pca_insights
        assert "principal_components" in pca_insights
        assert "dominant_patterns" in pca_insights
        assert len(pca_insights["explained_variance_ratio"]) <= 3  # Max 3 components for 3 sources
    
    def test_calculate_statistical_summaries(self, data_aggregator):
        """Test statistical summary calculation"""
        # Create sample data
        sample_data = pd.DataFrame({
            'source1': np.random.randn(100),
            'source2': np.random.randn(100)
        })
        
        stats = data_aggregator.calculate_statistical_summaries({"combined_data": sample_data})
        
        assert "descriptive_stats" in stats
        assert "correlation_matrix" in stats
        assert "distribution_analysis" in stats
        assert "source1" in stats["descriptive_stats"]
    
    def test_identify_trends_and_anomalies(self, data_aggregator):
        """Test trend and anomaly identification"""
        # Create sample data with trend
        dates = pd.date_range('2020-01-01', periods=24, freq='M')
        trend_data = np.arange(24) + np.random.randn(24) * 0.1
        sample_data = pd.DataFrame({
            'date': dates,
            'source1': trend_data
        }).set_index('date')
        
        trends = data_aggregator.identify_trends_and_anomalies({"combined_data": sample_data})
        
        assert "trend_analysis" in trends
        assert "anomaly_detection" in trends
        assert "seasonal_patterns" in trends


class TestPromptEngineer:
    """Test prompt engineering functionality"""
    
    @pytest.fixture
    def prompt_engineer(self):
        """Create prompt engineer instance"""
        return PromptEngineer('es')
    
    def test_create_analysis_prompt(self, prompt_engineer):
        """Test analysis prompt creation"""
        data = {
            "statistical_summary": {"mean": 1.0, "std": 0.5},
            "pca_insights": {"explained_variance": [0.7, 0.2, 0.1]},
            "trend_analysis": {"trend": "increasing"}
        }
        context = {
            "tool_name": "test_tool",
            "selected_sources": ["source1", "source2"],
            "language": "es"
        }
        
        prompt = prompt_engineer.create_analysis_prompt(data, context)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be a substantial prompt
        assert "análisis doctoral" in prompt.lower()  # Should contain doctoral-level instruction
        assert "test_tool" in prompt  # Should contain tool name
    
    def test_create_pca_focused_prompt(self, prompt_engineer):
        """Test PCA-focused prompt creation"""
        pca_data = {
            "explained_variance_ratio": [0.6, 0.3, 0.1],
            "principal_components": [[0.7, 0.3], [0.2, 0.8]],
            "dominant_patterns": ["temporal_trend", "seasonal_pattern"]
        }
        context = {
            "tool_name": "test_tool",
            "language": "es"
        }
        
        prompt = prompt_engineer.create_pca_focused_prompt(pca_data, context)
        
        assert isinstance(prompt, str)
        assert "análisis de componentes principales" in prompt.lower()
        assert "varianza explicada" in prompt.lower()
    
    def test_create_executive_summary_prompt(self, prompt_engineer):
        """Test executive summary prompt creation"""
        findings = {
            "principal_findings": [
                {"bullet_point": "Finding 1", "reasoning": "Reasoning 1"},
                {"bullet_point": "Finding 2", "reasoning": "Reasoning 2"}
            ],
            "pca_insights": {"dominant_components": "PC1"}
        }
        
        prompt = prompt_engineer.create_executive_summary_prompt(findings)
        
        assert isinstance(prompt, str)
        assert "resumen ejecutivo" in prompt.lower()
        assert "conclusiones clave" in prompt.lower()


class TestKeyFindingsModal:
    """Test modal component functionality"""
    
    @pytest.fixture
    def modal_component(self):
        """Create modal component instance"""
        return KeyFindingsModal(Mock(), Mock())
    
    def test_create_modal_layout(self, modal_component):
        """Test modal layout creation"""
        layout = modal_component.create_modal_layout()
        
        assert layout is not None
        # Should contain modal structure elements
        assert hasattr(layout, 'children')
    
    def test_create_findings_display(self, modal_component):
        """Test findings display creation"""
        report_data = {
            "principal_findings": [
                {"bullet_point": "Test finding", "reasoning": "Test reasoning", "confidence": "high"}
            ],
            "pca_insights": {"dominant_components": "PC1 explains 60% variance"},
            "executive_summary": "Test executive summary",
            "generation_metadata": {"model_used": "test-model", "api_latency_ms": 1500}
        }
        
        display = modal_component.create_findings_display(report_data)
        
        assert display is not None
        # Should contain structured findings display
        assert hasattr(display, 'children')
    
    def test_create_loading_state(self, modal_component):
        """Test loading state creation"""
        loading = modal_component.create_loading_state()
        
        assert loading is not None
        # Should contain loading indicator
        assert hasattr(loading, 'children')


class TestKeyFindingsService:
    """Test main service functionality"""
    
    @pytest.fixture
    def mock_service(self):
        """Create service with mocked dependencies"""
        with patch('key_findings.key_findings_service.KeyFindingsDBManager') as mock_db, \
             patch('key_findings.key_findings_service.OpenRouterService') as mock_ai, \
             patch('key_findings.key_findings_service.DataAggregator') as mock_aggregator, \
             patch('key_findings.key_findings_service.PromptEngineer') as mock_prompt, \
             patch('key_findings.key_findings_service.KeyFindingsModal') as mock_modal:
            
            service = KeyFindingsService()
            service.db_manager = mock_db.return_value
            service.ai_service = mock_ai.return_value
            service.data_aggregator = mock_aggregator.return_value
            service.prompt_engineer = mock_prompt.return_value
            service.modal_component = mock_modal.return_value
            
            yield service
    
    @pytest.mark.asyncio
    async def test_generate_key_findings_cache_hit(self, mock_service):
        """Test key findings generation with cache hit"""
        # Mock cache hit
        mock_service.db_manager.generate_scenario_hash.return_value = "test_hash"
        mock_service.db_manager.get_cached_report.return_value = {
            "principal_findings": [{"bullet_point": "Cached finding"}],
            "executive_summary": "Cached summary"
        }
        
        result = await mock_service.generate_key_findings("test_tool", ["source1"], "es")
        
        assert result["success"] == True
        assert result["cached"] == True
        assert "Cached finding" in str(result)
    
    @pytest.mark.asyncio
    async def test_generate_key_findings_cache_miss(self, mock_service):
        """Test key findings generation with cache miss"""
        # Mock cache miss
        mock_service.db_manager.generate_scenario_hash.return_value = "test_hash"
        mock_service.db_manager.get_cached_report.return_value = None
        
        # Mock data aggregation
        mock_service.data_aggregator.collect_analysis_data.return_value = {
            "statistical_summary": {"mean": 1.0},
            "pca_insights": {"explained_variance": [0.7, 0.3]}
        }
        
        # Mock AI service
        mock_service.ai_service.generate_analysis.return_value = {
            "success": True,
            "content": {
                "principal_findings": [{"bullet_point": "New finding"}],
                "executive_summary": "New summary"
            },
            "model_used": "test-model"
        }
        
        # Mock prompt engineering
        mock_service.prompt_engineer.create_analysis_prompt.return_value = "Test prompt"
        
        result = await mock_service.generate_key_findings("test_tool", ["source1"], "es")
        
        assert result["success"] == True
        assert result["cached"] == False
        assert "New finding" in str(result)
        
        # Verify caching was called
        mock_service.db_manager.cache_report.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_key_findings_force_refresh(self, mock_service):
        """Test key findings generation with force refresh"""
        # Mock existing cache
        mock_service.db_manager.generate_scenario_hash.return_value = "test_hash"
        mock_service.db_manager.get_cached_report.return_value = {
            "principal_findings": [{"bullet_point": "Old cached finding"}]
        }
        
        # Mock new AI response
        mock_service.ai_service.generate_analysis.return_value = {
            "success": True,
            "content": {
                "principal_findings": [{"bullet_point": "Fresh finding"}],
                "executive_summary": "Fresh summary"
            },
            "model_used": "test-model"
        }
        
        result = await mock_service.generate_key_findings(
            "test_tool", ["source1"], "es", force_refresh=True
        )
        
        assert result["success"] == True
        assert result["cached"] == False
        assert "Fresh finding" in str(result)
    
    def test_get_performance_metrics(self, mock_service):
        """Test performance metrics retrieval"""
        mock_service.db_manager.get_performance_metrics.return_value = [
            {"model_name": "test-model", "response_time_ms": 1500}
        ]
        
        metrics = mock_service.get_performance_metrics()
        
        assert metrics is not None
        assert len(metrics) > 0
        mock_service.db_manager.get_performance_metrics.assert_called_once()
    
    def test_update_user_feedback(self, mock_service):
        """Test user feedback update"""
        mock_service.db_manager.update_user_feedback.return_value = True
        
        result = mock_service.update_user_feedback("test_hash", 5, "Great analysis!")
        
        assert result == True
        mock_service.db_manager.update_user_feedback.assert_called_once_with(
            "test_hash", 5, "Great analysis!"
        )


# Integration Tests
class TestKeyFindingsIntegration:
    """Integration tests for Key Findings module"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Initialize real service components
            db_manager = KeyFindingsDBManager(db_path)
            
            # Mock AI service for integration test
            with patch('key_findings.key_findings_service.OpenRouterService') as mock_ai_class:
                mock_ai = Mock()
                mock_ai.generate_analysis.return_value = {
                    "success": True,
                    "content": {
                        "principal_findings": [
                            {"bullet_point": "Integration test finding", "reasoning": "Test reasoning"}
                        ],
                        "pca_insights": {"dominant_components": "PC1"},
                        "executive_summary": "Integration test summary"
                    },
                    "model_used": "test-model"
                }
                mock_ai_class.return_value = mock_ai
                
                service = KeyFindingsService()
                service.db_manager = db_manager
                
                # Test generation
                result = await service.generate_key_findings(
                    "test_tool", ["source1"], "es"
                )
                
                assert result["success"] == True
                assert result["cached"] == False
                
                # Test caching - second call should hit cache
                result2 = await service.generate_key_findings(
                    "test_tool", ["source1"], "es"
                )
                
                assert result2["success"] == True
                assert result2["cached"] == True
                
                # Verify database persistence
                assert db_manager.verify_persistence() == True
                
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


# Performance Tests
class TestKeyFindingsPerformance:
    """Performance tests for Key Findings module"""
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test caching performance"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = KeyFindingsDBManager(db_path)
            
            # Test multiple cache operations
            import time
            start_time = time.time()
            
            for i in range(100):
                scenario_hash = f"test_hash_{i}"
                report_data = {
                    "executive_summary": f"Test summary {i}",
                    "generation_metadata": {"model_used": "test-model"}
                }
                db_manager.cache_report(scenario_hash, "test_tool", ["source1"], report_data)
            
            cache_time = time.time() - start_time
            
            # Test retrieval performance
            start_time = time.time()
            for i in range(100):
                scenario_hash = f"test_hash_{i}"
                db_manager.get_cached_report(scenario_hash)
            
            retrieval_time = time.time() - start_time
            
            # Performance assertions
            assert cache_time < 5.0  # Should cache 100 reports in < 5 seconds
            assert retrieval_time < 1.0  # Should retrieve 100 reports in < 1 second
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])