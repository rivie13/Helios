import pytest
import os
import json
import tempfile
import csv
from unittest.mock import patch, MagicMock

from main import MainWindow
from insert_data import insert_simulation_data

class TestHeliosSimulation:
    
    @patch('main.QTabWidget')
    @patch('main.QMainWindow.setCentralWidget')
    def test_simulation_config_structure(self, mock_set_central, mock_tab_widget):
        """Test that simulation configuration has the expected structure"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
        
        # Check all required simulations exist
        expected_sims = ["wildfire", "earthquake", "flood", "tornado", "search_rescue", "hazmat"]
        for sim in expected_sims:
            assert sim in window.simulations_config
        
        # Check each simulation has required attributes
        for sim_name, sim_config in window.simulations_config.items():
            assert "exe_path" in sim_config
            assert "title" in sim_config
            assert "hwnd_title" in sim_config
    
    @patch('socket.socket')
    @patch('main.QTabWidget')
    @patch('main.QMainWindow.setCentralWidget')
    def test_sensor_data_processing(self, mock_set_central, mock_tab_widget, mock_socket):
        """Test the sensor data processing function"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
        
        # Simulate receiving sensor data
        test_data = {
            "lidarDistances": 12.5,
            "temperature": 22.3,
            "humidity": 45,
            "batteryLevel": 78
        }
        
        # Mock the sensor table
        window.sensor_table = MagicMock()
        window.fields = ["lidarDistances", "temperature", "humidity", "batteryLevel"]
        
        # Call the update method directly
        window.update_sensor_fields(test_data)
        
        # Verify the table was updated correctly
        assert window.sensor_table.setItem.call_count == 4
    
    @patch('main.QTabWidget')
    @patch('main.QMainWindow.setCentralWidget')
    def test_simulation_selection(self, mock_set_central, mock_tab_widget):
        """Test the simulation selection functionality"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
        
        # Mock the simulation buttons
        window.sim_buttons = {
            "wildfire": MagicMock(),
            "earthquake": MagicMock(),
            "flood": MagicMock()
        }
        
        # Select a simulation
        window.select_simulation("wildfire")
        
        # Check that the selected option was updated
        assert window.selected_option == "wildfire"
        
        # Check that the correct button was checked
        window.sim_buttons["wildfire"].setChecked.assert_called_with(True)
        window.sim_buttons["earthquake"].setChecked.assert_called_with(False)
        window.sim_buttons["flood"].setChecked.assert_called_with(False)

    @patch('main.QTabWidget')
    @patch('main.QMainWindow.setCentralWidget')
    def test_csv_export(self, mock_set_central, mock_tab_widget):
        """Test the CSV export functionality"""
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
            
        window.fields = ["lidarDistances", "temperature", "humidity", "batteryLevel"]
        window.sensor_table = MagicMock()
        
        # Mock table items
        def mock_item_at(row, col):
            values = ["10.5", "24.0", "55", "90"]
            if col == 1 and 0 <= row < len(values):
                item = MagicMock()
                item.text.return_value = values[row]
                return item
            return None
        
        window.sensor_table.item = mock_item_at
        
        # Use a temp file for the CSV export
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            # Patch QFileDialog.getSaveFileName to return our temp path
            with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName', return_value=(temp_path, "CSV Files (*.csv)")):
                window.download_csv()
                
                # Verify CSV contents
                with open(temp_path, 'r') as f:
                    csv_reader = csv.reader(f)
                    rows = list(csv_reader)
                    
                    # Check header
                    assert rows[0] == ["Sensor", "Value"]
                    
                    # Check data rows
                    assert rows[1] == ["lidarDistances", "10.5"]
                    assert rows[2] == ["temperature", "24.0"]
                    assert rows[3] == ["humidity", "55"]
                    assert rows[4] == ["batteryLevel", "90"]
        finally:
            # Clean up the temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    def test_insert_simulation_data(self):
        """Test the insert_simulation_data function"""
        # Create a temp CSV file
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            # Path the CSV path in the module
            with patch('insert_data.CSV_FILE_PATH', temp_path):
                # Insert some test data
                insert_simulation_data(
                    "Wild Fire",
                    "Multi-Robot",
                    "Warehouse",
                    "2023-04-01 10:00:00",
                    "2023-04-01 10:30:00"
                )
                
                # Verify the data was written correctly
                with open(temp_path, 'r') as f:
                    csv_reader = csv.reader(f)
                    rows = list(csv_reader)
                    last_row = rows[-1]
                    
                    assert "Wild Fire" in last_row
                    assert "Multi-Robot" in last_row
                    assert "Warehouse" in last_row
                    assert "2023-04-01 10:00:00" in last_row
                    assert "2023-04-01 10:30:00" in last_row
        finally:
            # Clean up the temp file
            if os.path.exists(temp_path):
                os.remove(temp_path) 