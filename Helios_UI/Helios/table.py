import csv
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

def create_dashboard_table():
    headers = ["robot_type", "world_type", "disaster_type", "time_seconds",
               "completed", "started_at", "completed_at"]

    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(30)

    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setAlternatingRowColors(True)
    table.setStyleSheet("""
        QTableWidget {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2e2e2e, stop:1 #31353d);
            alternate-background-color: #383838;
            color: #e0e6f0;
            gridline-color: #4a5a73;
            font-family: 'Roboto', sans-serif;
            font-size: 15px;
            border: 2px solid #4a5a73;
            border-radius: 8px;
            padding: 5px;
        }
        QTableWidget::item {
            padding: 12px;
            border: none;
        }
        QTableWidget::item:hover {
            background-color: #4a5a73;
        }
        QTableWidget::item:selected {
            background-color: #b48ead;
            color: #ffffff;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2a3441, stop:1 #353f4e);
            color: #e0e6f0;
            font-family: 'Inter', sans-serif;
            font-size: 16px;
            font-weight: 600;
            padding: 10px;
            border: none;
            border-bottom: 1px solid #4a5a73;
        }
    """)
    
    # UPDATE THIS PATH TO THE CORRECT PATH FOR YOUR SYSTEM
    csv_path = r"C:\Users\rivie\Helios\Helios_UI\dashboard_data.csv"

    try:
        with open(csv_path, newline='') as f:
            reader = list(csv.reader(f))
            data = reader[1:]  # Skip header

            table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)

                    if headers[col_idx] == "completed":
                        if value == "True":
                            item.setText("Success")
                            item.setForeground(QColor("#50fa7b"))
                        elif value == "False":
                            item.setText("Failed")
                            item.setForeground(QColor("#ff5555"))

                    table.setItem(row_idx, col_idx, item)

    except FileNotFoundError:
        print(f"❌ CSV file not found at: {csv_path}")
        table.setRowCount(0)

    table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(True)

    layout.addWidget(table)
    return widget