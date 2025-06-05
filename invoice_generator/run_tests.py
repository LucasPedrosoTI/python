#!/usr/bin/env python3
"""
Simple test runner for the invoice generator tests.
Run this script to execute all unit tests using pytest.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests using pytest."""
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', 
            '-v', 
            '--tb=short'
        ], cwd=os.path.dirname(__file__))
        
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == '__main__':
    print("Running Invoice Generator Unit Tests...")
    print("=" * 50)
    exit_code = run_tests()
    print("=" * 50)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    sys.exit(exit_code) 