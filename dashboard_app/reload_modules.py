"""
Module Reloader for Development Environment

Forces reload of Key Findings modules to pick up changes during development.
"""

import sys
import importlib

def reload_key_findings_modules():
    """Force reload of Key Findings modules to pick up changes."""
    modules_to_reload = [
        'dashboard_app.key_findings.prompt_engineer',
        'dashboard_app.key_findings.ai_service',
        'dashboard_app.key_findings.data_aggregator',
        'dashboard_app.key_findings.unified_ai_service'
    ]

    for module_name in modules_to_reload:
        if module_name in sys.modules:
            print(f"🔄 Reloading {module_name}")
            importlib.reload(sys.modules[module_name])

    print("✅ Key Findings modules reloaded successfully")

if __name__ == "__main__":
    reload_key_findings_modules()