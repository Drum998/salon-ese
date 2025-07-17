# Salon ESE - Test Suite Documentation

## Overview

This document describes the comprehensive test suite for the Salon ESE system, covering the new salon management features including salon settings, work patterns, and employment details functionality.

## Test Structure

The test suite is organized into three main categories:

### 1. Salon Settings Tests (`tests/test_salon_settings.py`)
Tests for salon configuration and opening hours management.

### 2. Work Patterns Tests (`tests/test_work_patterns.py`)
Tests for staff work schedules and pattern management.

### 3. Employment Details Tests (`tests/test_employment_details.py`)
Tests for employment type and commission management.

## What Each Test Suite Covers

### Salon Settings Tests

#### Model Tests
- **Creation**: Test salon settings creation with valid data
- **Default Settings**: Test automatic default settings creation when none exist
- **Retrieval**: Test existing settings retrieval and caching behavior

#### Form Tests
- **Time Validation**: HH:MM format validation for opening/closing times
- **Business Logic**: Closed days don't require time validation
- **Data Conversion**: Form data to opening hours dictionary conversion
- **Error Handling**: Invalid time formats and edge cases

#### Route Tests
- **Authentication**: Unauthenticated access prevention
- **Authorization**: Manager role requirement verification
- **CRUD Operations**: Create, read, update operations
- **Error Handling**: Form validation error display

### Work Patterns Tests

#### Model Tests
- **Creation**: Work pattern creation with weekly schedules
- **Hours Calculation**: Automatic weekly hours computation
- **Edge Cases**: Partial days, no working days, various schedules

#### Form Tests
- **Validation**: Time format and schedule validation
- **Business Logic**: Non-working days don't require time inputs
- **Data Conversion**: Form data to work schedule dictionary
- **User Selection**: Staff member dropdown population

#### Route Tests
- **Authentication**: Unauthenticated access prevention
- **Authorization**: Manager role requirement
- **CRUD Operations**: Full create, read, update, delete operations
- **Error Handling**: Form validation and database error handling

### Employment Details Tests

#### Model Tests
- **Creation**: Both employed and self-employed scenarios
- **Constraints**: Unique user constraint enforcement
- **Properties**: Employment type boolean properties
- **Data Types**: Decimal precision for commission percentages

#### Form Tests
- **Validation**: Commission percentage range validation (0-100)
- **Business Logic**: Commission only for self-employed staff
- **Constraints**: Duplicate user prevention
- **Data Types**: Proper decimal handling

#### Route Tests
- **Authentication**: Unauthenticated access prevention
- **Authorization**: Manager role requirement
- **CRUD Operations**: Full create, read, update, delete operations
- **Error Handling**: Form validation and constraint violations

## Running Tests in Docker Environment

### Prerequisites

Ensure your Docker container is running and the application is accessible:

```bash
# Start the Docker container
docker-compose up -d

# Check container status
docker-compose ps
```

### Method 1: Using the Test Runner Script

The easiest way to run tests is using the provided test runner script:

```bash
# Run all tests
docker exec -it salon-ese-web-1 python run_tests.py

# Run specific test suites
docker exec -it salon-ese-web-1 python run_tests.py salon_settings
docker exec -it salon-ese-web-1 python run_tests.py work_patterns
docker exec -it salon-ese-web-1 python run_tests.py employment_details

# Show test runner help
docker exec -it salon-ese-web-1 python run_tests.py help
```

### Method 2: Using Pytest Directly

For more control over test execution:

```bash
# Run all tests
docker exec -it salon-ese-web-1 pytest tests/ -v

# Run specific test file
docker exec -it salon-ese-web-1 pytest tests/test_salon_settings.py -v
docker exec -it salon-ese-web-1 pytest tests/test_work_patterns.py -v
docker exec -it salon-ese-web-1 pytest tests/test_employment_details.py -v

# Run with coverage reporting
docker exec -it salon-ese-web-1 pytest tests/ -v --cov=app

# Run specific test class
docker exec -it salon-ese-web-1 pytest tests/test_salon_settings.py::TestSalonSettingsModel -v

# Run specific test method
docker exec -it salon-ese-web-1 pytest tests/test_salon_settings.py::TestSalonSettingsModel::test_salon_settings_creation -v
```

