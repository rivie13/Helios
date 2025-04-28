"""
Tests to improve coverage of main.py without modifying the file.
"""
import sys
import os
import socket
import json
import time
import pytest
from unittest.mock import patch, MagicMock, call, mock_open
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QPoint

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
        
    def test_mouse_press_event(self):
        """Test mouse press event handling"""
        # Setup necessary mocks
        self.window.title_bar = MagicMock()
        self.window.title_bar.underMouse.return_value = True
        self.window.frameGeometry = MagicMock()
        self.window.frameGeometry.return_value.topLeft.return_value = QPoint(50, 50)
        
        # Create mock event
        event = MagicMock()
        event.button.return_value = Qt.LeftButton
        event.globalPos.return_value = QPoint(100, 100)
        
        # Test method
        self.window.mousePressEvent(event)
        
        # Verify drag position was calculated properly
        assert self.window.drag_position is not None
        # The drag position should be the difference between globalPos and top-left
        # In this case, that's (100,100) - (50,50) = (50,50)
        assert isinstance(self.window.drag_position, QPoint)
        
        # Test right button click (should not set drag position)
        self.window.drag_position = None
        event.button.return_value = Qt.RightButton
        self.window.mousePressEvent(event)
        assert self.window.drag_position is None
        
    def test_mouse_move_event(self):
        """Test mouse move event handling"""
        # Setup drag position
        self.window.drag_position = QPoint(50, 50)
        self.window.move = MagicMock()
        
        # Create mock event
        event = MagicMock()
        event.buttons.return_value = Qt.LeftButton
        event.globalPos.return_value = QPoint(200, 200)
        
        # Test method
        self.window.mouseMoveEvent(event)
        
        # Window should move to globalPos() - drag_position
        # In this case that's (200,200) - (50,50) = (150,150)
        self.window.move.assert_called_once()
        
        # Test when drag position is None
        self.window.drag_position = None
        self.window.move.reset_mock()
        self.window.mouseMoveEvent(event)
        self.window.move.assert_not_called()
        
    def test_mouse_release_event(self):
        """Test mouse release event handling"""
        # Setup
        self.window.drag_position = QPoint(50, 50)
        
        # Create mock event
        event = MagicMock()
        
        # Test method
        self.window.mouseReleaseEvent(event)
        
        # Verify drag position was reset
        assert self.window.drag_position is None
        
    @patch('os.path.exists', return_value=True)
    @patch('subprocess.Popen')
    @patch('time.sleep')
    @patch('win32gui.EnumWindows')
    @patch('win32gui.GetWindowText')
    @patch('win32gui.SetParent')
    @patch('win32gui.SetWindowLong')
    @patch('win32gui.MoveWindow')
    def test_embed_unity_success(self, mock_move, mock_set_long, mock_set_parent, mock_get_text, 
                                mock_enum, mock_sleep, mock_popen, mock_exists):
        """Test successful Unity embedding"""
        # Setup mocks
        self.window.selected_option = "wildfire"
        
        # Mock finding window by title
        def mock_enum_callback(callback, result_list):
            # Simulate finding one window
            callback(12345, result_list)
            return True
            
        mock_enum.side_effect = mock_enum_callback
        mock_get_text.return_value = "RoboticsNav2SLAMExample"
        
        # Mock unity container
        self.window.unity_container = MagicMock()
        self.window.unity_container.rect.return_value.width.return_value = 800
        self.window.unity_container.rect.return_value.height.return_value = 600
        self.window.unity_container.winId.return_value.__int__.return_value = 67890
        
        # Test method
        result = self.window.embed_unity()
        
        # Verify embedding process
        assert result is True
        mock_popen.assert_called_once()
        mock_set_parent.assert_called_once_with(12345, 67890)
        mock_set_long.assert_called_once()
        mock_move.assert_called_once_with(12345, 0, 0, 800, 600, True)
        assert self.window.unity_hwnd == 12345
    
    def test_create_title_bar(self):
        """Test creation of custom title bar"""
        # Mock required attributes
        with patch('main.QPixmap', MagicMock()):
            with patch('os.path.join', return_value="robot.jpg"):
                # Test method
                result = self.window.create_title_bar()
                
                # Verify result
                assert result is not None
                assert isinstance(result, QWidget)
                
                # Check layout
                layout = result.layout()
                assert isinstance(layout, QHBoxLayout)
                
                # Verify buttons were added (close, minimize, maximize)
                buttons_found = 0
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    if hasattr(widget, 'text') and widget.text() in ["–", "☐", "X"]:
                        buttons_found += 1
                
                assert buttons_found == 3
                
    @patch('os.path.join')
    def test_init_tabs(self, mock_join):
        """Test initialization of tabs"""
        # Setup window with required attributes
        self.window.home_tab = None
        self.window.tabs = MagicMock()
        self.window.setup_home_menu = MagicMock()
        
        # Mock necessary components
        with patch('main.create_dashboard_widget') as mock_create_dash:
            # Configure mock to return expected values
            mock_dash = MagicMock()
            mock_table = MagicMock()
            mock_csv_btn = MagicMock()
            mock_pdf_btn = MagicMock()
            mock_create_dash.return_value = (mock_dash, mock_table, mock_csv_btn, mock_pdf_btn)
            
            # Test method
            self.window.init_tabs()
            
            # Verify tabs were added
            self.window.tabs.addTab.assert_called()
            assert self.window.tabs.addTab.call_count >= 3  # At least 3 tabs
            
            # Verify home menu was setup
            self.window.setup_home_menu.assert_called_once()
            
            # Verify dashboard widget was created
            mock_create_dash.assert_called_once()
            
            # Verify click handlers were connected
            mock_csv_btn.clicked.connect.assert_called_once()
            mock_pdf_btn.clicked.connect.assert_called_once()
    
    @patch('main.QFileDialog.getSaveFileName', return_value=("test.csv", "CSV Files (*.csv)"))
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.writer')
    def test_download_csv_success(self, mock_writer, mock_file, mock_get_save):
        """Test CSV download when user selects a file"""
        # Setup
        self.window.fields = ["temperature", "humidity"]
        self.window.sensor_table = MagicMock()
        
        # Mock table item values - for each field, we need both column 0 (name) and column 1 (value)
        # Create enough mock items for the entire operation
        items = []
        field_names = ["temperature", "humidity"]
        field_values = ["25.5", "60%"]
        
        for name, value in zip(field_names, field_values):
            name_item = MagicMock()
            name_item.text.return_value = name
            
            value_item = MagicMock()
            value_item.text.return_value = value
            
            items.extend([None, name_item, value_item, None])
        
        # Configure the side_effect to return the appropriate item or None
        def side_effect(row, col):
            if col == 0:  # Field name column
                return items[row * 4 + 1]
            elif col == 1:  # Value column
                return items[row * 4 + 2]
            return None
        
        self.window.sensor_table.item.side_effect = side_effect
        
        # Mock csv writer
        writer_instance = MagicMock()
        mock_writer.return_value = writer_instance
        
        # Test method
        self.window.download_csv()
        
        # Verify file operations
        mock_file.assert_called_once_with("test.csv", 'w', newline='')
        writer_instance.writerow.assert_called() 
        # Should write header and 2 data rows
        assert writer_instance.writerow.call_count == 3 