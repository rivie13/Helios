# Helios Testing Guide

## Running Tests

To run the tests, use:

```
cd Helios_UI
pytest -v
```

Or run specific tests using the included batch file:

```
.\run_tests.bat
```

For coverage reporting, run:

```
.\run_with_coverage.bat
```

## Test Structure

The tests are organized into the following categories:

- **Unit Tests**: Located in `tests/unit/` - tests individual components in isolation
- **Integration Tests**: Located in `tests/integration/` - tests interactions between components
- **Acceptance Tests**: Located in `tests/acceptance/` - tests end-to-end functionality

## Testing Approach

The tests are designed to verify core functionality while avoiding GUI rendering issues. Key aspects:

1. **GUI Component Mocking**: Most GUI elements are mocked to prevent actual window creation
2. **QApplication Management**: A single QApplication instance is managed for the entire test session
3. **Socket Handling**: Network sockets are mocked to avoid actual network operations
4. **File Operations**: Temporary files are used for testing file operations

## Test Files

### Main Test Files
- `test_helios.py`: Tests for core application logic
- `test_socket_communication.py`: Tests for network communication
- `test_ui.py`: Tests for UI components
- `test_main_coverage.py`: Ensures comprehensive test coverage

### Integration Tests
- `test_simulation_lifecycle.py`: Tests the full simulation lifecycle

## Coverage Reporting

Coverage reports are generated using pytest-cov with configurations specified in `.coveragerc`. Running the `run_with_coverage.bat` script will:

1. Execute all tests with coverage tracking
2. Generate HTML and terminal reports
3. Open the HTML report automatically

## Common Issues

If tests get stuck or fail with Qt-related errors:

1. Make sure you're running from a proper Python environment with all dependencies
2. Check that QApplication is properly initialized in your fixtures
3. If the GUI is rendering during tests, ensure more components are mocked

## Adding New Tests

When adding new tests that interact with GUI components:
1. Add appropriate patches for GUI components
2. Avoid creating real windows or dialogs
3. Mock any network operations
4. Use the provided fixtures in conftest.py
5. Place in the appropriate directory (unit/, integration/, or acceptance/) based on test scope 