### Method 3: Interactive Testing

For debugging or interactive testing:

```bash
# Access the container shell
docker exec -it salon-ese-web-1 bash

# Run tests from within the container
python run_tests.py
# or
pytest tests/ -v
```

## Test Configuration

### Environment Setup

Tests use a separate test database configuration:

- **Database**: SQLite in-memory database for fast execution
- **Configuration**: `testing` environment with isolated settings
- **Fixtures**: Automatic database setup/teardown for each test

### Test Dependencies

Tests require the following packages (already included in requirements.txt):
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `flask-testing` - Flask testing utilities

## Understanding Test Output

### Successful Test Run

```
🧪 Running Salon ESE Unit Tests
==================================================

📋 Running tests in tests/test_salon_settings.py
----------------------------------------
test_salon_settings_creation PASSED
test_get_settings_creates_default PASSED
test_get_settings_returns_existing PASSED
...
✅ tests/test_salon_settings.py - All tests passed!
```

### Failed Test Run

```
test_invalid_time_format FAILED
test_commission_not_allowed_for_employed FAILED
...
❌ tests/test_employment_details.py - Some tests failed!
```

### Coverage Report

```
---------- coverage: platform linux, python 3.9.7-final-0 -----------
Name                           Stmts   Miss  Cover
--------------------------------------------------
app/__init__.py                   45      0   100%
app/forms.py                     245     12    95%
app/models.py                    416     15    96%
app/routes/admin.py              179      8    96%
...
TOTAL                          1000     50    95%
```

## Common Test Scenarios

### 1. Testing Form Validation

Tests verify that forms properly validate:
- Time formats (HH:MM)
- Commission percentages (0-100)
- Required fields
- Business logic constraints

### 2. Testing Database Operations

Tests ensure:
- Data is properly saved to database
- Relationships are maintained
- Constraints are enforced
- Data retrieval works correctly

### 3. Testing Authentication & Authorization

Tests verify:
- Unauthenticated users are redirected
- Only authorized roles can access admin pages
- Proper error messages are displayed

### 4. Testing Business Logic

Tests validate:
- Commission only applies to self-employed staff
- Work pattern hours are calculated correctly
- Salon settings defaults are created properly

## Troubleshooting

### Common Issues

1. **Container Not Running**
   ```bash
   # Check container status
   docker-compose ps
   
   # Start container if needed
   docker-compose up -d
   ```

2. **Database Connection Issues**
   ```bash
   # Rebuild container with fresh database
   docker-compose down
   docker-compose up --build -d
   ```

3. **Test Import Errors**
   ```bash
   # Ensure you're in the correct directory
   docker exec -it salon-ese-app pwd
   # Should show: /app
   ```

4. **Permission Issues**
   ```bash
   # Check file permissions
   docker exec -it salon-ese-app ls -la run_tests.py
   ```

### Debug Mode

For detailed debugging, run tests with verbose output:

```bash
docker exec -it salon-ese-app pytest tests/ -v -s --tb=long
```

The `-s` flag shows print statements, and `--tb=long` provides detailed tracebacks.

## Continuous Integration

These tests are designed to be run in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Tests
  run: |
    docker exec salon-ese-web-1 python run_tests.py
```

## Test Maintenance

### Adding New Tests

1. Create test file in `tests/` directory
2. Follow naming convention: `test_<feature>.py`
3. Use existing fixtures for database and user setup
4. Add test to `run_tests.py` if needed

### Updating Tests

When modifying functionality:
1. Update corresponding tests
2. Ensure all edge cases are covered
3. Run full test suite to verify changes
4. Update this documentation if needed

## Performance Notes

- Tests use in-memory SQLite for speed
- Each test runs in isolation
- Database is reset between tests
- Typical full test suite runs in 10-30 seconds

## Support

For test-related issues:
1. Check this documentation
2. Review test output for specific errors
3. Verify Docker container is running
4. Ensure all dependencies are installed

---

**Last Updated**: December 2024  
**Test Framework**: Pytest  
**Coverage**: Models, Forms, Routes, Business Logic 