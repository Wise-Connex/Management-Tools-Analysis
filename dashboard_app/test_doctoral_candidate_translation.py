#!/usr/bin/env python3
"""
Test script to verify the "Investigador Principal" -> "Doctoral Candidate" translation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the translation functions
from translations import get_text

def test_doctoral_candidate_translation():
    """Test that the translation for 'Investigador Principal' is correct"""
    print("Testing 'Investigador Principal' translation...")
    
    # Test Spanish translation
    spanish = get_text('principal_investigator', 'es')
    print(f"Spanish: '{spanish}'")
    assert spanish == 'Investigador Principal:', f"Expected 'Investigador Principal:', got '{spanish}'"
    
    # Test English translation (should be "Doctoral Candidate:")
    english = get_text('principal_investigator', 'en')
    print(f"English: '{english}'")
    assert english == 'Doctoral Candidate:', f"Expected 'Doctoral Candidate:', got '{english}'"
    
    print("\n✅ 'Investigador Principal' translation verified successfully!")
    print("   - Spanish: 'Investigador Principal:'")
    print("   - English: 'Doctoral Candidate:'")
    print("\nThis correctly reflects that the doctoral candidate is the author of the thesis.")

if __name__ == "__main__":
    test_doctoral_candidate_translation()