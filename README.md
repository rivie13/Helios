# Helios UI

## ✅ How to Run

### Install dependencies
Make sure Python 3 is installed and install required libraries:

#### Setting up a virtual environment (recommended)
Create and activate a virtual environment to isolate project dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate
```

#### Install required packages
```bash
pip install -r requirements.txt
```

### Run the app
Navigate to your project directory and run:

```bash
python main.py
```

> **Note:** If you have a different version of Python installed, use the appropriate command (e.g., `python3` or full path to python.exe).

## 🛠️ Important Setup
Make sure all paths for your Unity build files are correct for your device.

Update the CSV path in `insert_data.py` and `table.py` to point to the dashboard_data.csv in your project:

```python
CSV_PATH = r"path/to/your/project/dashboard_data.csv"
```

```python
csv_path = r"path/to/your/project/dashboard_data.csv"
```

## 🧩 Adding a Unity Simulation
To add a Unity world to the simulation menu:

### Build the Unity Project

1. Open your Unity scene.
2. Go to File > Build Settings, select Windows platform, and build your .exe file.

### Update the Config

1. In `main.py`, locate the `__init__` method and find the `self.simulations_config` dictionary.
2. Add a new entry in the following format:

```python
"my_custom_sim": {
    "exe_path": r"C:\\Full\\Path\\To\\Your\\UnityBuild.exe",
    "title": "My Custom Scenario",
    "hwnd_title": "UnityBuild"
}
```

- `exe_path`: Full file path to your Unity .exe.
- `title`: Display name in the UI.
- `hwnd_title`: Must match the window title of your Unity build.

### Restart the App

Your Unity world will appear as a new option in the simulation dashboard.

## 📦 Preconfigured Simulations
The following simulations are included by default:

```python
self.simulations_config = {
    "wildfire": {
        "exe_path": r"path/to/your/RoboticsNav2SLAMExample.exe",
        "title": "Wild Fire | Multi-Robot",
        "hwnd_title": "RoboticsNav2SLAMExample"
    },
    "earthquake": {
        "exe_path": os.path.abspath("build/UnityHelios.exe"),
        "title": "Earthquake | Single-Robot",
        "hwnd_title": "UnityHelios"
    },
    "flood": {
        "exe_path": os.path.abspath("path/to/your/Helios.exe"),
        "title": "Flood | Single-Robot",
        "hwnd_title": "Helios"
    },
    "tornado": {
        "exe_path": None,
        "title": "Tornado | Multi-Robot",
        "hwnd_title": None
    },
    "search_rescue": {
        "exe_path": None,
        "title": "Search & Rescue | Multi-Robot",
        "hwnd_title": None
    },
    "hazmat": {
        "exe_path": None,
        "title": "Hazmat | Multi-Robot",
        "hwnd_title": None
    }
}
```

## 📊 Features
- Frameless PyQt5 GUI with a custom title bar
- Dynamically loaded Unity scenarios
- PDF export with graph visualizations (temperature, humidity, battery, position)
- Socket communication with Unity for live sensor data
