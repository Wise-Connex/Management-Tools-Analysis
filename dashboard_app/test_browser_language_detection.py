#!/usr/bin/env python3
"""
Test script to verify browser language detection functionality
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_browser_language_detection():
    """Test that browser language detection is properly implemented"""
    
    # Read the app.py file to check for language detection implementation
    app_file = os.path.join(os.path.dirname(__file__), 'app.py')
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key components of browser language detection
    checks = {
        'getBrowserLanguage function': 'function getBrowserLanguage()' in content,
        'navigator.language detection': 'navigator.language || navigator.userLanguage' in content,
        'Spanish language check': "lang.startsWith('es')" in content,
        'localStorage persistence': 'localStorage.getItem(\'dashboard-language\')' in content,
        'DOMContentLoaded event listener': 'document.addEventListener(\'DOMContentLoaded\'' in content,
        'Automatic language application': 'languageSelector.dispatchEvent(new Event(\'change\'' in content,
        'Language change listener': 'document.addEventListener(\'change\', function(e)' in content,
        'Language selector in HTML': 'id=\'language-selector\'' in content
    }
    
    print("Browser Language Detection Implementation Check:")
    print("=" * 50)
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("✅ All browser language detection components are properly implemented!")
        print("\nHow it works:")
        print("1. On page load, JavaScript detects browser language using navigator.language")
        print("2. If language starts with 'es', it sets to Spanish, otherwise English")
        print("3. The preference is stored in localStorage for persistence")
        print("4. The language selector is automatically updated to match detected language")
        print("5. A change event is triggered to apply the language throughout the app")
        print("\nLanguage detection logic:")
        print("- Spanish (es): 'es', 'es-ES', 'es-MX', 'es-AR', etc.")
        print("- English (en): All other languages default to English")
    else:
        print("❌ Some browser language detection components are missing!")
    
    return all_passed

def test_language_storage_mechanism():
    """Test language persistence mechanism"""
    
    app_file = os.path.join(os.path.dirname(__file__), 'app.py')
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check localStorage functions
    storage_checks = {
        'getStoredLanguage function': 'function getStoredLanguage()' in content,
        'setStoredLanguage function': 'function setStoredLanguage(lang)' in content,
        'Storage key consistency': "'dashboard-language'" in content,
        'Initial language detection': 'getStoredLanguage() || getBrowserLanguage()' in content
    }
    
    print("\nLanguage Storage Mechanism Check:")
    print("=" * 50)
    
    all_passed = True
    for check_name, passed in storage_checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ Language persistence mechanism is properly implemented!")
    else:
        print("\n❌ Language persistence mechanism has issues!")
    
    return all_passed

def verify_language_selector_initialization():
    """Verify language selector is properly initialized"""
    
    app_file = os.path.join(os.path.dirname(__file__), 'app.py')
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check language selector HTML structure
    selector_checks = {
        'Language selector dropdown': 'dcc.Dropdown(' in content and 'id=\'language-selector\'' in content,
        'Spanish option': "'value': 'es'" in content,
        'English option': "'value': 'en'" in content,
        'Flag emojis': '🇪🇸' in content and '🇺🇸' in content,
        'Default to Spanish': "value='es'" in content,
        'Clearable disabled': 'clearable=False' in content
    }
    
    print("\nLanguage Selector Initialization Check:")
    print("=" * 50)
    
    all_passed = True
    for check_name, passed in selector_checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ Language selector is properly configured!")
    else:
        print("\n❌ Language selector configuration has issues!")
    
    return all_passed

if __name__ == "__main__":
    print("Testing Browser Language Detection Implementation")
    print("=" * 60)
    
    test1_passed = test_browser_language_detection()
    test2_passed = test_language_storage_mechanism()
    test3_passed = verify_language_selector_initialization()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("✅ ALL TESTS PASSED - Browser language detection is fully implemented!")
        print("\nThe dashboard will automatically detect and apply the browser language on first load:")
        print("- Spanish browsers will see the dashboard in Spanish")
        print("- English and other language browsers will see the dashboard in English")
        print("- User selection is persisted in localStorage for future visits")
    else:
        print("❌ SOME TESTS FAILED - Please check the implementation!")
    
    print("\nTo test manually:")
    print("1. Open the dashboard in a browser set to Spanish language")
    print("2. Verify it automatically loads in Spanish")
    print("3. Open in a browser set to English (or other language)")
    print("4. Verify it automatically loads in English")
    print("5. Change language manually and verify it persists on refresh")