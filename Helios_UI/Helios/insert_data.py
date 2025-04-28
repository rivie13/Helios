import csv
from datetime import datetime

# UPDATE THIS PATH TO THE CORRECT PATH FOR YOUR SYSTEM
CSV_PATH = r"C:\Users\rivie\Helios\Helios_UI\dashboard_data.csv"

def insert_simulation_data(disaster_type, robot_type, world_type, start_time, stop_time):
    # Calculate resolution time in seconds
    fmt = "%Y-%m-%d %H:%M:%S"
    start_dt = datetime.strptime(start_time, fmt)
    stop_dt = datetime.strptime(stop_time, fmt)
    resolution_seconds = round((stop_dt - start_dt).total_seconds(), 1)

    # Prepare row to write
    row = [
        robot_type,
        world_type,
        disaster_type,
        str(resolution_seconds),
        "True",
        start_time,
        stop_time
    ]

    # Append to CSV
    try:
        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)
        print("✅ Simulation data saved to CSV.")
    except Exception as e:
        print(f"❌ Failed to write to CSV: {e}")
