#!/usr/bin/env python3
"""
Fix Key Findings Modal Dependencies

Script to resolve the dependency and database issues preventing
the Key Findings modal from functioning properly.
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def install_missing_dependencies():
    """Install missing Python dependencies."""
    print("🔧 Installing missing dependencies...")

    dependencies = [
        'propcache',
        'aiohttp',
        'openai',
        'dash-bootstrap-components',
        'plotly',
        'pandas',
        'numpy',
        'scipy',
        'scikit-learn'
    ]

    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', dep],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {dep} installed successfully")
            else:
                print(f"❌ Failed to install {dep}: {result.stderr}")
        except Exception as e:
            print(f"❌ Error installing {dep}: {e}")

def create_basic_databases():
    """Create basic database files if they don't exist."""
    print("\n🗄️ Creating database files...")

    dashboard_app_path = Path("dashboard_app")
    dashboard_app_path.mkdir(exist_ok=True)

    # Create main database
    main_db_path = dashboard_app_path / "management_tools.db"
    if not main_db_path.exists():
        print("Creating main management_tools database...")
        try:
            conn = sqlite3.connect(str(main_db_path))
            cursor = conn.cursor()

            # Create basic tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS temporal_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool TEXT NOT NULL,
                    source TEXT NOT NULL,
                    date TEXT NOT NULL,
                    value REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Insert some sample tools
            tools = [
                ('Benchmarking', 'Benchmarking', 'Performance Management'),
                ('Calidad Total', 'Total Quality Management', 'Quality Management'),
                ('Cuadro de Mando Integral', 'Balanced Scorecard', 'Performance Management'),
                ('Gestión de la Cadena de Suministro', 'Supply Chain Management', 'Operations'),
                ('Innovación Colaborativa', 'Collaborative Innovation', 'Innovation')
            ]

            cursor.executemany(
                'INSERT OR IGNORE INTO tools (name, display_name, category) VALUES (?, ?, ?)',
                tools
            )

            conn.commit()
            conn.close()
            print("✅ Main database created successfully")

        except Exception as e:
            print(f"❌ Failed to create main database: {e}")
    else:
        print("✅ Main database already exists")

    # Create key findings database
    key_findings_db_path = dashboard_app_path / "key_findings.db"
    if not key_findings_db_path.exists():
        print("Creating key_findings database...")
        try:
            conn = sqlite3.connect(str(key_findings_db_path))
            cursor = conn.cursor()

            # Create key findings tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS key_findings_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT NOT NULL,
                    sources TEXT NOT NULL,
                    language TEXT NOT NULL,
                    findings TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    analysis_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')

            conn.commit()
            conn.close()
            print("✅ Key findings database created successfully")

        except Exception as e:
            print(f"❌ Failed to create key findings database: {e}")
    else:
        print("✅ Key findings database already exists")

def verify_dashboard_app_structure():
    """Verify and create necessary dashboard_app structure."""
    print("\n📁 Verifying dashboard_app structure...")

    dashboard_app_path = Path("dashboard_app")
    required_dirs = [
        'key_findings',
        'assets'
    ]

    for dir_name in required_dirs:
        dir_path = dashboard_app_path / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✅ {dir_name}/ directory exists")

def test_imports_after_fix():
    """Test imports after fixing dependencies."""
    print("\n🧪 Testing imports after fixes...")

    # Add dashboard_app to path
    dashboard_app_path = Path("dashboard_app")
    if str(dashboard_app_path) not in sys.path:
        sys.path.insert(0, str(dashboard_app_path))

    try:
        print("Testing main app import...")
        import app
        print("✅ Main app imported successfully")
    except Exception as e:
        print(f"❌ Failed to import main app: {e}")

    try:
        print("Testing Key Findings modal import...")
        from key_findings.modal_component import KeyFindingsModal
        print("✅ KeyFindingsModal imported successfully")
    except Exception as e:
        print(f"❌ Failed to import KeyFindingsModal: {e}")

    try:
        print("Testing AI service import...")
        from key_findings.ai_service import get_openrouter_service
        print("✅ AI service imported successfully")
    except Exception as e:
        print(f"❌ Failed to import AI service: {e}")

def create_simple_modal_test():
    """Create a simple test to verify modal functionality."""
    print("\n🧪 Creating simple modal test...")

    test_script = """#!/usr/bin/env python3
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
"""

    with open("test_modal_simple.py", "w") as f:
        f.write(test_script)

    print("✅ Simple modal test created: test_modal_simple.py")

def main():
    """Main function to fix modal dependencies."""
    print("🔧 KEY FINDINGS MODAL DEPENDENCY FIXER")
    print("=" * 50)

    # Step 1: Install missing dependencies
    install_missing_dependencies()

    # Step 2: Create database files
    create_basic_databases()

    # Step 3: Verify directory structure
    verify_dashboard_app_structure()

    # Step 4: Test imports
    test_imports_after_fix()

    # Step 5: Create simple test
    create_simple_modal_test()

    print("\n" + "=" * 50)
    print("🎯 DEPENDENCY FIXING COMPLETED")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run: python test_modal_simple.py")
    print("2. If successful, start the dashboard: cd dashboard_app && python app.py")
    print("3. Test the Key Findings button functionality")
    print("4. If issues persist, check the browser console for JavaScript errors")

if __name__ == "__main__":
    main()