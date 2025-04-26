import sys
import os
import subprocess
import time
import socket
import threading
import json
import csv
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from training_report import export_training_report_pdf
from PyQt5.QtGui import QPixmap, QTextDocument
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QFileDialog
)
from PyQt5.QtPrintSupport import QPrinter
import win32gui
import win32con
from table import create_dashboard_table
from insert_data import insert_simulation_data
from datetime import datetime
from home_style import HOME_STYLE, HEADER_LABEL_STYLE, BUTTON_STYLE, BUTTON_HOVER_STYLE, RUN_BUTTON_STYLE, GRID_LAYOUT_CONFIG
from sensor_data import create_sensor_data_widget, create_dashboard_widget

class MainWindow(QMainWindow):
    sensor_data_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        print("🛠 MainWindow initialized")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 1200, 800)

        self.drag_position   = None
        self.unity_process   = None
        self.unity_hwnd      = None
        self.selected_option = None
        self.client_socket   = None
        self.server_socket   = None

        self.simulations_config = {
            "wildfire": {
                "exe_path": r"C:\Users\mikeg\Documents\Helios_UI\Helios_UI\Helios\build_warehouse\RoboticsNav2SLAMExample.exe",
                "title": "Wild Fire | Multi-Robot",
                "hwnd_title": "RoboticsNav2SLAMExample"
            },
            "earthquake": {"exe_path": os.path.abspath("build/UnityHelios.exe"),
                           "title": "Earthquake | Single-Robot", "hwnd_title": "UnityHelios"},
            "flood": {"exe_path": os.path.abspath(r"C:\Users\mikeg\Documents\Helios_UI\Helios_UI\Helios\build_robot\Helios.exe"),
                      "title": "Flood | Single-Robot", "hwnd_title": "Helios"},
            "tornado": {"exe_path": None, "title": "Tornado | Multi-Robot", "hwnd_title": None},
            "search_rescue": {"exe_path": None, "title": "Search & Rescue | Multi-Robot", "hwnd_title": None},
            "hazmat": {"exe_path": None, "title": "Hazmat | Multi-Robot", "hwnd_title": None},
        }

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = self.create_title_bar()
        main_layout.addWidget(self.title_bar)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                font-size: 18px; font-weight: bold; padding: 18px 40px;
                border-right: 1px solid #666; min-width: 120px;
            }
            QTabBar::tab:last { border-right: none; }
        """)
        main_layout.addWidget(self.tabs)

        self.init_tabs()
        self.sensor_data_signal.connect(self.update_sensor_fields)
        self.start_socket_server()

    def create_title_bar(self):
        bar = QWidget()
        bar.setFixedHeight(50)
        bar.setStyleSheet("background-color: #1f1f1f;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 0, 10, 0)

        ico = QLabel()
        icon_path = os.path.join("Helios_Without_UnityProjectFiles", "robot.jpg")
        pix = QPixmap(icon_path)
        if not pix.isNull():
            ico.setPixmap(pix.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(ico)

        title = QLabel("Helios")
        title.setStyleSheet("color:white; font-size:20px; font-weight:bold;")
        layout.addWidget(title)
        layout.addStretch()

        btn_style = """
            QPushButton { font-family:Consolas; font-size:18px; color:white;
                          background:transparent; border:none; width:32px; height:32px; }
            QPushButton:hover { background:#333; }
        """
        for sym, slot in [("–", self.showMinimized), ("☐", self.toggle_maximize_restore), ("X", self.close)]:
            btn = QPushButton(sym)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        return bar

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def init_tabs(self):
        # Home tab
        self.home_tab = QWidget()
        self.tabs.addTab(self.home_tab, "Home")
        self.setup_home_menu()

        # Sensor Data tab
        self.fields = [
            "lidarDistances", "temperature", "humidity", "batteryLevel",
            "positionX", "positionY", "positionZ",
            "orientationX", "orientationY", "orientationZ"
        ]
        self.dash_tab, self.sensor_table, csv_btn, pdf_btn = create_dashboard_widget(self.fields)
        self.tabs.addTab(self.dash_tab, "Sensor Data")
        csv_btn.clicked.connect(self.download_csv)
        pdf_btn.clicked.connect(self.export_pdf)

        # Settings tab
        self.settings_tab = QWidget()
        settings_layout = QVBoxLayout(self.settings_tab)
        settings_layout.setContentsMargins(10, 10, 10, 10)
        settings_layout.setSpacing(10)
        settings_layout.addWidget(create_dashboard_table())
        self.tabs.addTab(self.settings_tab, "Dashboard")

    def setup_home_menu(self):
        layout = QVBoxLayout(self.home_tab)
        menu = QWidget()
        menu.setStyleSheet(HOME_STYLE)
        v = QVBoxLayout(menu)

        hdr = QLabel("Choose Simulation")
        hdr.setStyleSheet(HEADER_LABEL_STYLE)
        hdr.setAlignment(Qt.AlignCenter)
        v.addWidget(hdr)

        grid = QGridLayout()
        grid.setSpacing(GRID_LAYOUT_CONFIG["spacing"])
        grid.setContentsMargins(
            GRID_LAYOUT_CONFIG["margin"],
            GRID_LAYOUT_CONFIG["margin"],
            GRID_LAYOUT_CONFIG["margin"],
            GRID_LAYOUT_CONFIG["margin"]
        )

        labels = [
            "Warehouse with Robot", "TestScene with Unity UI", "Outdoor with Robot",
            "Tornado\nMulti-Robot", "Search & Rescue\nMulti-Robot", "Hazmat\nMulti-Robot"
        ]
        keys = ["wildfire", "earthquake", "flood", "tornado", "search_rescue", "hazmat"]
        self.sim_buttons = {}

        rows = GRID_LAYOUT_CONFIG["rows"]
        cols = GRID_LAYOUT_CONFIG["cols"]

        for index, (lab, k) in enumerate(zip(labels, keys)):
            btn = QPushButton(lab)
            btn.setCheckable(True)
            btn.setStyleSheet(BUTTON_STYLE + BUTTON_HOVER_STYLE)
            btn.clicked.connect(lambda _, x=k: self.select_simulation(x))
            self.sim_buttons[k] = btn
            row = index // cols
            col = index % cols
            grid.addWidget(btn, row, col)

        v.addLayout(grid)

        run_btn = QPushButton("Run")
        run_btn.setStyleSheet(RUN_BUTTON_STYLE)
        run_btn.clicked.connect(self.run_button_handler)
        v.addStretch()
        v.addWidget(run_btn, alignment=Qt.AlignCenter)

        layout.addWidget(menu)

    def select_simulation(self, key):
        self.selected_option = key
        for k, b in self.sim_buttons.items():
            b.setChecked(k == key)

    def run_button_handler(self):
        if not self.selected_option:
            return
        cfg = self.simulations_config[self.selected_option]
        if not cfg["exe_path"]:
            return
        self.show_simulation_screen()

    def show_simulation_screen(self):
        layout = self.home_tab.layout()
        for i in reversed(range(layout.count())):
            w = layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        sim_w = QWidget()
        sim_l = QVBoxLayout(sim_w)
        sim_l.setContentsMargins(0, 0, 0, 0)
        sim_l.setSpacing(0)

        top = QWidget()
        top.setFixedHeight(int(self.height() * 0.05))
        tl = QHBoxLayout(top)
        tl.setContentsMargins(10, 5, 10, 5)
        title = QLabel(self.simulations_config[self.selected_option]["title"])
        title.setStyleSheet("color:white; font-size:16px; font-weight:bold;")
        tl.addWidget(title)
        tl.addStretch()
        cb = QPushButton("Close")
        cb.setStyleSheet("background-color:#ff5555; color:white; padding:6px;")
        cb.clicked.connect(self.stop_simulation)
        tl.addWidget(cb)
        sim_l.addWidget(top)

        ctr = QWidget()
        ctr.setFixedHeight(int(self.height() * 0.05))
        cl = QHBoxLayout(ctr)
        cl.setContentsMargins(10, 5, 10, 5)
        for txt, slot in [("Start", self.start_simulation), ("Pause", self.pause_simulation), ("Stop", self.stop_simulation)]:
            b = QPushButton(txt)
            b.setStyleSheet("padding:6px;")
            b.clicked.connect(slot)
            cl.addWidget(b)
        cl.addStretch()
        sim_l.addWidget(ctr)

        self.unity_container = QWidget()
        sim_l.addWidget(self.unity_container, stretch=1)

        self.home_tab.layout().addWidget(sim_w)
        QApplication.processEvents()

        if self.embed_unity():
            self.wait_for_socket_connection()

    def update_sensor_fields(self, data):
        for key, val in data.items():
            if key in self.fields:
                row = self.fields.index(key)
                self.sensor_table.setItem(row, 1, QTableWidgetItem(str(val)))

    def download_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Sensor Data as CSV", "sensor_data.csv", "CSV Files (*.csv)")
        if not path:
            return
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Sensor", "Value"])
            for i, name in enumerate(self.fields):
                val = self.sensor_table.item(i, 1).text() if self.sensor_table.item(i, 1) else ""
                writer.writerow([name, val])

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Training Report as PDF", "training_report.pdf", "PDF Files (*.pdf)")
        if not path:
            return
        export_training_report_pdf(
            path,
            self.simulations_config[self.selected_option]["title"],
            self.fields,
            self.sensor_table
        )

    def start_socket_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind(('localhost', 12345))
            self.server_socket.listen(5)
        except:
            return
        threading.Thread(target=self.handle_socket_connections, daemon=True).start()

    def handle_socket_connections(self):
        while True:
            try:
                self.server_socket.settimeout(15)
                client, addr = self.server_socket.accept()
                self.server_socket.settimeout(None)
                self.client_socket = client
                while True:
                    raw = client.recv(4096).decode()
                    if not raw:
                        break
                    s = raw.strip()
                    if s.startswith('{') and s.endswith('}'):
                        try:
                            data = json.loads(s)
                            self.sensor_data_signal.emit(data)
                        except:
                            pass
                    else:
                        client.send("Message received".encode())
                client.close()
                self.client_socket = None
            except:
                continue

    def wait_for_socket_connection(self, timeout=20):
        start = time.time()
        while time.time() - start < timeout:
            if self.client_socket:
                return True
            time.sleep(0.5)
        return False

    def start_simulation(self):
        self.sim_start_time = datetime.now()
        print(f"▶️ Simulation started at {self.sim_start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        if self.client_socket:
            self.client_socket.send("START".encode())

    def pause_simulation(self):
        if self.client_socket:
            self.client_socket.send("PAUSE".encode())

    def stop_simulation(self):
        if self.sim_start_time is None:
            print("⚠️ No start time recorded.")
            return

        stop_time = datetime.now()
        print(f"⏹️ Simulation stopped at {stop_time.strftime('%Y-%m-%d %H:%M:%S')}")

        cfg = self.simulations_config.get(self.selected_option, {})
        title = cfg.get("title", "")
        if "|" in title:
            disaster_type, robot_type = [x.strip() for x in title.split("|")]
        else:
            disaster_type, robot_type = title, "Unknown"

        world_map = {
            "wildfire": "Warehouse",
            "earthquake": "Office",
            "flood": "Outdoor",
            "tornado": "City",
            "search_rescue": "Underground",
            "hazmat": "Factory"
        }
        world_type = world_map.get(self.selected_option, "Unknown")

        insert_simulation_data(
            disaster_type,
            robot_type,
            world_type,
            self.sim_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            stop_time.strftime("%Y-%m-%d %H:%M:%S")
        )

        if self.client_socket:
            self.client_socket.send("STOP".encode())
        if self.unity_process:
            self.unity_process.terminate()
            self.unity_process.wait()
            self.unity_process = None
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        self.sim_start_time = None
        self.selected_option = None
        while self.tabs.count():
            self.tabs.removeTab(0)
        self.init_tabs()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.underMouse():
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def embed_unity(self):
        cfg = self.simulations_config[self.selected_option]
        path = cfg["exe_path"]
        if not path or not os.path.exists(path):
            return False
        self.unity_process = subprocess.Popen(path)
        time.sleep(3)
        def finder(hwnd, acc):
            if cfg["hwnd_title"] in win32gui.GetWindowText(hwnd):
                acc.append(hwnd)
            return True
        hwnds = []
        win32gui.EnumWindows(finder, hwnds)
        if not hwnds:
            return False
        self.unity_hwnd = hwnds[0]
        parent = self.unity_container.winId().__int__()
        win32gui.SetParent(self.unity_hwnd, parent)
        win32gui.SetWindowLong(self.unity_hwnd, win32con.GWL_STYLE, win32con.WS_VISIBLE)
        r = self.unity_container.rect()
        win32gui.MoveWindow(self.unity_hwnd, 0, 0, r.width(), r.height(), True)
        return True

    def closeEvent(self, event):
        if self.unity_process:
            self.unity_process.terminate()
            self.unity_process.wait()
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget { background-color:#282a36; color:#f8f8f2; font-size:15px; }
        QTabBar::tab { background:#44475a; color:#f8f8f2; padding:12px 20px; }
        QTabBar::tab:selected { background:#6272a4; }
    """)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()