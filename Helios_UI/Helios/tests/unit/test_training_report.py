import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem

# Create QApplication instance before importing anything that might create widgets
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# Import the function to test
from training_report import export_training_report_pdf

class TestTrainingReport:
    """Unit tests for training report functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a mock table widget with some sample data
        self.sensor_fields = ["temperature", "humidity", "batteryLevel", "positionX", "positionY"]
        self.sensor_table = QTableWidget(len(self.sensor_fields), 2)
        
        # Add some sample data to the table
        for i, field in enumerate(self.sensor_fields):
            self.sensor_table.setItem(i, 0, QTableWidgetItem(field))
            self.sensor_table.setItem(i, 1, QTableWidgetItem(str(i * 10)))
    
    @patch('training_report.plt')
    @patch('training_report.QTextDocument')
    @patch('training_report.QPrinter')
    @patch('os.path.exists', return_value=True)
    @patch('os.remove')
    def test_export_training_report_pdf(self, mock_remove, mock_exists, mock_qprinter, mock_qdoc, mock_plt):
        """Test PDF report export with all dependencies mocked"""
        # Set up mocks
        mock_fig = MagicMock()
        mock_plt.figure.return_value = mock_fig
        
        mock_doc_instance = MagicMock()
        mock_qdoc.return_value = mock_doc_instance
        
        mock_printer_instance = MagicMock()
        mock_qprinter.return_value = mock_printer_instance
        
        # Call the function
        test_path = "test_report.pdf"
        export_training_report_pdf(
            test_path,
            "Test Simulation",
            self.sensor_fields,
            self.sensor_table
        )
        
        # Verify that the document was created and printed
        mock_qdoc.assert_called_once()
        mock_doc_instance.setHtml.assert_called_once()
        mock_doc_instance.print_.assert_called_once_with(mock_printer_instance)
        
        # Verify that we cleaned up the image files
        assert mock_remove.call_count == 4  # 4 plots should be created and cleaned up
    
    def test_export_training_report_empty_path(self):
        """Test that the function returns early if the path is empty"""
        # The function should return immediately if path is empty
        result = export_training_report_pdf("", "Test", [], None)
        assert result is None
    
    @patch('training_report.plt')
    @patch('training_report.QTextDocument')
    @patch('training_report.QPrinter')
    @patch('os.path.exists', return_value=False)  # Simulate missing image files
    @patch('os.remove')
    def test_export_training_report_missing_images(self, mock_remove, mock_exists, mock_qprinter, mock_qdoc, mock_plt):
        """Test report generation when image files are missing"""
        # Call the function
        test_path = "test_report.pdf"
        export_training_report_pdf(
            test_path,
            "Test Simulation",
            self.sensor_fields,
            self.sensor_table
        )
        
        # Verify that we didn't try to remove any files
        mock_remove.assert_not_called() 