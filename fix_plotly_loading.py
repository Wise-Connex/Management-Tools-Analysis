#!/usr/bin/env python3
"""
Fix Plotly Loading Issues

Script to resolve Plotly.js component loading errors that prevent
the Key Findings modal from appearing.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_plotly_installation():
    """Check if Plotly is properly installed."""
    print("🔍 Checking Plotly installation...")

    try:
        import plotly
        print(f"✅ Plotly version: {plotly.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False

def fix_dash_plotly_components():
    """Fix Dash Plotly component loading issues."""
    print("\n🔧 Fixing Dash Plotly components...")

    # Try to reinstall dash-core-components which includes Plotly
    try:
        print("Reinstalling dash-core-components...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--force-reinstall",
            "dash-core-components"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ dash-core-components reinstalled successfully")
        else:
            print(f"⚠️ dash-core-components reinstall had issues: {result.stderr}")

    except Exception as e:
        print(f"❌ Failed to reinstall dash-core-components: {e}")

def clear_dash_cache():
    """Clear Dash component cache to force reloading."""
    print("\n🗑️ Clearing Dash component cache...")

    # Common Dash cache locations
    cache_dirs = [
        Path.home() / ".dash" / "core-components",
        Path.home() / ".cache" / "dash",
        ".dash_cache",
        "__pycache__"
    ]

    for cache_dir in cache_dirs:
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir)
                print(f"✅ Cleared cache: {cache_dir}")
            except Exception as e:
                print(f"⚠️ Could not clear {cache_dir}: {e}")

def check_dash_version():
    """Check Dash version and compatibility."""
    print("\n📦 Checking Dash version...")

    try:
        import dash
        print(f"✅ Dash version: {dash.__version__}")

        # Check for version compatibility issues
        major_version = int(dash.__version__.split('.')[0])
        if major_version >= 2:
            print("✅ Dash version is compatible")
            return True
        else:
            print("⚠️ Dash version may be too old")
            return False

    except ImportError as e:
        print(f"❌ Dash import failed: {e}")
        return False

def create_simple_plotly_test():
    """Create a simple test to verify Plotly works."""
    print("\n🧪 Creating Plotly test...")

    test_code = '''
import plotly.graph_objects as go
import dash
from dash import dcc, html

# Create a simple figure
fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 1, 2]))
print("✅ Plotly figure created successfully")

# Test Dash component
app = dash.Dash(__name__)
app.layout = html.Div([dcc.Graph(figure=fig)])
print("✅ Dash app with Plotly component created successfully")
'''

    try:
        with open("test_plotly_simple.py", "w") as f:
            f.write(test_code)
        print("✅ Plotly test file created: test_plotly_simple.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create test file: {e}")
        return False

def run_plotly_test():
    """Run the simple Plotly test."""
    print("\n🏃 Running Plotly test...")

    try:
        result = subprocess.run([
            sys.executable, "test_plotly_simple.py"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ Plotly test passed!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Plotly test failed:")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("⚠️ Plotly test timed out")
        return False
    except Exception as e:
        print(f"❌ Failed to run Plotly test: {e}")
        return False

def generate_fix_report():
    """Generate a report of fixes applied."""
    print("\n📄 Generating fix report...")

    report = {
        'timestamp': datetime.now().isoformat(),
        'plotly_working': check_plotly_installation(),
        'dash_version': None,
        'recommendations': []
    }

    try:
        import dash
        report['dash_version'] = dash.__version__
    except:
        pass

    # Add recommendations
    if not report['plotly_working']:
        report['recommendations'].append("Reinstall Plotly: pip install plotly")

    if not report['dash_version']:
        report['recommendations'].append("Reinstall Dash: pip install dash")

    print("✅ Fix report generated")
    return report

def main():
    """Main function to fix Plotly loading issues."""
    print("🔧 PLOTLY LOADING ISSUE FIXER")
    print("=" * 50)

    # Step 1: Check current installation
    plotly_ok = check_plotly_installation()
    dash_ok = check_dash_version()

    # Step 2: Clear cache
    clear_dash_cache()

    # Step 3: Fix components if needed
    if not plotly_ok or not dash_ok:
        fix_dash_plotly_components()

    # Step 4: Create and run test
    create_simple_plotly_test()
    test_passed = run_plotly_test()

    # Step 5: Generate report
    report = generate_fix_report()

    print("\n" + "=" * 50)
    print("🎯 FIX SUMMARY")
    print("=" * 50)

    if test_passed:
        print("✅ Plotly loading issues should be resolved!")
        print("💡 Restart the dashboard and test the Key Findings modal")
    else:
        print("⚠️ Plotly issues persist. Manual intervention needed:")
        print("   1. Try: pip install --upgrade plotly dash dash-core-components")
        print("   2. Clear browser cache and restart")
        print("   3. Check for conflicting Plotly installations")

    print(f"\n📊 Test results:")
    print(f"   Plotly: {'✅ Working' if plotly_ok else '❌ Broken'}")
    print(f"   Dash: {'✅ Working' if dash_ok else '❌ Broken'}")
    print(f"   Integration: {'✅ Working' if test_passed else '❌ Broken'}")

if __name__ == "__main__":
    from datetime import datetime
    main()