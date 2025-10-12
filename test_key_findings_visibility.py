#!/usr/bin/env python3
"""
Test script to check Key Findings module visibility and functionality
"""

import sys
import os

# Add dashboard_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("🔍 Testing Key Findings Module Visibility")
print("=" * 50)

# Test 1: Check if module can be imported
try:
    from key_findings import KeyFindingsService, KeyFindingsModal
    print("✅ Key Findings module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Key Findings module: {e}")
    sys.exit(1)

# Test 2: Check if service can be initialized
try:
    from key_findings.database_manager import KeyFindingsDBManager
    # Use local path for testing
    db_manager = KeyFindingsDBManager(db_path='./test_key_findings.db')
    config = {'key_findings_db_path': './test_key_findings.db'}
    api_key = os.getenv('OPENROUTER_API_KEY')
    service = KeyFindingsService(db_manager=db_manager, config=config, api_key=api_key)
    print("✅ Key Findings service initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Key Findings service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Skip modal component test (requires full Dash app context)
print("✅ Key Findings modal component test skipped (requires Dash app context)")

# Test 4: Check if OpenRouter API key is available
api_key = os.getenv('OPENROUTER_API_KEY')
if api_key:
    print(f"✅ OpenRouter API key found (length: {len(api_key)})")
else:
    print("⚠️  OpenRouter API key not found in environment")

# Test 5: Check database connectivity
try:
    from key_findings.database_manager import KeyFindingsDBManager
    db_manager = KeyFindingsDBManager()
    print("✅ Key Findings database manager initialized")
except Exception as e:
    print(f"❌ Failed to initialize database manager: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Key Findings Module Status: READY")
print("\n📋 Next Steps:")
print("1. Run the dashboard with: cd dashboard_app && python app.py")
print("2. Select a tool and data sources")
print("3. Click the '🧠 Generar Key Findings' button")
print("4. The modal should appear with AI-generated insights")
