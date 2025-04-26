from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QTableWidget, QPushButton, QTableWidgetItem
from PyQt5.QtCore import Qt

def create_sensor_data_widget():
    sensor_widget = QWidget()
    sensor_layout = QVBoxLayout(sensor_widget)
    sensor_layout.setContentsMargins(5, 5, 5, 5)
    sensor_layout.setSpacing(10)

    # Dark theme styling for terminal appearance
    terminal_style = """
        QTextEdit {
            background-color: #1e1e1e;
            color: #00ff00;
            font-family: 'Courier New';
            font-size: 13px;
            border: 1px solid #444;
            padding: 5px;
        }
        QLabel {
            color: white;
            background-color: #2a2a2a;
            font-size: 14px;
            font-weight: bold;
            padding: 6px 10px;
            border-radius: 4px;
        }
    """

    # LIDAR Sensor Terminal
    lidar_label = QLabel("LIDAR Sensor Output")
    lidar_terminal = QTextEdit()
    lidar_terminal.setReadOnly(True)
    lidar_terminal.setStyleSheet(terminal_style)
    lidar_terminal.setText("""[LIDAR SCAN DATA]
Range: 3.2m
Angle: 45 degrees
Points: 342
...
Obstacle detected at 1.1m
...
""")

    # Camera Sensor Terminal
    camera_label = QLabel("Camera Object Detection")
    camera_terminal = QTextEdit()
    camera_terminal.setReadOnly(True)
    camera_terminal.setStyleSheet(terminal_style)
    camera_terminal.setText("""[OBJECT DETECTION]
Frame 301: Fire detected
Frame 302: Smoke detected
Frame 303: Fire detected
...
""")

    sensor_layout.addWidget(lidar_label)
    sensor_layout.addWidget(lidar_terminal)
    sensor_layout.addWidget(camera_label)
    sensor_layout.addWidget(camera_terminal)

    return sensor_widget

def create_dashboard_widget(fields):
    dash_widget = QWidget()
    dash_layout = QVBoxLayout(dash_widget)
    dash_layout.setContentsMargins(10, 10, 10, 10)
    dash_layout.setSpacing(15)

    # Modern dark theme styling inspired by home_style.py
    terminal_style = """
        QTextEdit {
            background-color: #0a0e17;
            color: #00cc00;
            font-family: 'Roboto Mono', monospace;
            font-size: 14px;
            border: 1px solid #4a5a73;
            border-radius: 6px;
            padding: 10px;
        }
        QLabel {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2a3441, stop:1 #3b4a5e);
            color: #e0e6f0;
            font-family: 'Inter', sans-serif;
            font-size: 16px;
            font-weight: 600;
            padding: 8px 12px;
            border-radius: 4px;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5e81ac, stop:1 #81a1c1);
            color: #ffffff;
            font-family: 'Roboto', sans-serif;
            font-size: 14px;
            font-weight: 600;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #81a1c1, stop:1 #a3bffa);
        }
        QPushButton#pdfButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #50fa7b, stop:1 #69ff94);
            color: #0a0e17;
        }
        QPushButton#pdfButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #69ff94, stop:1 #82ffb0);
        }
    """

    # Sensor terminal
    sensor_label = QLabel("Sensor Data Terminal")
    sensor_label.setStyleSheet(terminal_style)
    dash_layout.addWidget(sensor_label)

    sensor_terminal = QTextEdit()
    sensor_terminal.setReadOnly(True)
    sensor_terminal.setStyleSheet(terminal_style)
    # Initialize with sensor data
    sensor_text = "[SENSOR DATA]\n"
    for field in fields:
        sensor_text += f"{field}: N/A\n"
    sensor_terminal.setText(sensor_text)
    dash_layout.addWidget(sensor_terminal)

    # Hidden sensor table for main.py compatibility
    sensor_table = QTableWidget(len(fields), 2)
    sensor_table.setHorizontalHeaderLabels(["Sensor", "Value"])
    sensor_table.setVisible(False)  # Hidden, only for data updates
    for i, name in enumerate(fields):
        sensor_table.setItem(i, 0, QTableWidgetItem(name))
        sensor_table.setItem(i, 1, QTableWidgetItem(""))
    dash_layout.addWidget(sensor_table)

    # CSV download controls
    csv_label = QLabel("Download Sensor Data as CSV")
    csv_label.setStyleSheet(terminal_style)
    dash_layout.addWidget(csv_label)
    csv_btn = QPushButton("Download")
    csv_btn.setStyleSheet(terminal_style)
    dash_layout.addWidget(csv_btn, alignment=Qt.AlignLeft)

    # PDF export controls
    pdf_label = QLabel("Export Training Report as PDF")
    pdf_label.setStyleSheet(terminal_style)
    dash_layout.addWidget(pdf_label)
    pdf_btn = QPushButton("Export PDF")
    pdf_btn.setObjectName("pdfButton")
    pdf_btn.setStyleSheet(terminal_style)
    dash_layout.addWidget(pdf_btn, alignment=Qt.AlignLeft)

    # Update terminal when table changes
    def update_terminal():
        text = "[SENSOR DATA]\n"
        for i, field in enumerate(fields):
            value = sensor_table.item(i, 1).text() if sensor_table.item(i, 1) else "N/A"
            text += f"{field}: {value}\n"
        sensor_terminal.setText(text)

    # Connect table changes to terminal update
    sensor_table.itemChanged.connect(update_terminal)

    return dash_widget, sensor_table, csv_btn, pdf_btn