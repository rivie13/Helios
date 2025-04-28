"""
Unit tests for data handling in the Helios application.
Test IDs: UT-003, UT-004 from the Test Procedures Document
"""
import pytest
import csv
import os
from unittest.mock import patch
from datetime import datetime

# Import the functionality to test
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

class TestDataHandling:
    """Test cases for data handling functionality"""
    
    def test_csv_data_insertion(self, temp_csv_file):
        """
        UT-003: Test CSV data insertion
        Verify that simulation data is correctly inserted into the CSV file
        """
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
                assert rows[1][5] == start_time           # Start time
                assert rows[1][6] == stop_time            # End time
    
    def test_resolution_time_calculation(self, temp_csv_file):
        """
        UT-004: Test resolution time calculation
        Verify that the time difference is calculated correctly
        """
        # Patch the CSV path in the module to use our test file
        with patch('insert_data.CSV_PATH', temp_csv_file):
            # Define test times with a known difference (30 minutes = 1800 seconds)
            start_time = "2023-01-01 10:00:00"
            stop_time = "2023-01-01 10:30:00"
            
            # Insert test data
            insert_simulation_data(
                "Test Disaster",
                "Test Robot",
                "Test World",
                start_time,
                stop_time
            )
            
            # Calculate expected resolution time as the application does
            fmt = "%Y-%m-%d %H:%M:%S"
            start_dt = datetime.strptime(start_time, fmt)
            stop_dt = datetime.strptime(stop_time, fmt)
            expected_resolution = str(round((stop_dt - start_dt).total_seconds(), 1))
            
            # Read the file and check if the resolution time is calculated correctly
            with open(temp_csv_file, 'r') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
                
                # Check resolution time matches expected calculation
                assert rows[1][3] == expected_resolution  # Resolution time in seconds
                # Verify the value is approximately 1800 seconds (30 minutes)
                assert float(rows[1][3]) == 1800.0 