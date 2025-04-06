import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_simulated_demand(start_date, days=7, seed=42):
    np.random.seed(seed)
    freq = '15min'
    end_date = start_date + timedelta(days=days)
    
    time_index = pd.date_range(start=start_date, end=end_date, freq=freq, inclusive="left")
    
    demand_values = []

    for timestamp in time_index:
        hour = timestamp.hour
        day = timestamp.weekday()  # Monday = 0, Sunday = 6

        # Office working hours: higher demand
        if day < 5:  # Weekday
            if 8 <= hour < 18:
                base = 50  # kWh per 15min
                variation = np.random.normal(0, 5)
            elif 6 <= hour < 8 or 18 <= hour < 20:
                base = 30
                variation = np.random.normal(0, 3)
            else:
                base = 15
                variation = np.random.normal(0, 2)
        else:  # Weekend
            if 9 <= hour < 17:
                base = 20
                variation = np.random.normal(0, 3)
            else:
                base = 10
                variation = np.random.normal(0, 1.5)

        # Friday adjustment
        if day == 4 and hour >= 16:
            base *= 0.7

        demand = max(base + variation, 0)  # Avoid negatives
        demand_values.append(demand)

    df = pd.DataFrame({
        'timestamp': time_index,
        'simulated_demand_kWh': demand_values
    })

    return df

if __name__ == "__main__":
    start = datetime.utcnow() - timedelta(days=7)
    df = generate_simulated_demand(start_date=start)
    df.to_csv("data/simulated_energy_demand.csv", index=False)
    print("✅ Simulated demand saved to data/simulated_energy_demand.csv")