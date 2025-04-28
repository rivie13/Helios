import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication

# Create a global QApplication that will be used for all tests
# This needs to happen at module import time, before any tests run
app = QApplication.instance()
if app is None:
    app = QApplication([])

@pytest.fixture(scope="session")
def qapp():
    """Return the existing QApplication instance."""
    return app

@pytest.fixture
def app(qapp):
    """Use the session-level QApplication fixture and process pending events."""
    yield qapp
    qapp.processEvents()

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_path = temp_file.name
    
    yield temp_path
    
    # Clean up after the test
    if os.path.exists(temp_path):
        os.remove(temp_path)

@pytest.fixture
def mock_sensor_data():
    """Return mock sensor data for testing"""
    return {
        "lidarDistances": 15.3,
        "temperature": 24.7,
        "humidity": 52,
        "batteryLevel": 85,
        "positionX": 10.5,
        "positionY": 20.3,
        "positionZ": 0.5,
        "orientationX": 0.0,
        "orientationY": 0.1,
        "orientationZ": 0.0
    }

# Add mock fixtures to prevent GUI components from actually rendering
@pytest.fixture(autouse=True)
def mock_gui_components():
    """Mock various GUI components to prevent actual window creation"""
    with patch('PyQt5.QtWidgets.QMainWindow.show', return_value=None):
        with patch('PyQt5.QtWidgets.QMainWindow.setGeometry', return_value=None):
            with patch('PyQt5.QtWidgets.QMainWindow.showMinimized', return_value=None):
                with patch('PyQt5.QtWidgets.QWidget', return_value=MagicMock()):
                    with patch('PyQt5.QtWidgets.QVBoxLayout', return_value=MagicMock()):
                        with patch('PyQt5.QtWidgets.QHBoxLayout', return_value=MagicMock()):
                            yield 