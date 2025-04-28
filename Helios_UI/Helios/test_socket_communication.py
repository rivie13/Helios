import pytest
import socket
import json
import threading
import time
from unittest.mock import patch, MagicMock

from main import MainWindow

@pytest.fixture(autouse=True)
def mock_qt_widgets():
    """Mock all Qt-related widgets for all tests in this module"""
    with patch('main.QMainWindow'):
        with patch('main.QTabWidget'):
            with patch('main.QWidget'):
                with patch('main.QVBoxLayout'):
                    with patch('main.QHBoxLayout'):
                        with patch('main.QPushButton'):
                            with patch('main.QLabel'):
                                yield

class TestSocketCommunication:
    
    @patch('socket.socket')
    @patch('main.QApplication')
    def test_socket_server_initialization(self, mock_qapp, mock_socket, app):
        """Test that the socket server is initialized correctly"""
        # Create instance which should start the socket server
        with patch('threading.Thread'):
            window = MainWindow()
        
        # Check if socket was created with correct params
        mock_socket.assert_called()
        mock_instance = mock_socket.return_value
        
        # Check that it tries to bind to localhost:12345
        mock_instance.bind.assert_called_with(('localhost', 12345))
        mock_instance.listen.assert_called_with(5)
        
    @patch('threading.Thread')
    @patch('socket.socket')
    @patch('main.QApplication')
    def test_socket_server_threading(self, mock_qapp, mock_socket, mock_thread, app):
        """Test that a thread is created for handling socket connections"""
        window = MainWindow()
        
        # Check if a thread was started to handle connections
        mock_thread.assert_called_with(
            target=window.handle_socket_connections,
            daemon=True
        )
        mock_thread.return_value.start.assert_called_once()
    
    @patch('socket.socket')
    @patch('main.QApplication')
    def test_sensor_data_signal_emission(self, mock_qapp, mock_socket, app):
        """Test that sensor data signals are emitted when received"""
        with patch('threading.Thread'):
            window = MainWindow()
        
        # Mock the signal to check if it's emitted
        window.sensor_data_signal = MagicMock()
        
        # Simulate received data
        mock_client = MagicMock()
        test_data = {'temperature': 25.5, 'humidity': 60}
        mock_client.recv.return_value = json.dumps(test_data).encode()
        
        # We need to call the handler function directly because it's run in a thread
        # Mock the accept method to return our mock client
        mock_server = mock_socket.return_value
        mock_server.accept.return_value = (mock_client, ('127.0.0.1', 54321))
        
        # Create a mock function to break out of the infinite loop
        orig_recv = mock_client.recv
        call_count = 0
        
        def mock_recv(size):
            nonlocal call_count
            if call_count == 0:
                call_count += 1
                return json.dumps(test_data).encode()
            return b''  # Return empty data to break the loop
            
        mock_client.recv = mock_recv
        
        # Execute the first iteration of the connection handler
        window.handle_socket_connections()
        
        # Check that the signal was emitted with the correct data
        window.sensor_data_signal.emit.assert_called_with(test_data)
        
    @patch('main.QApplication')
    def test_simulation_command_sending(self, mock_qapp, app):
        """Test that simulation commands are sent correctly"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
            
        window.client_socket = MagicMock()
        
        # Test start command
        window.start_simulation()
        window.client_socket.send.assert_called_with("START".encode())
        
        # Test pause command
        window.pause_simulation()
        window.client_socket.send.assert_called_with("PAUSE".encode())
        
        # Test stop command (only testing the socket part, not all the other stop logic)
        window.sim_start_time = MagicMock()  # Mock start time to prevent errors
        window.stop_simulation()
        window.client_socket.send.assert_called_with("STOP".encode()) 