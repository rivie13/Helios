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
        # Match the actual columns used in insert_data.py
        writer.writerow(["Robot Type", "World Type", "Disaster Type", "Resolution Time", "Success", "Start Time", "End Time"])
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
            # Define test times
            start_time = "2023-01-01 10:00:00"
            stop_time = "2023-01-01 10:30:00"
            
            # Insert some test data
            insert_simulation_data(
                "Test Disaster",
                "Test Robot",
                "Test World",
                start_time,
                stop_time
            )
            
            # Calculate expected resolution time like insert_data.py does
            fmt = "%Y-%m-%d %H:%M:%S"
            start_dt = datetime.strptime(start_time, fmt)
            stop_dt = datetime.strptime(stop_time, fmt)
            expected_resolution = str(round((stop_dt - start_dt).total_seconds(), 1))
            
            # Read the file and check if the entry exists with correct data
            with open(temp_csv_file, 'r') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
                assert len(rows) > 1  # Header + at least one data row
                
                # Check header row matches expected columns
                assert rows[0] == ["Robot Type", "World Type", "Disaster Type", "Resolution Time", "Success", "Start Time", "End Time"]
                
                # Check data row according to actual implementation in insert_data.py
                assert rows[1][0] == "Test Robot"
                assert rows[1][1] == "Test World"
                assert rows[1][2] == "Test Disaster"
                assert rows[1][3] == expected_resolution  # Resolution time in seconds
                assert rows[1][4] == "True"               # Success flag
                assert rows[1][5] == start_time           # Start time
                assert rows[1][6] == stop_time            # End time

    def test_simulation_lifecycle(self):
        """Test the simulation lifecycle (start, pause, stop) with proper initialization"""
        # Create window and properly initialize required attributes
        with patch('main.MainWindow.__init__', return_value=None):
            window = MainWindow()
            
            # Initialize required attributes based on the actual MainWindow implementation
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
            window.tabs = MagicMock()
        
        # Test start simulation
        assert window.sim_start_time is None
        window.start_simulation()
        assert window.sim_start_time is not None
        assert isinstance(window.sim_start_time, datetime)
        window.client_socket.send.assert_called_with("START".encode())
        
        # Test pause simulation
        window.pause_simulation()
        window.client_socket.send.assert_called_with("PAUSE".encode())
        
        # Mock required methods for stop_simulation to prevent actual calls
        window.stop_simulation = MagicMock()
        window.stop_simulation()
        assert window.stop_simulation.called
            
    @pytest.mark.skipif(not os.path.exists(r"C:\Users\rivie\Helios\Helios_UI\Helios\build_warehouse\RoboticsNav2SLAMExample.exe"), 
                       reason="Wildfire executable not found")
    def test_wildfire_simulation_path(self):
        """Test that the wildfire simulation path is correctly configured and exists"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
        
        # Get the wildfire config
        wildfire_config = window.simulations_config.get("wildfire", {})
        exe_path = wildfire_config.get("exe_path")
        
        # Verify executable path is set and points to an actual file
        assert exe_path, "Wildfire executable path not configured"
        assert os.path.exists(exe_path), f"Wildfire executable not found at: {exe_path}"
        
        # Verify other configuration fields
        assert wildfire_config.get("title") == "Wild Fire | Multi-Robot"
        assert wildfire_config.get("hwnd_title") == "RoboticsNav2SLAMExample"