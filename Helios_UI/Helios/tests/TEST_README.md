# Helios Testing Guide

## Running Tests

To run the tests, use:

```
cd Helios_UI
pytest -v
```

Or simply run the included batch file:
powershell:

```
./run_tests.bat
```

## Testing Approach

The tests are designed to verify core functionality while avoiding GUI rendering issues. Key aspects:

1. **GUI Component Mocking**: Most GUI elements are mocked to prevent actual window creation
2. **QApplication Management**: A single QApplication instance is managed for the entire test session
3. **Socket Handling**: Network sockets are mocked to avoid actual network operations
4. **File Operations**: Temporary files are used for testing file operations

## Test Files

- `test_helios.py`: Tests for core application logic
- `test_socket_communication.py`: Tests for network communication
- `test_ui.py`: Tests for UI components

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