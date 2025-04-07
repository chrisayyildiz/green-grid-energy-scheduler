from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_carbon_data():
    start = datetime.utcnow()
    end = start + timedelta(days=7)
    timestamps = pd.date_range(start=start, end=end, freq="15min", tz="UTC")

    # Simulate some carbon intensity values (can replace with real API later)
    carbon = 100 + 50 * np.sin(np.linspace(0, 12 * np.pi, len(timestamps)))

    df = pd.DataFrame({
        "timestamp": timestamps,
        "carbon_gCO2_per_kWh": carbon
    })
    df.to_csv("data/carbon_intensity.csv", index=False)
    print(f"✅ Simulated {len(df)} carbon intensity records from {start} to {end}")

if __name__ == "__main__":
    generate_carbon_data()
