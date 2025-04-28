import pytest
import sys
import csv
import os
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication
from datetime import datetime

# Create QApplication instance before importing anything that might create widgets
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# Only import after QApplication is created
from main import MainWindow
from insert_data import insert_simulation_data, CSV_PATH

@pytest.fixture
def temp_csv_file(tmp_path):
    """Create a temporary CSV file for testing"""
    csv_file = tmp_path / "test_simulation_data.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Robot Type", "World Type", "Disaster Type", "Start Time", "End Time"])
    return str(csv_file)

class TestHeliosSimulation:
    
    def test_simulation_config_structure(self):
        """Test that simulation configuration has the expected structure and paths are valid"""
        # Create the main window with patched socket server to avoid actual connections
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
        
        # Verify that simulations exist with expected structure
        assert hasattr(window, 'simulations_config')
        assert len(window.simulations_config) > 0
        
        # Verify wildfire configuration
        assert "wildfire" in window.simulations_config
        wildfire_config = window.simulations_config["wildfire"]
        assert "exe_path" in wildfire_config
        assert "title" in wildfire_config
        assert "hwnd_title" in wildfire_config
        
        # Verify the wildfire executable path exists if specified in test environment
        wildfire_path = wildfire_config["exe_path"]
        if wildfire_path:
            assert os.path.exists(wildfire_path), f"Specified wildfire executable not found at: {wildfire_path}"
    
    def test_insert_simulation_data(self, temp_csv_file):
        """Test that simulation data is correctly inserted into the CSV file"""
        # Patch the CSV path in the module to use our test file
        with patch('insert_data.CSV_PATH', temp_csv_file):
            # Insert some test data
            insert_simulation_data(
                "Test Disaster",
                "Test Robot",
                "Test World",
                "2023-01-01 10:00:00",
                "2023-01-01 10:30:00"
            )
            
            # Read the file and check if the entry exists with correct data
            with open(temp_csv_file, 'r') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
                assert len(rows) > 1  # Header + at least one data row
                
                # Check header row
                assert rows[0] == ["Robot Type", "World Type", "Disaster Type", "Start Time", "End Time"]
                
                # Check data row
                assert rows[1][0] == "Test Robot"
                assert rows[1][1] == "Test World"
                assert rows[1][2] == "Test Disaster"
                assert rows[1][3] == "2023-01-01 10:00:00"
                assert rows[1][4] == "2023-01-01 10:30:00"

    def test_simulation_lifecycle(self):
        """Test the simulation lifecycle (start, pause, stop) with proper timing"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
        
        # Mock client socket
        window.client_socket = MagicMock()
        
        # Test start simulation
        assert window.sim_start_time is None
        window.start_simulation()
        assert window.sim_start_time is not None
        assert isinstance(window.sim_start_time, datetime)
        window.client_socket.send.assert_called_with("START".encode())
        
        # Test pause simulation
        window.pause_simulation()
        window.client_socket.send.assert_called_with("PAUSE".encode())
        
        # Mock required attributes for stop_simulation
        window.selected_option = "wildfire"
        
        # Patch insert_simulation_data to prevent actual file operations
        with patch('main.insert_simulation_data') as mock_insert:
            # Test stop simulation
            window.stop_simulation()
            
            # Verify sim_start_time was reset
            assert window.sim_start_time is None
            assert window.selected_option is None
            
            # Verify socket commands
            window.client_socket.send.assert_called_with("STOP".encode())
            
            # Verify insert_simulation_data was called
            assert mock_insert.called
            
    @pytest.mark.skipif(not os.path.exists(r"C:\Users\rivie\Helios\Helios_UI\Helios\build_warehouse\RoboticsNav2SLAMExample.exe"), 
                       reason="Wildfire executable not found")
    def test_wildfire_simulation_path(self):
        """Test that the wildfire simulation path is correctly configured and exists"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
        
        # Get the wildfire config
        wildfire_config = window.simulations_config.get("wildfire", {})
        exe_path = wildfire_config.get("exe_path")
        
        # Verify executable path is set and exists
        assert exe_path, "Wildfire executable path not configured"
        assert os.path.exists(exe_path), f"Wildfire executable not found at: {exe_path}"
        
        # Verify other configuration fields
        assert wildfire_config.get("title") == "Wild Fire | Multi-Robot"
        assert wildfire_config.get("hwnd_title") == "RoboticsNav2SLAMExample"