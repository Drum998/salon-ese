#!/usr/bin/env python3
"""
Test Configuration for Salon ESE Comprehensive Test Runner
==========================================================

This file allows you to easily enable/disable individual test units
by commenting out the test files you don't want to run.

To disable a test, simply comment out the line with a # symbol.
To enable a test, remove the # symbol.

Example:
    # 'test_db.py',                    # This test is DISABLED
    'test_models.py',                  # This test is ENABLED
"""

# Test Configuration - Easy Enable/Disable
# ========================================

# Core System Tests
# ----------------
CORE_TESTS = [
    'test_db.py',                      # Database connectivity tests
    'test_models.py',                  # Database model tests
    # 'test_new_models.py',            # New model functionality tests (temporarily disabled)
    'test_template_filter.py',         # Template filter tests
    'test_timezone.py',                # Timezone handling tests
    'test_auth.py',                    # Authentication tests
]

# Admin Panel Tests
# ----------------
ADMIN_TESTS = [
    'test_admin.py',                   # Admin panel functionality tests
    'tests/test_auth.py',              # Admin authentication tests
]

# HR System Tests
# --------------
HR_TESTS = [
    'test_hr_system.py',               # HR system functionality tests
    'test_commission_system.py',       # Commission calculation tests
    'test_analytics_system.py',        # Analytics system tests
    'tests/test_salon_settings.py',    # Salon settings tests
    'tests/test_work_patterns.py',     # Work patterns tests
    'tests/test_employment_details.py', # Employment details tests
]

# User Interface Tests
# -------------------
UI_TESTS = [
    'test_sidebar_navigation.py',      # Sidebar navigation tests
    'test_services_matrix.py',         # Services matrix tests
    'test_single_block_css.py',        # CSS styling tests
    'test_calendar_navigation.py',     # Calendar navigation tests
    'test_calendar_view.py',           # Calendar view tests
    'test_click_to_book.py',           # Click-to-book functionality tests
    'test_appointment_visibility.py',  # Appointment visibility tests
    'test_appointment_display.py',     # Appointment display tests
]

# Analytics Tests
# --------------
ANALYTICS_TESTS = [
    'test_analytics_system.py',        # Analytics system tests
    'test_commission_system.py',       # Commission analytics tests
]

# Integration Tests
# ----------------
INTEGRATION_TESTS = [
    'test_salon_hours_integration.py', # Salon hours integration tests
    'debug_tests.py',                  # Debug and system-wide tests
]

# Test Categories Configuration
# ============================
TEST_CATEGORIES = {
    'core': {
        'description': 'Core system functionality tests',
        'tests': CORE_TESTS,
        'enabled': True,  # Set to False to disable entire category
    },
    'admin': {
        'description': 'Admin panel and user management tests',
        'tests': ADMIN_TESTS,
        'enabled': True,
    },
    'hr': {
        'description': 'HR system and employment management tests',
        'tests': HR_TESTS,
        'enabled': True,
    },
    'ui': {
        'description': 'User interface and navigation tests',
        'tests': UI_TESTS,
        'enabled': True,
    },
    'analytics': {
        'description': 'Analytics and reporting system tests',
        'tests': ANALYTICS_TESTS,
        'enabled': True,
    },
    'integration': {
        'description': 'Integration and system-wide tests',
        'tests': INTEGRATION_TESTS,
        'enabled': True,
    }
}

# Test Execution Settings
# ======================
TEST_SETTINGS = {
    'timeout_per_test': 300,           # 5 minutes per test
    'timeout_pytest': 600,             # 10 minutes for pytest
    'run_pytest_coverage': True,       # Run pytest with coverage
    'show_detailed_output': True,      # Show detailed test output
    'stop_on_first_failure': False,    # Continue running tests even if one fails
}

# Quick Test Presets
# =================
# Uncomment the preset you want to use for quick testing

# QUICK_TEST_PRESET = 'smoke'          # Basic functionality tests only
# QUICK_TEST_PRESET = 'core'           # Core system tests only
# QUICK_TEST_PRESET = 'hr'             # HR system tests only
# QUICK_TEST_PRESET = 'ui'             # UI tests only

# Smoke Test Configuration (for quick validation)
SMOKE_TESTS = [
    'test_db.py',                      # Database connectivity
    'test_auth.py',                    # Authentication
    'test_admin.py',                   # Admin functionality
    'tests/test_salon_settings.py',    # Basic settings
]

# Development Test Configuration (for active development)
DEV_TESTS = [
    'test_db.py',
    'test_models.py',
    'test_auth.py',
    'test_admin.py',
    'tests/test_salon_settings.py',
    'tests/test_work_patterns.py',
    'test_hr_system.py',
]

# Production Test Configuration (for deployment validation)
PROD_TESTS = [
    'test_db.py',
    'test_models.py',
    'test_auth.py',
    'test_admin.py',
    'test_hr_system.py',
    'test_commission_system.py',
    'test_analytics_system.py',
    'tests/test_salon_settings.py',
    'tests/test_work_patterns.py',
    'tests/test_employment_details.py',
    'test_sidebar_navigation.py',
    'test_services_matrix.py',
    'test_calendar_navigation.py',
    'test_calendar_view.py',
    'test_appointment_visibility.py',
    'test_appointment_display.py',
    'test_salon_hours_integration.py',
]

# Test Presets
TEST_PRESETS = {
    'smoke': {
        'description': 'Quick smoke tests for basic functionality',
        'tests': SMOKE_TESTS,
    },
    'dev': {
        'description': 'Development tests for active development',
        'tests': DEV_TESTS,
    },
    'prod': {
        'description': 'Full production test suite',
        'tests': PROD_TESTS,
    }
}

def get_enabled_tests(category):
    """Get enabled tests for a category, filtering out commented tests."""
    if category not in TEST_CATEGORIES:
        return []
    
    category_config = TEST_CATEGORIES[category]
    if not category_config.get('enabled', True):
        return []
    
    # Filter out commented tests (lines starting with #)
    enabled_tests = []
    for test in category_config['tests']:
        if not test.strip().startswith('#'):
            enabled_tests.append(test.strip())
    
    return enabled_tests

def get_preset_tests(preset_name):
    """Get tests for a specific preset."""
    if preset_name not in TEST_PRESETS:
        return []
    
    preset_config = TEST_PRESETS[preset_name]
    enabled_tests = []
    for test in preset_config['tests']:
        if not test.strip().startswith('#'):
            enabled_tests.append(test.strip())
    
    return enabled_tests

def get_all_enabled_tests():
    """Get all enabled tests across all categories."""
    all_tests = {}
    for category in TEST_CATEGORIES:
        enabled_tests = get_enabled_tests(category)
        if enabled_tests:
            all_tests[category] = {
                'description': TEST_CATEGORIES[category]['description'],
                'tests': enabled_tests
            }
    return all_tests
