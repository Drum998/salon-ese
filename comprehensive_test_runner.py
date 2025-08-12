#!/usr/bin/env python3
"""
Comprehensive Test Runner for Salon ESE
=======================================

This script runs all tests in the Salon ESE project, organized by category.
Individual test units can be easily commented out for selective testing.

Usage:
    python comprehensive_test_runner.py                    # Run all tests
    python comprehensive_test_runner.py --category core    # Run core tests only
    python comprehensive_test_runner.py --category admin   # Run admin tests only
    python comprehensive_test_runner.py --category hr      # Run HR tests only
    python comprehensive_test_runner.py --category ui      # Run UI tests only
    python comprehensive_test_runner.py --category analytics # Run analytics tests only
    python comprehensive_test_runner.py --help            # Show help

Docker Usage:
    docker exec -it salon-ese-web-1 python comprehensive_test_runner.py
"""

import sys
import subprocess
import os
import argparse
import time
from datetime import datetime

# Import test configuration
try:
    from test_config import get_enabled_tests, get_preset_tests, get_all_enabled_tests, TEST_SETTINGS, TEST_PRESETS
except ImportError:
    print("⚠️  Warning: test_config.py not found, using default configuration")
    # Fallback configuration if test_config.py is not available
    def get_enabled_tests(category):
        return []
    def get_preset_tests(preset_name):
        return []
    def get_all_enabled_tests():
        return {}
    TEST_SETTINGS = {'timeout_per_test': 300, 'timeout_pytest': 600}
    TEST_PRESETS = {}

