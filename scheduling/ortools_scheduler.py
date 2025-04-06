from ortools.sat.python import cp_model
import pandas as pd
import math

# Load 1-day carbon intensity forecast (96 rows @ 15min intervals)
carbon_df = pd.read_csv("data/carbon_intensity.csv", parse_dates=["timestamp"])
carbon_df = carbon_df.set_index("timestamp").resample("15min").mean().reset_index()
carbon_df["carbon_gCO2_per_kWh"] = carbon_df["carbon_gCO2_per_kWh"].interpolate().bfill().ffill()
carbon_df = carbon_df.head(96)  # Trim to 1-day view for now

# OR-Tools prep
model = cp_model.CpModel()

# Define time slots
num_slots = len(carbon_df)
slot_duration_min = 15

# Example tasks
tasks = [
    {
        "name": "EV Charger",
        "duration": 8,  # 2 hours
        "window_start": 0,
        "window_end": 32,  # Can run anytime between 00:00–08:00
        "energy_kWh": 7.5
    },
    {
        "name": "Preheat HVAC",
        "duration": 4,
        "window_start": 20,
        "window_end": 32,
        "energy_kWh": 5.0
    },
    {
        "name": "Water Heater",
        "duration": 4,
        "window_start": 24,
        "window_end": 40,
        "energy_kWh": 3.0
    }
]

# Decision variables: task start times
task_vars = {}
for task in tasks:
    task_vars[task['name']] = model.NewIntVar(
        task['window_start'],
        task['window_end'] - task['duration'],
        f"start_{task['name']}"
    )

# Objective: minimise total carbon emitted from all task energy
carbon_values = carbon_df["carbon_gCO2_per_kWh"].values

objective_terms = []
for task in tasks:
    start_var = task_vars[task['name']]
    for i in range(task['duration']):
        slot_index = model.NewIntVar(0, num_slots - 1, f"slot_{task['name']}_{i}")
        model.Add(slot_index == start_var + i)

        carbon = int(task['energy_kWh'] * 1000)  # Convert kWh to Wh for granularity
        idx = i + task['window_start']
        if idx < len(carbon_values) and not math.isnan(carbon_values[idx]):
            carbon_cost = carbon_values[idx]
        else:
            carbon_cost = 9999  # Penalise unknowns heavily

        weighted_cost = int(carbon * carbon_cost)
        objective_terms.append(weighted_cost)

model.Minimize(sum(objective_terms))

# Solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("✅ Optimised schedule:")
    schedule = []
    for task in tasks:
        start = solver.Value(task_vars[task['name']])
        for i in range(task['duration']):
            timestamp = carbon_df.iloc[start + i]["timestamp"]
            schedule.append({
                "timestamp": timestamp,
                "task": task["name"],
                "energy_kWh": task["energy_kWh"]
            })
            print(f"{task['name']} at {timestamp}")
    pd.DataFrame(schedule).to_csv("data/shifted_schedule_ortools.csv", index=False)
else:
    print("❌ No solution found.")
