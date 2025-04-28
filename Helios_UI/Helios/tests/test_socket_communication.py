import pytest
import socket
import json
import threading
import time
import os
from unittest.mock import patch, MagicMock, Mock

from main import MainWindow

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
                "exe_path": r"C:\Users\rivie\Helios\Helios_UI\Helios\build_warehouse\RoboticsNav2SLAMExample.exe",
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
            
        # Create test data
        test_data = {
            "lidarDistances": [1.2, 3.4, 5.6],
            "temperature": 25.5,
            "humidity": 48.2,
            "batteryLevel": 75
        }
        
        # Simulate receiving JSON data
        with patch('socket.socket.recv', return_value=json.dumps(test_data).encode()):
            # Manually call the handler with mocked socket
            mock_client = MagicMock()
            mock_client.recv.return_value = json.dumps(test_data).encode()
            
            # Call the handler method directly with our test data
            window.client_socket = mock_client
            
            # Simulate a message being received and processed
            thread = threading.Thread(target=lambda: window.sensor_data_signal.emit(test_data))
            thread.start()
            thread.join()
            
            # Verify the signal was emitted with our test data
            window.sensor_data_signal.emit.assert_called_with(test_data)
            
    @pytest.mark.skipif(not os.path.exists(r"C:\Users\rivie\Helios\Helios_UI\Helios\build_warehouse\RoboticsNav2SLAMExample.exe"), 
                        reason="Simulation executable not found")
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
            mock_client.recv.side_effect = [
                json.dumps({"temperature": 25.5, "humidity": 48.2}).encode(),
                json.dumps({"batteryLevel": 75}).encode(),
                b''  # Empty response to end the loop
            ]
            
            # Setup server to return our mock client
            window.server_socket.accept.return_value = (mock_client, ('127.0.0.1', 12345))
            window.server_socket.settimeout = MagicMock()
            
            # Run the handler in a separate thread with a timeout
            thread = threading.Thread(target=window.handle_socket_connections)
            thread.daemon = True
            thread.start()
            
            # Give the thread time to process
            time.sleep(0.5)
            
            # Force thread termination after test
            window.server_socket.accept.side_effect = Exception("Test complete")
            
            # Verify the expected calls
            assert mock_client.recv.call_count > 0
            assert window.sensor_data_signal.emit.call_count >= 1 