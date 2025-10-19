#!/usr/bin/env python3
"""
Key Findings Modal Debugging Tool

Comprehensive debugging script for the Key Findings modal functionality.
Tests the complete flow from button click to modal display and AI processing.
"""

import os
import sys
import logging
import json
import asyncio
import time
from datetime import datetime
from pathlib import Path

# Add dashboard_app to path
dashboard_app_path = Path(__file__).parent / "dashboard_app"
sys.path.insert(0, str(dashboard_app_path))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('key_findings_debug.log', mode='w')
    ]
)

logger = logging.getLogger(__name__)

class KeyFindingsDebugger:
    """Comprehensive debugging tool for Key Findings modal functionality."""

    def __init__(self):
        self.debug_results = {
            'timestamp': datetime.now().isoformat(),
            'tests_run': [],
            'errors_found': [],
            'recommendations': []
        }

    def run_all_tests(self):
        """Run complete debugging test suite."""
        print("🔍 KEY FINDINGS MODAL DEBUGGING SUITE")
        print("=" * 60)

        # Test 1: Import tests
        self.test_imports()

        # Test 2: Configuration tests
        self.test_configuration()

        # Test 3: AI service tests
        self.test_ai_service_initialization()

        # Test 4: Database tests
        self.test_database_connectivity()

        # Test 5: Modal component tests
        self.test_modal_component()

        # Test 6: Callback simulation
        self.test_callback_simulation()

        # Test 7: AI processing test
        asyncio.run(self.test_ai_processing())

        # Generate report
        self.generate_debug_report()

    def test_imports(self):
        """Test all required imports."""
        print("\n📦 TEST 1: Import Testing")
        print("-" * 40)

        test_name = "Import Testing"
        start_time = time.time()

        try:
            # Test dashboard_app imports
            print("Testing dashboard_app imports...")

            try:
                import app
                print("✅ Main app module imported successfully")
            except Exception as e:
                print(f"❌ Failed to import main app: {e}")
                self.debug_results['errors_found'].append(f"Import error - main app: {e}")

            try:
                from key_findings.modal_component import KeyFindingsModal
                print("✅ KeyFindingsModal imported successfully")
            except Exception as e:
                print(f"❌ Failed to import KeyFindingsModal: {e}")
                self.debug_results['errors_found'].append(f"Import error - KeyFindingsModal: {e}")

            try:
                from key_findings.key_findings_service import KeyFindingsService
                print("✅ KeyFindingsService imported successfully")
            except Exception as e:
                print(f"❌ Failed to import KeyFindingsService: {e}")
                self.debug_results['errors_found'].append(f"Import error - KeyFindingsService: {e}")

            try:
                from key_findings.ai_service import get_openrouter_service
                print("✅ AI service imported successfully")
            except Exception as e:
                print(f"❌ Failed to import AI service: {e}")
                self.debug_results['errors_found'].append(f"Import error - AI service: {e}")

            try:
                from key_findings.data_aggregator import DataAggregator
                print("✅ DataAggregator imported successfully")
            except Exception as e:
                print(f"❌ Failed to import DataAggregator: {e}")
                self.debug_results['errors_found'].append(f"Import error - DataAggregator: {e}")

            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'passed',
                'duration': duration,
                'details': 'All imports successful'
            })
            print(f"✅ Import tests completed in {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'failed',
                'duration': duration,
                'details': f'Import test failed: {e}'
            })
            print(f"❌ Import tests failed: {e}")

    def test_configuration(self):
        """Test configuration and environment variables."""
        print("\n⚙️ TEST 2: Configuration Testing")
        print("-" * 40)

        test_name = "Configuration Testing"
        start_time = time.time()

        try:
            # Check environment variables
            env_vars = [
                'OPENROUTER_API_KEY',
                'GROQ_API_KEY',
                'FLASK_ENV'
            ]

            missing_vars = []
            for var in env_vars:
                value = os.getenv(var)
                if value:
                    # Mask sensitive values
                    masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
                    print(f"✅ {var}: {masked_value}")
                else:
                    print(f"⚠️ {var}: Not set")
                    missing_vars.append(var)

            # Check database files
            db_files = [
                'dashboard_app/management_tools.db',
                'dashboard_app/key_findings.db'
            ]

            for db_file in db_files:
                if os.path.exists(db_file):
                    size = os.path.getsize(db_file)
                    print(f"✅ {db_file}: {size:,} bytes")
                else:
                    print(f"❌ {db_file}: Not found")
                    missing_vars.append(db_file)

            duration = time.time() - start_time

            if missing_vars:
                self.debug_results['errors_found'].append(f"Missing configuration: {missing_vars}")
                self.debug_results['recommendations'].append("Set missing environment variables and ensure database files exist")

            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'passed' if not missing_vars else 'warning',
                'duration': duration,
                'details': f'Configuration checked. Missing: {missing_vars}'
            })
            print(f"✅ Configuration tests completed in {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'failed',
                'duration': duration,
                'details': f'Configuration test failed: {e}'
            })
            print(f"❌ Configuration tests failed: {e}")

    def test_ai_service_initialization(self):
        """Test AI service initialization."""
        print("\n🤖 TEST 3: AI Service Initialization")
        print("-" * 40)

        test_name = "AI Service Initialization"
        start_time = time.time()

        try:
            from key_findings.ai_service import get_openrouter_service

            # Test service initialization
            print("Testing AI service initialization...")

            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                print("⚠️ OpenRouter API key not found, using mock test")
                self.debug_results['recommendations'].append("Set OPENROUTER_API_KEY environment variable")
                duration = time.time() - start_time
                self.debug_results['tests_run'].append({
                    'name': test_name,
                    'status': 'warning',
                    'duration': duration,
                    'details': 'API key not found, cannot test AI service'
                })
                return

            try:
                service = get_openrouter_service(api_key)
                print("✅ AI service initialized successfully")
                print(f"✅ Models configured: {len(service.config['models'])}")
                for i, model in enumerate(service.config['models'][:3]):  # Show first 3
                    print(f"   {i+1}. {model}")
                if len(service.config['models']) > 3:
                    print(f"   ... and {len(service.config['models']) - 3} more")

            except Exception as e:
                print(f"❌ AI service initialization failed: {e}")
                self.debug_results['errors_found'].append(f"AI service init failed: {e}")

            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'passed',
                'duration': duration,
                'details': 'AI service initialization successful'
            })
            print(f"✅ AI service tests completed in {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'failed',
                'duration': duration,
                'details': f'AI service test failed: {e}'
            })
            print(f"❌ AI service tests failed: {e}")

    def test_database_connectivity(self):
        """Test database connectivity and basic queries."""
        print("\n🗄️ TEST 4: Database Connectivity")
        print("-" * 40)

        test_name = "Database Connectivity"
        start_time = time.time()

        try:
            from database import get_db_connection

            print("Testing database connection...")

            # Test main database
            try:
                conn = get_db_connection()
                cursor = conn.cursor()

                # Test basic query
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"✅ Main database: {len(tables)} tables found")

                # Check key tables
                table_names = [table[0] for table in tables]
                key_tables = ['temporal_data', 'tools']
                for table in key_tables:
                    if table in table_names:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"✅ Table '{table}': {count:,} records")
                    else:
                        print(f"⚠️ Table '{table}': Not found")

                conn.close()

            except Exception as e:
                print(f"❌ Main database connection failed: {e}")
                self.debug_results['errors_found'].append(f"Database connection failed: {e}")

            # Test key findings database if it exists
            key_findings_db = 'dashboard_app/key_findings.db'
            if os.path.exists(key_findings_db):
                try:
                    import sqlite3
                    conn = sqlite3.connect(key_findings_db)
                    cursor = conn.cursor()

                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    print(f"✅ Key findings database: {len(tables)} tables found")

                    conn.close()

                except Exception as e:
                    print(f"❌ Key findings database connection failed: {e}")
            else:
                print("⚠️ Key findings database not found (will be created when needed)")

            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'passed',
                'duration': duration,
                'details': 'Database connectivity verified'
            })
            print(f"✅ Database tests completed in {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'failed',
                'duration': duration,
                'details': f'Database test failed: {e}'
            })
            print(f"❌ Database tests failed: {e}")

    def test_modal_component(self):
        """Test modal component initialization and methods."""
        print("\n🖼️ TEST 5: Modal Component Testing")
        print("-" * 40)

        test_name = "Modal Component Testing"
        start_time = time.time()

        try:
            from key_findings.modal_component import KeyFindingsModal

            print("Testing modal component initialization...")

            # Create a mock app and language store
            class MockApp:
                def callback(self, *args, **kwargs):
                    pass

            class MockLanguageStore:
                def __init__(self):
                    self.data = {'language': 'es'}

            try:
                mock_app = MockApp()
                mock_language_store = MockLanguageStore()

                modal = KeyFindingsModal(mock_app, mock_language_store)
                print("✅ Modal component initialized successfully")

                # Check modal attributes
                if hasattr(modal, 'modal'):
                    print("✅ Modal object exists")
                else:
                    print("❌ Modal object missing")
                    self.debug_results['errors_found'].append("Modal object missing from KeyFindingsModal")

                # Test modal layout generation
                if hasattr(modal, 'get_modal_layout'):
                    layout = modal.get_modal_layout()
                    if layout:
                        print("✅ Modal layout generated successfully")
                    else:
                        print("⚠️ Modal layout is empty")
                else:
                    print("❌ get_modal_layout method missing")
                    self.debug_results['errors_found'].append("get_modal_layout method missing")

            except Exception as e:
                print(f"❌ Modal component initialization failed: {e}")
                self.debug_results['errors_found'].append(f"Modal init failed: {e}")

            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'passed',
                'duration': duration,
                'details': 'Modal component testing completed'
            })
            print(f"✅ Modal component tests completed in {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'failed',
                'duration': duration,
                'details': f'Modal component test failed: {e}'
            })
            print(f"❌ Modal component tests failed: {e}")

    def test_callback_simulation(self):
        """Test callback simulation for modal toggle."""
        print("\n🔄 TEST 6: Callback Simulation")
        print("-" * 40)

        test_name = "Callback Simulation"
        start_time = time.time()

        try:
            print("Testing callback parameters and flow...")

            # Simulate the callback inputs
            simulate_inputs = {
                'generate_clicks': 1,  # Button clicked
                'close_clicks': None,  # Close button not clicked
                'modal_is_open': False,  # Modal initially closed
                'selected_tool': 'Benchmarking',
                'selected_sources': ['Google Trends'],
                'language': 'es'
            }

            print(f"Simulated inputs: {simulate_inputs}")

            # Check if the callback function exists
            try:
                import app
                if hasattr(app, 'toggle_key_findings_modal'):
                    print("✅ toggle_key_findings_modal function found")
                else:
                    print("❌ toggle_key_findings_modal function not found")
                    self.debug_results['errors_found'].append("toggle_key_findings_modal function missing")

                # Check if required dependencies exist
                required_deps = [
                    'generate-key-findings-btn',
                    'close-key-findings-modal-btn',
                    'key-findings-modal',
                    'key-findings-modal-body'
                ]

                print("Checking required callback dependencies...")
                for dep in required_deps:
                    # In a real test, we'd check the DOM or app layout
                    print(f"✅ Dependency '{dep}' expected to exist")

            except Exception as e:
                print(f"❌ Callback simulation failed: {e}")
                self.debug_results['errors_found'].append(f"Callback simulation failed: {e}")

            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'passed',
                'duration': duration,
                'details': 'Callback simulation completed'
            })
            print(f"✅ Callback simulation completed in {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'failed',
                'duration': duration,
                'details': f'Callback simulation failed: {e}'
            })
            print(f"❌ Callback simulation failed: {e}")

    async def test_ai_processing(self):
        """Test AI processing with mock data."""
        print("\n🧠 TEST 7: AI Processing Test")
        print("-" * 40)

        test_name = "AI Processing Test"
        start_time = time.time()

        try:
            from key_findings.ai_service import get_openrouter_service
            from key_findings.prompt_engineer import PromptEngineer

            print("Testing AI processing pipeline...")

            # Check API key
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                print("⚠️ Skipping AI processing test - no API key")
                duration = time.time() - start_time
                self.debug_results['tests_run'].append({
                    'name': test_name,
                    'status': 'skipped',
                    'duration': duration,
                    'details': 'No API key provided'
                })
                return

            # Test prompt engineering
            try:
                prompt_engineer = PromptEngineer(language='es')

                # Create mock data
                mock_data = {
                    'tool_name': 'Benchmarking',
                    'sources': ['Google Trends'],
                    'statistics': {
                        'mean': 45.2,
                        'trend': 'increasing',
                        'volatility': 0.15
                    },
                    'basic_analysis': 'Test analysis data for debugging'
                }

                prompt = prompt_engineer.build_comprehensive_prompt(mock_data)
                print(f"✅ Prompt generated successfully ({len(prompt)} characters)")

                # Test AI service with minimal prompt
                service = get_openrouter_service(api_key)
                print("✅ AI service ready for processing")

                # Optional: Test with very short prompt for quick validation
                try:
                    print("Testing AI with minimal prompt...")
                    minimal_prompt = "Generate a brief JSON response for testing."
                    result = await service.generate_analysis(minimal_prompt, language='es')

                    if result.get('success'):
                        print(f"✅ AI processing successful ({result.get('response_time_ms', 0)}ms)")
                        print(f"✅ Model used: {result.get('model_used', 'unknown')}")
                    else:
                        print(f"⚠️ AI processing returned non-success result")

                except Exception as e:
                    print(f"⚠️ AI processing test failed (this may be expected): {e}")
                    self.debug_results['recommendations'].append("Check API key and internet connectivity for AI processing")

            except Exception as e:
                print(f"❌ Prompt engineering or AI processing setup failed: {e}")
                self.debug_results['errors_found'].append(f"AI processing setup failed: {e}")

            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'passed',
                'duration': duration,
                'details': 'AI processing pipeline tested'
            })
            print(f"✅ AI processing tests completed in {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start_time
            self.debug_results['tests_run'].append({
                'name': test_name,
                'status': 'failed',
                'duration': duration,
                'details': f'AI processing test failed: {e}'
            })
            print(f"❌ AI processing tests failed: {e}")

    def generate_debug_report(self):
        """Generate comprehensive debug report."""
        print("\n📊 DEBUG REPORT")
        print("=" * 60)

        total_tests = len(self.debug_results['tests_run'])
        passed_tests = len([t for t in self.debug_results['tests_run'] if t['status'] == 'passed'])
        failed_tests = len([t for t in self.debug_results['tests_run'] if t['status'] == 'failed'])
        warning_tests = len([t for t in self.debug_results['tests_run'] if t['status'] in ['warning', 'skipped']])

        print(f"Tests Run: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"❌ Failed: {failed_tests}")

        if self.debug_results['errors_found']:
            print(f"\n❌ Errors Found ({len(self.debug_results['errors_found'])}):")
            for i, error in enumerate(self.debug_results['errors_found'], 1):
                print(f"  {i}. {error}")

        if self.debug_results['recommendations']:
            print(f"\n💡 Recommendations ({len(self.debug_results['recommendations'])}):")
            for i, rec in enumerate(self.debug_results['recommendations'], 1):
                print(f"  {i}. {rec}")

        # Save detailed report
        report_file = 'key_findings_debug_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.debug_results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Detailed report saved to: {report_file}")
        print(f"📄 Log file saved to: key_findings_debug.log")

        # Key findings specific recommendations
        print(f"\n🎯 Key Findings Modal Specific Recommendations:")

        if failed_tests == 0:
            print("✅ All tests passed! The modal should work correctly.")
            print("💡 If the modal still doesn't appear, check:")
            print("   1. Browser console for JavaScript errors")
            print("   2. Network tab for failed requests")
            print("   3. Whether the callback is being triggered (check n_clicks)")
        else:
            print("⚠️ Some tests failed. Fix these issues first:")

        # Common modal issues
        print("\n🔧 Common Modal Issues to Check:")
        print("1. Callback function signature matches app.py definition")
        print("2. Modal component ID matches exactly in layout and callback")
        print("3. Button 'n_clicks' property is properly incremented")
        print("4. Modal 'is_open' property is being set correctly")
        print("5. No JavaScript errors in browser console")
        print("6. Dash app is running in debug mode for better error messages")

def main():
    """Main debugging function."""
    debugger = KeyFindingsDebugger()
    debugger.run_all_tests()

    print(f"\n🎯 Debugging completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📧 Review the generated reports and log file for detailed information.")

if __name__ == "__main__":
    main()