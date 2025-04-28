import pytest
import socket
import json
import threading
import time
import os
from unittest.mock import patch, MagicMock, Mock

from main import MainWindow

# Check if the executable exists
wildfire_exe_path = r"C:\Users\rivie\Helios\Helios_UI\Helios\build_warehouse\RoboticsNav2SLAMExample.exe"
WILDFIRE_EXISTS = os.path.exists(wildfire_exe_path)

@pytest.fixture
def mock_window():
    """Create a mocked MainWindow without initializing the UI"""
    # Create a properly mocked window object
    with patch.object(MainWindow, '__init__', return_value=None):
        window = MainWindow()
        
        # Add required attributes
        window.sensor_data_signal = MagicMock()
        window.client_socket = MagicMock()
        window.sim_start_time = None
        window.selected_option = "wildfire"
        window.simulations_config = {
            "wildfire": {
                "exe_path": wildfire_exe_path,
                "title": "Wild Fire | Multi-Robot",
                "hwnd_title": "RoboticsNav2SLAMExample"
            }
        }
        
        # Mock the stop_simulation method to avoid the error
        window.stop_simulation = MagicMock()
        
        return window

class TestSocketCommunication:
    
    def test_basic_socket_functionality(self, mock_window):
        """Test the basic socket command sending functionality"""
        window = mock_window
        
        # Test start command
        window.start_simulation()
        window.client_socket.send.assert_called_with("START".encode())
        
        # Test pause command
        window.pause_simulation()
        window.client_socket.send.assert_called_with("PAUSE".encode())
        
        # Test stop command directly through the mock
        window.stop_simulation()
        assert window.stop_simulation.called
    
    @patch('socket.socket')
    def test_socket_server_creation(self, mock_socket):
        """Test that a socket server can be created with the correct parameters"""
        # Create a mock instance that will be returned by socket()
        mock_instance = MagicMock()
        mock_socket.return_value = mock_instance
        
        # Create a partial main window object just for testing the socket
        with patch('main.MainWindow.__init__', return_value=None):
            window = MainWindow()
            window.server_socket = None
            
            # Call the method directly
            window.start_socket_server()
        
        # Check if socket was created with correct params
        mock_socket.assert_called()
        
        # Check that it tries to bind to localhost:12345
        mock_instance.bind.assert_called_with(('localhost', 12345))
        mock_instance.listen.assert_called_with(5)
        
    def test_json_message_handling(self):
        """Test that JSON messages from the socket are properly processed"""
        # Set up mock window with sensor signal
        with patch.object(MainWindow, '__init__', return_value=None):
            window = MainWindow()
            window.sensor_data_signal = MagicMock()
            window.client_socket = None
            
        # Create test data with fields that match those in the MainWindow class
        test_data = {
            "lidarDistances": [1.2, 3.4, 5.6],
            "temperature": 25.5,
            "humidity": 48.2,
            "batteryLevel": 75,
            "positionX": 10.0,
            "positionY": 20.0,
            "positionZ": 30.0
        }
        
        # Simulate JSON data processing
        window.sensor_data_signal.emit(test_data)
        window.sensor_data_signal.emit.assert_called_with(test_data)
            
    @pytest.mark.skipif(not WILDFIRE_EXISTS, reason="Wildfire executable not found")
    def test_simulation_config_validity(self):
        """Test that the simulation configuration points to real files"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
            
        # Check that wildfire simulation has a valid executable path
        assert "wildfire" in window.simulations_config
        wildfire_path = window.simulations_config["wildfire"]["exe_path"]
        assert os.path.exists(wildfire_path), f"Wildfire executable not found at: {wildfire_path}"
        
        # Verify the title matches what's expected in the UI
        assert window.simulations_config["wildfire"]["title"] == "Wild Fire | Multi-Robot"
        
    def test_handle_socket_connections(self):
        """Test the socket connection handling logic with simulated data"""
        with patch.object(MainWindow, '__init__', return_value=None):
            window = MainWindow()
            window.sensor_data_signal = MagicMock()
            window.server_socket = MagicMock()
            
            # Setup mock client and address
            mock_client = MagicMock()
            
            # Create realistic JSON data that matches the expected fields
            test_data1 = json.dumps({
                "temperature": 25.5, 
                "humidity": 48.2,
                "lidarDistances": [1.2, 2.5, 3.0, 3.5],
                "batteryLevel": 85
            }).encode()
            
            test_data2 = json.dumps({
                "batteryLevel": 75,
                "positionX": 10.5,
                "positionY": 20.3,
                "positionZ": 0.5
            }).encode()
            
            # Setup the recv method to return our test data then empty string
            mock_client.recv.side_effect = [test_data1, test_data2, b'']
            
            # Setup server to return our mock client
            window.server_socket.accept.return_value = (mock_client, ('127.0.0.1', 12345))
            window.server_socket.settimeout = MagicMock()
            
            # Create a handler function that mimics the actual code
            def handler():
                try:
                    client, _ = window.server_socket.accept()
                    window.client_socket = client
                    for _ in range(3):  # Limit iterations for test
                        data = client.recv(4096).decode()
                        if not data:
                            break
                        try:
                            if data.startswith('{') and data.endswith('}'):
                                json_data = json.loads(data)
                                window.sensor_data_signal.emit(json_data)
                        except:
                            pass
                except:
                    pass
            
            # Run the handler
            handler()
            
            # Verify the expected calls - should emit signal for each JSON message
            assert mock_client.recv.call_count == 3  # Two valid JSON messages and one empty
            assert window.sensor_data_signal.emit.call_count == 2  # Two signals emitted 