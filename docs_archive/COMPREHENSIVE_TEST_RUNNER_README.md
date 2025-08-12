# Salon ESE Comprehensive Test Runner

## Overview

The Comprehensive Test Runner is a powerful testing system designed to organize and execute all tests in the Salon ESE project. It provides flexible test execution options, easy configuration management, and comprehensive reporting.

## Features

- **Organized Test Categories**: Tests are grouped into logical categories (core, admin, hr, ui, analytics, integration)
- **Easy Configuration**: Simple commenting system to enable/disable individual tests
- **Test Presets**: Pre-configured test suites for different scenarios (smoke, dev, prod)
- **Docker Integration**: Optimized for running in Docker containers
- **Comprehensive Reporting**: Detailed test results with timing and error information
- **Flexible Execution**: Run all tests, specific categories, or custom presets

## Quick Start

### 1. Using the Docker Script (Recommended)

```bash
# Run all tests
./run_tests_docker.sh

# Run smoke tests (quick validation)
./run_tests_docker.sh smoke

# Run development tests
./run_tests_docker.sh dev

# Run production tests
./run_tests_docker.sh prod

# Run specific category
./run_tests_docker.sh core
./run_tests_docker.sh hr
./run_tests_docker.sh ui

# Show help
./run_tests_docker.sh help
```

### 2. Using Python Directly

```bash
# Run all tests
docker exec -it salon-ese-web-1 python comprehensive_test_runner.py

# Run specific category
docker exec -it salon-ese-web-1 python comprehensive_test_runner.py --category core

# Run preset
docker exec -it salon-ese-web-1 python comprehensive_test_runner.py --preset smoke

# Run pytest only
docker exec -it salon-ese-web-1 python comprehensive_test_runner.py --pytest

# Show help
docker exec -it salon-ese-web-1 python comprehensive_test_runner.py --help
```

## Test Categories

### Core Tests
- **Description**: Core system functionality tests
- **Tests**: Database connectivity, models, authentication, timezone handling
- **Files**: `test_db.py`, `test_models.py`, `test_new_models.py`, `test_template_filter.py`, `test_timezone.py`, `test_auth.py`

### Admin Tests
- **Description**: Admin panel and user management tests
- **Tests**: Admin functionality, user management, role management
- **Files**: `test_admin.py`, `tests/test_auth.py`

### HR Tests
- **Description**: HR system and employment management tests
- **Tests**: HR functionality, commission calculations, employment details, work patterns
- **Files**: `test_hr_system.py`, `test_commission_system.py`, `test_analytics_system.py`, `tests/test_salon_settings.py`, `tests/test_work_patterns.py`, `tests/test_employment_details.py`

### UI Tests
- **Description**: User interface and navigation tests
- **Tests**: Navigation, calendar views, appointment display, services matrix
- **Files**: `test_sidebar_navigation.py`, `test_services_matrix.py`, `test_single_block_css.py`, `test_calendar_navigation.py`, `test_calendar_view.py`, `test_click_to_book.py`, `test_appointment_visibility.py`, `test_appointment_display.py`

### Analytics Tests
- **Description**: Analytics and reporting system tests
- **Tests**: Analytics functionality, commission analytics, reporting
- **Files**: `test_analytics_system.py`, `test_commission_system.py`

### Integration Tests
- **Description**: Integration and system-wide tests
- **Tests**: System integration, salon hours integration, debug tests
- **Files**: `test_salon_hours_integration.py`, `debug_tests.py`

## Test Presets

### Smoke Tests
- **Purpose**: Quick validation of basic functionality
- **Use Case**: Fast feedback during development
- **Tests**: Database connectivity, authentication, admin functionality, basic settings

### Development Tests
- **Purpose**: Comprehensive testing during active development
- **Use Case**: Regular development workflow
- **Tests**: Core functionality, admin, settings, work patterns, HR system

### Production Tests
- **Purpose**: Full validation for deployment
- **Use Case**: Pre-deployment testing, release validation
- **Tests**: Complete test suite covering all functionality

## Configuration

### Easy Test Management

Edit `test_config.py` to enable/disable individual tests:

```python
# Core System Tests
CORE_TESTS = [
    'test_db.py',                      # Database connectivity tests
    # 'test_models.py',                # Comment out to disable
    'test_new_models.py',              # New model functionality tests
    'test_template_filter.py',         # Template filter tests
    'test_timezone.py',                # Timezone handling tests
    'test_auth.py',                    # Authentication tests
]
```

### Test Settings

Configure test execution behavior in `test_config.py`:

```python
TEST_SETTINGS = {
    'timeout_per_test': 300,           # 5 minutes per test
    'timeout_pytest': 600,             # 10 minutes for pytest
    'run_pytest_coverage': True,       # Run pytest with coverage
    'show_detailed_output': True,      # Show detailed test output
    'stop_on_first_failure': False,    # Continue running tests even if one fails
}
```

### Category Management

Enable/disable entire test categories:

```python
TEST_CATEGORIES = {
    'core': {
        'description': 'Core system functionality tests',
        'tests': CORE_TESTS,
        'enabled': True,  # Set to False to disable entire category
    },
    'ui': {
        'description': 'User interface and navigation tests',
        'tests': UI_TESTS,
        'enabled': False,  # Disable all UI tests
    }
}
```

## File Structure

```
salon-ese/
├── comprehensive_test_runner.py      # Main test runner
├── test_config.py                    # Test configuration
├── run_tests_docker.sh              # Docker execution script
├── COMPREHENSIVE_TEST_RUNNER_README.md # This documentation
├── tests/                           # Pytest-based tests
│   ├── test_salon_settings.py
│   ├── test_work_patterns.py
│   └── test_employment_details.py
├── test_*.py                        # Individual test files
└── run_tests.py                     # Legacy test runner
```

## Usage Examples

### Development Workflow

1. **Quick Validation** (during development):
   ```bash
   ./run_tests_docker.sh smoke
   ```

2. **Feature Testing** (when working on specific features):
   ```bash
   # Test HR features
   ./run_tests_docker.sh hr
   
   # Test UI features
   ./run_tests_docker.sh ui
   ```

3. **Full Testing** (before commits):
   ```bash
   ./run_tests_docker.sh dev
   ```

### Production Deployment

1. **Pre-deployment Testing**:
   ```bash
   ./run_tests_docker.sh prod
   ```

2. **Coverage Testing**:
   ```bash
   ./run_tests_docker.sh pytest
   ```

### Custom Testing

1. **Disable Specific Tests**:
   Edit `test_config.py` and comment out unwanted tests:
   ```python
   # 'test_appointment_display.py',  # Disable this test
   ```

2. **Create Custom Preset**:
   Add to `test_config.py`:
   ```python
   CUSTOM_TESTS = [
       'test_db.py',
       'test_auth.py',
       'test_admin.py',
   ]
   
   TEST_PRESETS['custom'] = {
       'description': 'Custom test suite',
       'tests': CUSTOM_TESTS,
   }
   ```

## Output and Reporting

### Test Results Format

```
🧪============================================================
   COMPREHENSIVE TEST RUNNER - SALON ESE
==============================================================
   Started at: 2024-12-19 14:30:25
   Working Directory: /app
   Python Version: 3.9.7
==============================================================

📋 Running: test_db.py
--------------------------------------------------
✅ Database connectivity test passed
✅ test_db.py - PASSED (2.34s)

📋 Running: test_models.py
--------------------------------------------------
✅ Model creation test passed
✅ test_models.py - PASSED (1.87s)

==============================================================
   TEST RUN SUMMARY
==============================================================
   Total Tests Run: 25
   Passed: 23 ✅
   Failed: 2 ❌
   Duration: 45.67 seconds
   Completed at: 2024-12-19 14:31:10
==============================================================

❌ FAILED TESTS:
   - test_analytics_system.py: Analytics service not available
   - test_commission_system.py: Commission calculation error

✅ PASSED TESTS (23):
   - test_db.py
   - test_models.py
   - test_auth.py
   ...
```

### Understanding Test Output

- **✅ PASSED**: Test completed successfully
- **❌ FAILED**: Test failed with errors
- **⏱️ TIMEOUT**: Test exceeded time limit
- **⚠️ ERROR**: Unexpected error during test execution

## Troubleshooting

### Common Issues

1. **Docker Container Not Running**:
   ```bash
   # Start the container
   docker-compose up -d
   
   # Check container status
   docker-compose ps
   ```

