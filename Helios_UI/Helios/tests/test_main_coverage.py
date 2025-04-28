"""
Tests to improve coverage of main.py without modifying the file.
"""
import sys
import os
import socket
import json
import time
import pytest
from unittest.mock import patch, MagicMock, call
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

# Create QApplication instance before importing anything that might create widgets
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# Import after QApplication is created
from main import MainWindow

class TestMainWindowCoverage:
    """Tests designed specifically to improve code coverage for MainWindow"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Mock init to avoid actual window creation
        with patch.object(MainWindow, '__init__', return_value=None):
            self.window = MainWindow()
            
            # Mock necessary attributes that would be set in __init__
            self.window.server_socket = None
            self.window.client_socket = None
            self.window.unity_process = None
            self.window.sim_start_time = None
            self.window.selected_option = "wildfire"
            self.window.tabs = MagicMock()
            self.window.sensor_table = MagicMock()
            self.window.fields = ["temperature", "humidity", "batteryLevel"]
            self.window.simulations_config = {
                "wildfire": {
                    "exe_path": r"C:\Path\To\Simulation.exe",
                    "title": "Wild Fire | Multi-Robot", 
                    "hwnd_title": "RoboticsNav2SLAMExample"
                }
            }
    
    @patch('socket.socket')
    def test_start_socket_server_success(self, mock_socket):
        """Test socket server startup - success case"""
        # Set up mock socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # Test method
        self.window.start_socket_server()
        
        # Verify socket was created and configured
        mock_socket.assert_called_once()
        mock_socket_instance.setsockopt.assert_called_once()
        mock_socket_instance.bind.assert_called_once_with(('localhost', 12345))
        mock_socket_instance.listen.assert_called_once_with(5)
    
    @patch('socket.socket')
    def test_start_socket_server_exception(self, mock_socket):
        """Test socket server startup - exception case"""
        # Set up mock to raise exception on bind
        mock_socket_instance = MagicMock()
        mock_socket_instance.bind.side_effect = socket.error("Test error")
        mock_socket.return_value = mock_socket_instance
        
        # Test method
        self.window.start_socket_server()
        
        # Verify socket was created but did not complete setup
        mock_socket.assert_called_once()
        mock_socket_instance.bind.assert_called_once()
        mock_socket_instance.listen.assert_not_called()
    
    def test_update_sensor_fields(self):
        """Test sensor field updates from received data"""
        # Setup
        self.window.sensor_table = MagicMock()
        test_data = {
            "temperature": 72.5,
            "humidity": 45.2,
            "batteryLevel": 87.3,
            "unknown_field": "test"  # This should be ignored
        }
        
        # Test
        self.window.update_sensor_fields(test_data)
        
        # Verify that setItem was called exactly 3 times (once for each field)
        assert self.window.sensor_table.setItem.call_count == 3
        
        # Instead of comparing the exact objects, just verify the correct indices were used
        calls = self.window.sensor_table.setItem.call_args_list
        indices_used = [(args[0], args[1]) for args, _ in calls]
        expected_indices = [(0, 1), (1, 1), (2, 1)]
        
        # Check that we have set items at the expected row,col positions
        for expected in expected_indices:
            assert expected in indices_used
    
    @patch('time.time')
    @patch('time.sleep')
    def test_wait_for_socket_connection_timeout(self, mock_sleep, mock_time):
        """Test socket connection timeout"""
        # Setup for timeout
        mock_time.side_effect = [0, 5, 10, 15, 21]  # time passes beyond timeout
        self.window.client_socket = None
        
        # Test
        result = self.window.wait_for_socket_connection(timeout=20)
        
        # Verify timeout behavior
        assert result is False
        assert mock_sleep.call_count > 0
    
    @patch('time.time')
    @patch('time.sleep')
    def test_wait_for_socket_connection_success(self, mock_sleep, mock_time):
        """Test successful socket connection"""
        # Use a counter to dynamically return increasing time values
        time_values = [0]
        def time_side_effect():
            time_values[0] += 1  # Increment time counter
            return time_values[0]
            
        mock_time.side_effect = time_side_effect
        self.window.client_socket = None
        
        # Set client_socket after first sleep call to simulate connection
        def sleep_side_effect(seconds):
            if mock_sleep.call_count == 1:
                self.window.client_socket = MagicMock()
        
        mock_sleep.side_effect = sleep_side_effect
        
        # Test
        result = self.window.wait_for_socket_connection(timeout=20)
        
        # Verify success behavior
        assert result is True
        assert mock_sleep.call_count >= 1  # We need at least one sleep call
    
    def test_stop_simulation_no_start_time(self):
        """Test stopping simulation when no start time exists"""
        # Setup
        self.window.sim_start_time = None
        
        # Test
        self.window.stop_simulation()
        
        # No assertions needed - we're just ensuring it doesn't crash
    
    @patch('main.insert_simulation_data')
    def test_stop_simulation_with_client(self, mock_insert_data):
        """Test stopping simulation with client socket"""
        # Setup
        self.window.sim_start_time = MagicMock()
        # Make sure sim_start_time.strftime works properly
        self.window.sim_start_time.strftime.return_value = "2023-01-01 12:00:00"
        
        # Create a client_socket mock - IMPORTANT: This needs to be set before calling stop_simulation
        client_socket_mock = MagicMock()
        self.window.client_socket = client_socket_mock
        
        # Setup unity_process properly
        unity_process_mock = MagicMock()
        unity_process_mock.terminate = MagicMock()  # Ensure terminate exists
        unity_process_mock.wait = MagicMock()      # Ensure wait exists
        self.window.unity_process = unity_process_mock
        
        # Setup simulations_config for the selected_option
        self.window.selected_option = "wildfire"
        self.window.simulations_config = {
            "wildfire": {
                "exe_path": r"C:\Path\To\Simulation.exe",
                "title": "Wild Fire | Multi-Robot", 
                "hwnd_title": "RoboticsNav2SLAMExample"
            }
        }
        
        # Mock tabs properly to avoid the while loop
        tabs_mock = MagicMock()
        tabs_mock.count.return_value = 0  # Avoid entering the while loop
        self.window.tabs = tabs_mock
        
        # Mock init_tabs to prevent it from doing anything
        self.window.init_tabs = MagicMock()
        
        # Simply test the method call - we'll verify socket operations afterward
        self.window.stop_simulation()
        
        # Verify the expected behaviors
        mock_insert_data.assert_called_once()
        
        # Check client_socket operations
        # The client_socket might be None after the call, so we'll just check if send was called
        client_socket_mock.send.assert_called_once_with("STOP".encode())
        client_socket_mock.close.assert_called_once()
        
        # Check that unity_process operations were called
        unity_process_mock.terminate.assert_called_once()
        unity_process_mock.wait.assert_called_once()
    
    def test_toggle_maximize_restore(self):
        """Test window maximize/restore toggling"""
        # Setup
        self.window.isMaximized = MagicMock(return_value=False)
        self.window.showMaximized = MagicMock()
        self.window.showNormal = MagicMock()
        
        # Test initially not maximized
        self.window.toggle_maximize_restore()
        self.window.showMaximized.assert_called_once()
        self.window.showNormal.assert_not_called()
        
        # Test when maximized
        self.window.isMaximized.return_value = True
        self.window.toggle_maximize_restore()
        self.window.showNormal.assert_called_once()

    @patch('main.QFileDialog.getSaveFileName', return_value=("", ""))
    def test_download_csv_cancel(self, mock_get_save):
        """Test CSV download when user cancels"""
        # Test
        self.window.download_csv()
        # Verify that it just returns without error
        mock_get_save.assert_called_once()

    @patch('main.QFileDialog.getSaveFileName', return_value=("", ""))
    def test_export_pdf_cancel(self, mock_get_save):
        """Test PDF export when user cancels"""
        # Test
        self.window.export_pdf()
        # Verify that it just returns without error
        mock_get_save.assert_called_once()
        
    @patch('os.path.exists', return_value=False)
    def test_embed_unity_file_not_found(self, mock_exists):
        """Test embed_unity when exe file doesn't exist"""
        # Test
        result = self.window.embed_unity()
        
        # Verify behavior
        assert result is False
        mock_exists.assert_called_once() 