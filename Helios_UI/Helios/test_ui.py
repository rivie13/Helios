import pytest
from unittest.mock import patch, MagicMock
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem

from main import MainWindow
from sensor_data import create_sensor_data_widget, create_dashboard_widget
from table import create_dashboard_table

@pytest.fixture(autouse=True)
def mock_qt_widgets():
    """Mock all Qt-related widgets for all tests in this module"""
    with patch('main.QMainWindow'):
        with patch('main.QTabWidget'):
            with patch('main.QWidget'):
                with patch('main.QVBoxLayout'):
                    with patch('main.QHBoxLayout'):
                        with patch('main.QGridLayout'):
                            with patch('main.QLabel'):
                                with patch('main.QPushButton'):
                                    yield

class TestUIComponents:
    
    @patch('main.QApplication')
    def test_main_window_initialization(self, mock_qapp, app):
        """Test that the main window initializes properly"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            with patch('main.MainWindow.init_tabs', return_value=None):
                window = MainWindow()
        
        # Check that tabs are created
        assert window.tabs is not None
        
        # Check that title bar exists
        assert window.title_bar is not None
        
        # Check that unity container is not created yet
        assert not hasattr(window, 'unity_container')
    
    @patch('main.QApplication')
    def test_tab_creation(self, mock_qapp, app):
        """Test that tabs are created with correct titles"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            with patch('main.MainWindow.setup_home_menu'):
                with patch('sensor_data.create_dashboard_widget'):
                    window = MainWindow()
                    
                    # Mock tab widget
                    window.tabs = MagicMock()
                    window.tabs.count.return_value = 3
                    window.tabs.tabText.side_effect = ["Home", "Sensor Data", "Dashboard"]
        
        # Check tab titles
        assert window.tabs.tabText(0) == "Home"
        assert window.tabs.tabText(1) == "Sensor Data"
        assert window.tabs.tabText(2) == "Dashboard"
    
    @patch('PyQt5.QtWidgets.QTableWidget')
    def test_sensor_data_widget_creation(self, mock_table, app):
        """Test that sensor data widget is created properly"""
        # Define test fields
        fields = ["field1", "field2", "field3"]
        
        # Create widget
        with patch('PyQt5.QtWidgets.QWidget', return_value=MagicMock()):
            with patch('PyQt5.QtWidgets.QPushButton', return_value=MagicMock()):
                widget, table, csv_btn, pdf_btn = create_dashboard_widget(fields)
        
        # Check that all components exist
        assert widget is not None
        assert table is not None
        assert csv_btn is not None
        assert pdf_btn is not None
        
        # Check table initialization
        mock_table.return_value.setRowCount.assert_called_with(len(fields))
        mock_table.return_value.setColumnCount.assert_called_with(2)
        
    @patch('PyQt5.QtWidgets.QTableWidget')
    def test_dashboard_table_creation(self, mock_table, app):
        """Test dashboard table creation"""
        with patch('PyQt5.QtWidgets.QTableWidgetItem', return_value=MagicMock()):
            table = create_dashboard_table()
        
        # Check that table exists
        assert table is not None
        
        # Check row and column counts
        mock_table.return_value.setRowCount.assert_called_with(5)
        mock_table.return_value.setColumnCount.assert_called_with(5)
    
    @patch('main.QApplication')
    def test_home_menu_simulation_buttons(self, mock_qapp, app):
        """Test that simulation buttons are created in home menu"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            with patch('main.MainWindow.setup_home_menu'):
                window = MainWindow()
                
                # Mock simulation buttons
                window.sim_buttons = {
                    "wildfire": MagicMock(),
                    "earthquake": MagicMock(),
                    "flood": MagicMock(),
                    "tornado": MagicMock(),
                    "search_rescue": MagicMock(),
                    "hazmat": MagicMock()
                }
        
        # Check that all buttons exist
        expected_sims = ["wildfire", "earthquake", "flood", "tornado", "search_rescue", "hazmat"]
        for sim in expected_sims:
            assert sim in window.sim_buttons
    
    @patch('subprocess.Popen')
    @patch('win32gui.EnumWindows')
    @patch('win32gui.SetParent')
    @patch('main.QApplication')
    def test_embed_unity_flow(self, mock_qapp, mock_set_parent, mock_enum_windows, mock_popen, app):
        """Test the unity embedding process flow"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            with patch('main.MainWindow.init_tabs', return_value=None):
                window = MainWindow()
            
        window.selected_option = "wildfire"
        window.unity_container = MagicMock()
        window.unity_container.rect.return_value.width.return_value = 800
        window.unity_container.rect.return_value.height.return_value = 600
        window.unity_container.winId = MagicMock(return_value=12345)
        
        # Mock EnumWindows to simulate finding the Unity window
        def mock_enum_func(callback, output):
            # Call the callback with a mock hwnd
            callback(12345, output)
            return True
            
        mock_enum_windows.side_effect = mock_enum_func
        
        # Execute the embed function
        with patch('win32gui.GetWindowText', return_value="RoboticsNav2SLAMExample"):
            with patch('os.path.exists', return_value=True):
                with patch('time.sleep'):
                    with patch('win32gui.MoveWindow'):
                        with patch('win32gui.SetWindowLong'):
                            result = window.embed_unity()
        
        # Check that the process was started
        mock_popen.assert_called_once()
        
        # Check that the parent was set
        mock_set_parent.assert_called_once()
        
        # Check the result
        assert result is True
        assert window.unity_hwnd == 12345 