2. **Test File Not Found**:
   - Verify test file exists in the project
   - Check file path in `test_config.py`
   - Ensure file permissions are correct

3. **Import Errors**:
   - Ensure all dependencies are installed
   - Check Python path configuration
   - Verify test file imports are correct

4. **Database Connection Issues**:
   - Check database container is running
   - Verify database credentials
   - Ensure database is accessible from test container

### Debug Mode

For detailed debugging, modify `test_config.py`:

```python
TEST_SETTINGS = {
    'show_detailed_output': True,      # Show all test output
    'stop_on_first_failure': True,     # Stop on first error
    'timeout_per_test': 600,           # Increase timeout
}
```

### Performance Optimization

1. **Reduce Test Scope**:
   ```bash
   # Run only essential tests
   ./run_tests_docker.sh smoke
   ```

2. **Disable Slow Tests**:
   Edit `test_config.py` and comment out slow tests:
   ```python
   # 'test_analytics_system.py',  # Slow test - disable during development
   ```

3. **Parallel Execution** (Future Enhancement):
   - Consider running independent test categories in parallel
   - Use pytest-xdist for parallel test execution

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Run Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start Docker containers
        run: docker-compose up -d
        
      - name: Wait for database
        run: sleep 30
        
      - name: Run smoke tests
        run: docker exec salon-ese-web-1 python comprehensive_test_runner.py --preset smoke
        
      - name: Run full test suite
        run: docker exec salon-ese-web-1 python comprehensive_test_runner.py --preset prod
        
      - name: Run coverage tests
        run: docker exec salon-ese-web-1 python comprehensive_test_runner.py --pytest
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'docker-compose up -d'
                sh 'sleep 30'
            }
        }
        
        stage('Smoke Tests') {
            steps {
                sh 'docker exec salon-ese-web-1 python comprehensive_test_runner.py --preset smoke'
            }
        }
        
        stage('Full Tests') {
            steps {
                sh 'docker exec salon-ese-web-1 python comprehensive_test_runner.py --preset prod'
            }
        }
        
        stage('Coverage') {
            steps {
                sh 'docker exec salon-ese-web-1 python comprehensive_test_runner.py --pytest'
            }
        }
    }
}
```

## Best Practices

### Test Organization

1. **Group Related Tests**: Keep related tests in the same category
2. **Use Descriptive Names**: Test files should clearly indicate their purpose
3. **Maintain Test Independence**: Tests should not depend on each other
4. **Keep Tests Fast**: Individual tests should complete quickly

### Configuration Management

1. **Version Control**: Keep `test_config.py` in version control
2. **Environment-Specific**: Use different configurations for different environments
3. **Documentation**: Document any custom test configurations
4. **Regular Review**: Periodically review and update test configurations

### Execution Strategy

1. **Smoke Tests First**: Always run smoke tests before full test suite
2. **Fail Fast**: Use `stop_on_first_failure` for development
3. **Regular Execution**: Run tests regularly during development
4. **Pre-deployment**: Always run full test suite before deployment

## Migration from Legacy Test Runner

The comprehensive test runner is designed to work alongside the existing `run_tests.py`. To migrate:

1. **Gradual Migration**: Start using the new runner for new tests
2. **Preserve Existing**: Keep `run_tests.py` for existing workflows
3. **Update Documentation**: Update team documentation to reference new runner
4. **Training**: Train team members on new test runner features

## Support and Maintenance

### Adding New Tests

1. **Create Test File**: Add new test file to appropriate category in `test_config.py`
2. **Update Documentation**: Document new test in this README
3. **Test Integration**: Verify test works with test runner
4. **Update Presets**: Add to appropriate presets if needed

### Updating Test Categories

1. **Review Organization**: Periodically review test categorization
2. **Update Descriptions**: Keep category descriptions current
3. **Optimize Grouping**: Group tests for optimal execution
4. **Remove Obsolete**: Remove or update obsolete tests

### Performance Monitoring

1. **Track Execution Time**: Monitor test execution times
2. **Identify Slow Tests**: Identify and optimize slow tests
3. **Resource Usage**: Monitor resource usage during test execution
4. **Optimize Configuration**: Adjust timeouts and settings as needed

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Test Framework**: Python + Pytest  
**Docker Support**: Full integration
