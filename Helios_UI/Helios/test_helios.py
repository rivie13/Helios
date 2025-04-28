import pytest
import sys
import csv
from unittest.mock import patch
from PyQt5.QtWidgets import QApplication

# Create QApplication instance before importing anything that might create widgets
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# Only import after QApplication is created
from main import MainWindow
from insert_data import insert_simulation_data, CSV_PATH

class TestHeliosSimulation:
    
    def test_simulation_config_structure(self, app):
        """Simple test that simulation configuration has the expected structure"""
        # Create the main window with patched socket server to avoid actual connections
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
        
        # Just check that simulations exist - simplest possible test
        assert hasattr(window, 'simulations_config')
        assert len(window.simulations_config) > 0
    
    def test_insert_simulation_data(self, temp_csv_file):
        """Simple test for the insert_simulation_data function"""
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
            
            # Read the file and check if at least one entry exists
            with open(temp_csv_file, 'r') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
                assert len(rows) > 0