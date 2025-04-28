"""
Unit tests for simulation configuration in the Helios application.
Test IDs: UT-001, UT-002 from the Test Procedures Document
"""
import pytest
import os
from unittest.mock import patch, MagicMock
import sys
from PyQt5.QtWidgets import QApplication

# Create QApplication instance before importing anything that might create widgets
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# Only import after QApplication is created
from main import MainWindow

class TestSimulationConfig:
    """Test cases for verifying simulation configuration"""
    
    def test_simulation_config_structure(self):
        """
        UT-001: Verify simulation configuration structure
        """
        # Create the main window with patched socket server to avoid actual connections
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
        
        # Verify that simulations exist with expected structure
        assert hasattr(window, 'simulations_config')
        assert len(window.simulations_config) > 0
        
        # Check that each simulation has the required fields
        for sim_name, sim_config in window.simulations_config.items():
            assert "exe_path" in sim_config
            assert "title" in sim_config
            assert "hwnd_title" in sim_config
    
    def test_wildfire_configuration(self):
        """
        UT-002: Verify wildfire configuration
        """
        # Create the main window with patched socket server to avoid actual connections
        with patch('main.MainWindow.start_socket_server', return_value=None):
            window = MainWindow()
        
        # Verify wildfire configuration exists
        assert "wildfire" in window.simulations_config
        wildfire_config = window.simulations_config["wildfire"]
        
        # Verify wildfire configuration has required fields
        assert "exe_path" in wildfire_config
        assert "title" in wildfire_config
        assert "hwnd_title" in wildfire_config
        
        # Verify the fields have appropriate values
        assert wildfire_config["title"] == "Wild Fire | Multi-Robot"
        assert wildfire_config["hwnd_title"] == "RoboticsNav2SLAMExample"
        
        # Verify the wildfire executable path exists if specified
        wildfire_path = wildfire_config["exe_path"]
        if wildfire_path and not wildfire_path.startswith(('r"', 'os.path')):
            # Skip this assertion if the path is a variable or function call
            assert os.path.exists(wildfire_path), f"Specified wildfire executable not found at: {wildfire_path}" 