class ComprehensiveTestRunner:
    """Comprehensive test runner for Salon ESE project."""
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
        # Load test categories from configuration
        self.test_categories = get_all_enabled_tests()
        
        # Fallback to default categories if configuration is empty
        if not self.test_categories:
            self.test_categories = {
                'core': {
                    'description': 'Core system functionality tests',
                    'tests': [
                        'test_db.py',
                        'test_models.py',
                        'test_new_models.py',
                        'test_template_filter.py',
                        'test_timezone.py',
                        'test_auth.py',
                    ]
                },
                'admin': {
                    'description': 'Admin panel and user management tests',
                    'tests': [
                        'test_admin.py',
                        'tests/test_auth.py',
                    ]
                },
                'hr': {
                    'description': 'HR system and employment management tests',
                    'tests': [
                        'test_hr_system.py',
                        'test_commission_system.py',
                        'test_analytics_system.py',
                        'tests/test_salon_settings.py',
                        'tests/test_work_patterns.py', 
                        'tests/test_employment_details.py',
                    ]
                },
                'ui': {
                    'description': 'User interface and navigation tests',
                    'tests': [
                        'test_sidebar_navigation.py',
                        'test_services_matrix.py',
                        'test_single_block_css.py',
                        'test_calendar_navigation.py',
                        'test_calendar_view.py',
                        'test_click_to_book.py',
                        'test_appointment_visibility.py',
                        'test_appointment_display.py',
                    ]
                },
                'analytics': {
                    'description': 'Analytics and reporting system tests',
                    'tests': [
                        'test_analytics_system.py',
                        'test_commission_system.py',
                    ]
                },
                'integration': {
                    'description': 'Integration and system-wide tests',
                    'tests': [
                        'test_salon_hours_integration.py',
                        'debug_tests.py',
                    ]
                }
            }
    
    def print_header(self):
        """Print the test runner header."""
        print("🧪" + "=" * 60)
        print("   COMPREHENSIVE TEST RUNNER - SALON ESE")
        print("=" * 62)
        print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Working Directory: {self.script_dir}")
        print(f"   Python Version: {sys.version}")
        print("=" * 62)
    
    def print_footer(self):
        """Print the test runner footer with summary."""
        print("\n" + "=" * 62)
        print("   TEST RUN SUMMARY")
        print("=" * 62)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASSED')
        failed_tests = total_tests - passed_tests
        
        print(f"   Total Tests Run: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            print(f"   Duration: {duration:.2f} seconds")
        
        print(f"   Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 62)
        
        # Print failed tests if any
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test_file, result in self.test_results.items():
                if result['status'] == 'FAILED':
                    print(f"   - {test_file}: {result.get('error', 'Unknown error')}")
        
        # Print passed tests
        if passed_tests > 0:
            print(f"\n✅ PASSED TESTS ({passed_tests}):")
            for test_file, result in self.test_results.items():
                if result['status'] == 'PASSED':
                    print(f"   - {test_file}")
    
    def run_single_test(self, test_file):
        """Run a single test file and return the result."""
        print(f"\n📋 Running: {test_file}")
        print("-" * 50)
        
        # Check if test file exists
        test_path = os.path.join(self.script_dir, test_file)
        if not os.path.exists(test_path):
            error_msg = f"Test file not found: {test_file}"
            print(f"❌ {error_msg}")
            return {
                'status': 'FAILED',
                'error': error_msg,
                'output': '',
                'duration': 0
            }
        
        start_time = time.time()
        timeout = TEST_SETTINGS.get('timeout_per_test', 300)
        
        try:
            # Run the test file
            result = subprocess.run([
                sys.executable, test_path
            ], capture_output=True, text=True, cwd=self.script_dir, timeout=timeout)
            
            duration = time.time() - start_time
            
            # Print output based on settings
            if TEST_SETTINGS.get('show_detailed_output', True):
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            
            # Determine status
            if result.returncode == 0:
                status = 'PASSED'
                print(f"✅ {test_file} - PASSED ({duration:.2f}s)")
            else:
                status = 'FAILED'
                print(f"❌ {test_file} - FAILED ({duration:.2f}s)")
            
            return {
                'status': status,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else '',
                'duration': duration
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            error_msg = f"Test timed out after {duration:.2f} seconds"
            print(f"❌ {test_file} - TIMEOUT ({duration:.2f}s)")
            return {
                'status': 'FAILED',
                'error': error_msg,
                'output': '',
                'duration': duration
            }
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Error running test: {str(e)}"
            print(f"❌ {test_file} - ERROR ({duration:.2f}s): {error_msg}")
            return {
                'status': 'FAILED',
                'error': error_msg,
                'output': '',
                'duration': duration
            }
    
    def run_category_tests(self, category):
        """Run all tests in a specific category."""
        if category not in self.test_categories:
            print(f"❌ Unknown test category: {category}")
            return
        
        category_info = self.test_categories[category]
        print(f"\n🎯 Running {category.upper()} Tests")
        print(f"   Description: {category_info['description']}")
        print(f"   Test Files: {len(category_info['tests'])}")
        print("=" * 62)
        
        for test_file in category_info['tests']:
            result = self.run_single_test(test_file)
            self.test_results[test_file] = result
    
    def run_all_tests(self):
        """Run all tests in all categories."""
        print("\n🚀 Running ALL Tests")
        print("=" * 62)
        
        for category, category_info in self.test_categories.items():
            print(f"\n📂 Category: {category.upper()}")
            print(f"   {category_info['description']}")
            print("-" * 40)
            
            for test_file in category_info['tests']:
                result = self.run_single_test(test_file)
                self.test_results[test_file] = result
    
    def run_pytest_tests(self):
        """Run pytest-based tests for coverage."""
        if not TEST_SETTINGS.get('run_pytest_coverage', True):
            print("\n🔬 Pytest tests skipped (disabled in configuration)")
            return
            
        print("\n🔬 Running Pytest Tests with Coverage")
        print("=" * 62)
        
        try:
            timeout = TEST_SETTINGS.get('timeout_pytest', 600)
            # Run pytest on the tests directory
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short', '--cov=app'
            ], capture_output=True, text=True, cwd=self.script_dir, timeout=timeout)
            
            if TEST_SETTINGS.get('show_detailed_output', True):
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            
            if result.returncode == 0:
                print("✅ Pytest tests completed successfully!")
            else:
                print("❌ Some pytest tests failed!")
                
        except Exception as e:
            print(f"❌ Error running pytest tests: {e}")
    
    def run_preset_tests(self, preset_name):
        """Run tests from a specific preset."""
        if preset_name not in TEST_PRESETS:
            print(f"❌ Unknown test preset: {preset_name}")
            return
        
        preset_info = TEST_PRESETS[preset_name]
        preset_tests = get_preset_tests(preset_name)
        
        print(f"\n🎯 Running {preset_name.upper()} Preset Tests")
        print(f"   Description: {preset_info['description']}")
        print(f"   Test Files: {len(preset_tests)}")
        print("=" * 62)
        
        for test_file in preset_tests:
            result = self.run_single_test(test_file)
            self.test_results[test_file] = result
            
            # Stop on first failure if configured
            if (result['status'] == 'FAILED' and 
                TEST_SETTINGS.get('stop_on_first_failure', False)):
                print(f"\n⚠️  Stopping on first failure: {test_file}")
                break
    
    def show_help(self):
        """Show help information."""
        print("🧪 Salon ESE Comprehensive Test Runner")
        print("=" * 50)
        print("Usage:")
        print("  python comprehensive_test_runner.py                    # Run all tests")
        print("  python comprehensive_test_runner.py --category core    # Run core tests only")
        print("  python comprehensive_test_runner.py --category admin   # Run admin tests only")
        print("  python comprehensive_test_runner.py --category hr      # Run HR tests only")
        print("  python comprehensive_test_runner.py --category ui      # Run UI tests only")
        print("  python comprehensive_test_runner.py --category analytics # Run analytics tests only")
        print("  python comprehensive_test_runner.py --category integration # Run integration tests only")
        print("  python comprehensive_test_runner.py --preset smoke     # Run smoke tests")
        print("  python comprehensive_test_runner.py --preset dev       # Run development tests")
        print("  python comprehensive_test_runner.py --preset prod      # Run production tests")
        print("  python comprehensive_test_runner.py --pytest           # Run pytest tests with coverage")
        print("  python comprehensive_test_runner.py --help             # Show this help")
        
        print("\nAvailable Test Categories:")
        for category, info in self.test_categories.items():
            print(f"  - {category}: {info['description']}")
            print(f"    Files: {', '.join(info['tests'])}")
        
        print("\nAvailable Test Presets:")
        for preset, info in TEST_PRESETS.items():
            print(f"  - {preset}: {info['description']}")
        
        print("\nConfiguration:")
        print(f"  - Test timeout: {TEST_SETTINGS.get('timeout_per_test', 300)}s per test")
        print(f"  - Pytest timeout: {TEST_SETTINGS.get('timeout_pytest', 600)}s")
        print(f"  - Stop on first failure: {TEST_SETTINGS.get('stop_on_first_failure', False)}")
        print(f"  - Show detailed output: {TEST_SETTINGS.get('show_detailed_output', True)}")
        
        print("\nDocker Usage:")
        print("  docker exec -it salon-ese-web-1 python comprehensive_test_runner.py")
        print("  docker exec -it salon-ese-web-1 python comprehensive_test_runner.py --category core")
        print("  docker exec -it salon-ese-web-1 python comprehensive_test_runner.py --preset smoke")
    
    def run(self, args):
        """Main run method."""
        self.start_time = time.time()
        
        try:
            self.print_header()
            
            if args.pytest:
                self.run_pytest_tests()
            elif args.preset:
                self.run_preset_tests(args.preset)
            elif args.category:
                self.run_category_tests(args.category)
            else:
                self.run_all_tests()
                # Also run pytest tests for coverage
                self.run_pytest_tests()
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Test run interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            self.end_time = time.time()
            self.print_footer()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Comprehensive Test Runner for Salon ESE')
    parser.add_argument('--category', choices=['core', 'admin', 'hr', 'ui', 'analytics', 'integration'],
                       help='Run tests from a specific category only')
    parser.add_argument('--preset', choices=['smoke', 'dev', 'prod'],
                       help='Run tests from a specific preset')
    parser.add_argument('--pytest', action='store_true',
                       help='Run pytest tests with coverage only')
    
    args = parser.parse_args()
    
    # Show help if requested
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        runner = ComprehensiveTestRunner()
        runner.show_help()
        return
    
    # Run tests
    runner = ComprehensiveTestRunner()
    runner.run(args)

if __name__ == '__main__':
    main()
