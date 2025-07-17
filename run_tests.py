#!/usr/bin/env python3
"""
Test runner script for Salon ESE new features.
This script runs unit tests for salon settings and work patterns functionality.
"""

import sys
import subprocess
import os

def run_tests():
    """Run all unit tests for the new features."""
    print("🧪 Running Salon ESE Unit Tests")
    print("=" * 50)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the project directory
    os.chdir(script_dir)
    
    # Test files to run
    test_files = [
        'tests/test_salon_settings.py',
        'tests/test_work_patterns.py', 
        'tests/test_employment_details.py'
    ]
    
    # Run each test file
    for test_file in test_files:
        print(f"\n📋 Running tests in {test_file}")
        print("-" * 40)
        
        try:
            # Run pytest on the specific test file
            result = subprocess.run([
                sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short'
            ], capture_output=True, text=True, cwd=script_dir)
            
            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            # Check if tests passed
            if result.returncode == 0:
                print(f"✅ {test_file} - All tests passed!")
            else:
                print(f"❌ {test_file} - Some tests failed!")
                
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
    
    # Run all tests together for coverage
    print(f"\n📊 Running all tests for coverage")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short', '--cov=app'
        ], capture_output=True, text=True, cwd=script_dir)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        if result.returncode == 0:
            print("✅ All tests completed successfully!")
        else:
            print("❌ Some tests failed!")
            
    except Exception as e:
        print(f"❌ Error running coverage tests: {e}")

def run_specific_test(test_name):
    """Run a specific test by name."""
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 50)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', f'tests/test_{test_name}.py', '-v', '--tb=short'
        ], capture_output=True, text=True, cwd=script_dir)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        if result.returncode == 0:
            print(f"✅ {test_name} tests passed!")
        else:
            print(f"❌ {test_name} tests failed!")
            
    except Exception as e:
        print(f"❌ Error running {test_name} tests: {e}")

def show_test_help():
    """Show help information for the test runner."""
    print("🧪 Salon ESE Test Runner")
    print("=" * 30)
    print("Usage:")
    print("  python run_tests.py                    # Run all tests")
    print("  python run_tests.py salon_settings     # Run salon settings tests")
    print("  python run_tests.py work_patterns      # Run work patterns tests")
    print("  python run_tests.py employment_details # Run employment details tests")
    print("  python run_tests.py help               # Show this help")
    print("\nAvailable test suites:")
    print("  - salon_settings: Tests for salon settings functionality")
    print("  - work_patterns: Tests for work patterns functionality")
    print("  - employment_details: Tests for employment details functionality")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'help':
            show_test_help()
        elif command in ['salon_settings', 'work_patterns', 'employment_details']:
            run_specific_test(command)
        else:
            print(f"❌ Unknown test suite: {command}")
            show_test_help()
    else:
        run_tests() 