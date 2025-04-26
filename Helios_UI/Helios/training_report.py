import os
import matplotlib.pyplot as plt
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter


def export_training_report_pdf(path, simulation_title, sensor_fields, sensor_table):
    """
    Generates a PDF training report with actual graph visualizations.

    Args:
        path (str): The file path where the PDF will be saved.
        simulation_title (str): The title of the selected simulation.
        sensor_fields (list): List of sensor field names.
        sensor_table (QTableWidget): The table widget containing sensor data.
    """
    if not path:
        return

    # Fixed sample data for visualization purposes
    sample_data = {
        "temperature": [68, 70, 72, 71, 69],
        "humidity": [40, 45, 50, 42, 44],
        "batteryLevel": [100, 95, 90, 85, 80],
        "positionX": [0, 5, 10, 15, 20],
        "positionY": [0, 3, 6, 9, 12],
    }

    # Generate plots and save images
    image_paths = []

    def save_plot(title, x, y, xlabel, ylabel, filename):
        plt.figure()
        plt.plot(x, y, marker='o')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        filepath = f"{filename}.png"
        plt.savefig(filepath)
        plt.close()
        image_paths.append(filepath)

    save_plot("Temperature Over Time", list(range(len(sample_data["temperature"]))), sample_data["temperature"], "Time", "Temperature (°F)", "temperature")
    save_plot("Humidity Levels", list(range(len(sample_data["humidity"]))), sample_data["humidity"], "Time", "Humidity (%)", "humidity")
    save_plot("Battery Depletion", list(range(len(sample_data["batteryLevel"]))), sample_data["batteryLevel"], "Time", "Battery (%)", "battery")
    save_plot("Robot Movement Trajectory", sample_data["positionX"], sample_data["positionY"], "X Position", "Y Position", "trajectory")

    # Build HTML content for PDF
    html = f"""
    <h1>Training Report</h1>
    <p><b>Scenario:</b> {simulation_title}</p>
    <h2>Data Visualizations</h2>
    """

    for image_path in image_paths:
        if os.path.exists(image_path):
            html += f'<p><img src="{image_path}" width="500"></p>'

    doc = QTextDocument()
    doc.setHtml(html)

    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(path)

    doc.print_(printer)

    # Cleanup generated images
    for image_path in image_paths:
        if os.path.exists(image_path):
            os.remove(image_path)

    print(f"✅ PDF with graphs exported to {path}")
