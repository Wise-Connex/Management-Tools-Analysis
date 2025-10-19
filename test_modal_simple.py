#!/usr/bin/env python3
import sys
from pathlib import Path

# Add dashboard_app to path
dashboard_app_path = Path(__file__).parent / "dashboard_app"
sys.path.insert(0, str(dashboard_app_path))

try:
    print("Testing modal functionality...")

    # Import the modal component
    from key_findings.modal_component import KeyFindingsModal

    # Create mock objects for testing
    class MockApp:
        def callback(self, *args, **kwargs):
            pass

    class MockLanguageStore:
        def __init__(self):
            self.data = {'language': 'es'}

    # Test modal creation
    mock_app = MockApp()
    mock_language_store = MockLanguageStore()

    modal = KeyFindingsModal(mock_app, mock_language_store)
    print("✅ Modal component created successfully")

    # Test modal layout generation
    layout = modal.get_modal_layout()
    print(f"✅ Modal layout generated successfully (type: {type(layout)})")

    print("🎉 Modal test completed successfully!")

except Exception as e:
    print(f"❌ Modal test failed: {e}")
    import traceback
    traceback.print_exc()
