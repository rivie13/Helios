import pytest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QWidget

# Import directly, no need for complex mocking
from table import create_dashboard_table
from sensor_data import create_sensor_data_widget, create_dashboard_widget

class TestUIComponents:
    
    def test_dashboard_table_direct_creation(self):
        """Test dashboard table creation directly without mocks"""
        widget = create_dashboard_table()
        
        # Check that widget exists and is the right type
        assert widget is not None
        assert isinstance(widget, QWidget)  # The function returns a QWidget container, not the table itself
        
        # Check that the widget contains a layout with a table widget
        assert widget.layout() is not None
        assert widget.layout().count() > 0

    def test_dashboard_widget_creation(self):
        """Test dashboard widget creation with minimal necessary mocks"""
        # Define test fields
        fields = ["field1", "field2", "field3"]
        
        # Create widget
        widget, table, csv_btn, pdf_btn = create_dashboard_widget(fields)
        
        # Check that all components exist
        assert widget is not None
        assert table is not None
        assert csv_btn is not None
        assert pdf_btn is not None
        
        # Check table properties
        assert table.rowCount() == len(fields)
        assert table.columnCount() == 2 