import pytest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QWidget, QTextEdit, QLabel, QVBoxLayout

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
        
    def test_create_sensor_data_widget(self):
        """Test sensor data widget creation and verify components"""
        widget = create_sensor_data_widget()
        
        # Check widget exists
        assert widget is not None
        assert isinstance(widget, QWidget)
        
        # Check widget has a layout
        layout = widget.layout()
        assert layout is not None
        assert isinstance(layout, QVBoxLayout)
        
        # Check layout contains expected components (labels and terminals)
        # Should have at least 4 widgets (2 labels + 2 terminals for LIDAR and Camera)
        assert layout.count() >= 4  
        
        # Check if we can find QTextEdit components (terminal displays)
        text_edits_found = 0
        labels_found = 0
        for i in range(layout.count()):
            item = layout.itemAt(i).widget()
            if isinstance(item, QTextEdit):
                text_edits_found += 1
                # Verify content - terminals should contain specific text
                assert item.toPlainText() != ""
                assert "[" in item.toPlainText()  # All terminals show data in [BRACKETS]
            elif isinstance(item, QLabel):
                labels_found += 1
                # Verify labels have proper text
                assert "Sensor" in item.text() or "Object Detection" in item.text()
                
        assert text_edits_found >= 2  # Should have at least 2 QTextEdit components
        assert labels_found >= 2  # Should have at least 2 label components
        
    def test_dashboard_widget_update_mechanism(self):
        """Test dashboard widget terminal updates when table data changes"""
        fields = ["temperature", "humidity", "batteryLevel"]
        
        # Create widget with components
        widget, table, csv_btn, pdf_btn = create_dashboard_widget(fields)
        
        # Find the QTextEdit terminal in the layout
        terminal = None
        for i in range(widget.layout().count()):
            item = widget.layout().itemAt(i).widget()
            if isinstance(item, QTextEdit):
                terminal = item
                break
        
        assert terminal is not None
        
        # Get initial text to compare changes
        initial_text = terminal.toPlainText()
        
        # Verify initial state shows N/A for values
        for field in fields:
            assert f"{field}: N/A" in initial_text
        
        # Change a table value
        table.setItem(0, 1, QTableWidgetItem("99.5"))
        
        # Get updated text
        updated_text = terminal.toPlainText()
        
        # Check terminal text was updated with new value
        assert f"{fields[0]}: 99.5" in updated_text
        
        # Change another value
        table.setItem(1, 1, QTableWidgetItem("45%"))
        
        # Get final text
        final_text = terminal.toPlainText()
        
        # Check both values were updated
        assert f"{fields[0]}: 99.5" in final_text
        assert f"{fields[1]}: 45%" in final_text
        
    def test_dashboard_widget_buttons(self):
        """Test dashboard widget buttons are configured correctly"""
        fields = ["temperature", "humidity"]
        
        # Create widget
        widget, table, csv_btn, pdf_btn = create_dashboard_widget(fields)
        
        # Verify button properties
        assert csv_btn.text() == "Download"
        assert pdf_btn.text() == "Export PDF"
        
        # Verify button styling
        assert "background" in pdf_btn.styleSheet()
        assert pdf_btn.objectName() == "pdfButton"  # Special styling for PDF button 