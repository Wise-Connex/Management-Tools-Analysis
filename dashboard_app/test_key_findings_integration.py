#!/usr/bin/env python3
"""
End-to-end integration test for Key Findings module
"""

import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

def test_module_imports():
    """Test that all Key Findings modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from key_findings.database_manager import KeyFindingsDBManager
        from key_findings.ai_service import OpenRouterService
        from key_findings.data_aggregator import DataAggregator
        from key_findings.prompt_engineer import PromptEngineer
        from key_findings.modal_component import KeyFindingsModal
        from key_findings.key_findings_service import KeyFindingsService
        from key_findings.docker_config import DockerPersistenceConfig
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_operations():
    """Test database manager operations"""
    print("\n🗄️ Testing database operations...")
    
    try:
        from key_findings.database_manager import KeyFindingsDBManager
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = KeyFindingsDBManager(db_path)
        
        # Test database initialization
        assert db.verify_persistence() == True
        print("✅ Database initialization successful")
        
        # Test scenario hash generation
        hash1 = db.generate_scenario_hash("test_tool", ["source1", "source2"], "es")
        hash2 = db.generate_scenario_hash("test_tool", ["source1", "source2"], "es")
        assert hash1 == hash2
        print("✅ Scenario hash generation consistent")
        
        # Test caching
        report_data = {
            "principal_findings": [{"bullet_point": "Test finding", "reasoning": "Test reasoning"}],
            "executive_summary": "Test summary",
            "generation_metadata": {"model_used": "test-model"}
        }
        
        success = db.cache_report(hash1, "test_tool", ["source1"], report_data)
        assert success == True
        print("✅ Report caching successful")
        
        # Test retrieval
        cached_report = db.get_cached_report(hash1)
        assert cached_report is not None
        assert cached_report["executive_summary"] == "Test summary"
        print("✅ Report retrieval successful")
        
        # Test performance metrics
        db.record_model_performance("test-model", 1500, 1000, True, None, 4)
        metrics = db.get_performance_metrics()
        assert len(metrics) > 0
        print("✅ Performance metrics tracking successful")
        
        # Cleanup
        os.unlink(db_path)
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_prompt_engineering():
    """Test prompt engineering functionality"""
    print("\n📝 Testing prompt engineering...")
    
    try:
        from key_findings.prompt_engineer import PromptEngineer
        
        # Test Spanish prompts
        prompter_es = PromptEngineer('es')
        prompt_es = prompter_es.create_analysis_prompt(
            {"statistical_summary": {"mean": 1.0}},
            {"tool_name": "test_tool", "language": "es"}
        )
        assert isinstance(prompt_es, str)
        assert len(prompt_es) > 100
        print("✅ Spanish prompt generation successful")
        
        # Test English prompts
        prompter_en = PromptEngineer('en')
        prompt_en = prompter_en.create_analysis_prompt(
            {"statistical_summary": {"mean": 1.0}},
            {"tool_name": "test_tool", "language": "en"}
        )
        assert isinstance(prompt_en, str)
        assert len(prompt_en) > 100
        print("✅ English prompt generation successful")
        
        # Test PCA-focused prompts
        pca_prompt = prompter_es.create_pca_focused_prompt(
            {"explained_variance_ratio": [0.7, 0.3]},
            {"tool_name": "test_tool"}
        )
        assert isinstance(pca_prompt, str)
        assert "componentes principales" in pca_prompt.lower()
        print("✅ PCA-focused prompt generation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt engineering test failed: {e}")
        return False

def test_docker_configuration():
    """Test Docker configuration"""
    print("\n🐳 Testing Docker configuration...")
    
    try:
        from key_findings.docker_config import DockerPersistenceConfig
        
        config = DockerPersistenceConfig()
        
        # Test directory creation
        results = config.ensure_persistence_directories()
        assert all(results.values())
        print("✅ Directory creation successful")
        
        # Test environment detection
        is_docker = config._is_docker_environment()
        print(f"✅ Environment detection: {'Docker' if is_docker else 'Host'}")
        
        # Test verification
        verification = config.verify_persistence_setup()
        assert 'verified' in verification
        print("✅ Configuration verification successful")
        
        # Test Docker Compose generation
        compose_config = config.get_docker_compose_config()
        assert 'services:' in compose_config
        assert 'dashboard-app:' in compose_config
        print("✅ Docker Compose configuration generation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Docker configuration test failed: {e}")
        return False

async def test_ai_service():
    """Test AI service functionality (mock)"""
    print("\n🤖 Testing AI service...")
    
    try:
        from key_findings.ai_service import OpenRouterService
        
        # Test service initialization
        service = OpenRouterService("test-api-key", {
            'models': ['openai/gpt-4o-mini'],
            'timeout': 30,
            'max_retries': 3
        })
        assert service.api_key == "test-api-key"
        print("✅ AI service initialization successful")
        
        # Test cost calculation
        cost = service.calculate_cost(1000, "openai/gpt-4o-mini")
        assert cost >= 0
        print("✅ Cost calculation successful")
        
        # Test performance stats
        stats = service.get_performance_stats()
        assert isinstance(stats, dict)
        print("✅ Performance statistics successful")
        
        return True
        
    except Exception as e:
        print(f"❌ AI service test failed: {e}")
        return False

def test_modal_component():
    """Test modal component functionality"""
    print("\n🖼️ Testing modal component...")
    
    try:
        from key_findings.modal_component import KeyFindingsModal
        
        # Create mock app and language store
        class MockApp:
            pass
        
        class MockLanguageStore:
            def get(self, key):
                return 'es'
        
        modal = KeyFindingsModal(MockApp(), MockLanguageStore())
        
        # Test modal layout creation
        layout = modal.create_modal_layout()
        assert layout is not None
        print("✅ Modal layout creation successful")
        
        # Test findings display
        report_data = {
            "principal_findings": [
                {"bullet_point": "Test finding", "reasoning": "Test reasoning", "confidence": "high"}
            ],
            "executive_summary": "Test summary",
            "generation_metadata": {"model_used": "test-model", "api_latency_ms": 1500}
        }
        
        display = modal.create_findings_display(report_data)
        assert display is not None
        print("✅ Findings display creation successful")
        
        # Test loading state
        loading = modal.create_loading_state()
        assert loading is not None
        print("✅ Loading state creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Modal component test failed: {e}")
        return False

async def test_service_integration():
    """Test complete service integration"""
    print("\n🔗 Testing service integration...")
    
    try:
        from key_findings.key_findings_service import KeyFindingsService
        from key_findings.database_manager import KeyFindingsDBManager
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Create mock database manager
        class MockDBManager:
            def get_keywords_list(self):
                return ["test_tool"]
        
        # Initialize service
        service = KeyFindingsService(
            MockDBManager(),
            api_key="test-key",
            config={'key_findings_db_path': db_path}
        )
        
        # Test performance metrics
        metrics = service.get_performance_metrics()
        assert 'service_metrics' in metrics
        assert 'database_metrics' in metrics
        print("✅ Service performance metrics successful")
        
        # Test health check
        health = service.verify_service_health()
        assert 'overall_status' in health
        assert 'components' in health
        print("✅ Service health check successful")
        
        # Cleanup
        os.unlink(db_path)
        return True
        
    except Exception as e:
        print(f"❌ Service integration test failed: {e}")
        return False

def test_app_integration():
    """Test integration with main app"""
    print("\n🚀 Testing app integration...")
    
    try:
        # Test that app can be imported with Key Findings
        import app
        
        # Check if Key Findings is available
        assert hasattr(app, 'key_findings_service') or app.KEY_FINDINGS_AVAILABLE
        print("✅ Key Findings integration in app successful")
        
        # Check if modal is in layout
        assert 'key-findings-modal' in str(app.layout)
        print("✅ Key Findings modal in layout successful")
        
        return True
        
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

async def run_all_tests():
    """Run all integration tests"""
    print("🧪 Key Findings Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_module_imports),
        ("Database Operations", test_database_operations),
        ("Prompt Engineering", test_prompt_engineering),
        ("Docker Configuration", test_docker_configuration),
        ("AI Service", test_ai_service),
        ("Modal Component", test_modal_component),
        ("Service Integration", test_service_integration),
        ("App Integration", test_app_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Key Findings module is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    # Run integration tests
    success = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)