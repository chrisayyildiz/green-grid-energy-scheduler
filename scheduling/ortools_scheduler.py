from ortools.sat.python import cp_model
import pandas as pd
from datetime import timedelta
import math

def schedule_tasks_ortools(tasks, carbon_df):
    """
    Schedules tasks using Google OR-Tools to minimise carbon emissions.
    
    Parameters:
        tasks (list of dict): Each task must have keys:
            - name
            - duration_blocks (int)
            - flex_start (ISO string)
            - flex_end (ISO string)
            - energy_per_block (float)
        carbon_df (DataFrame): Must include 'timestamp' and 'carbon_gCO2_per_kWh' columns

    Returns:
        pd.DataFrame with scheduled tasks and timestamps
    """
    model = cp_model.CpModel()

    # Preprocess carbon dataframe
    carbon_df = carbon_df.copy()
    carbon_df = carbon_df.rename(columns={"timestamp": "ds"})
    carbon_df = carbon_df.set_index("ds").resample("15min").mean().reset_index()
    carbon_df["carbon_gCO2_per_kWh"] = carbon_df["carbon_gCO2_per_kWh"].interpolate().bfill().ffill()

    num_slots = len(carbon_df)
    carbon_values = carbon_df["carbon_gCO2_per_kWh"].values

    task_vars = {}
    objective_terms = []

    for task in tasks:
        duration = task['duration_blocks']
        window_start_time = pd.to_datetime(task['flex_start'])
        window_end_time = pd.to_datetime(task['flex_end'])

        # Find slot indices for flexibility window
        valid_slots = carbon_df[
            (carbon_df["ds"] >= window_start_time) &
            (carbon_df["ds"] <= window_end_time - timedelta(minutes=15 * duration))
        ].reset_index(drop=True)

        if valid_slots.empty:
            raise ValueError(f"No valid time slots for task '{task['name']}' in the given window.")

        start_min = carbon_df[carbon_df["ds"] == valid_slots.iloc[0]["ds"]].index[0]
        start_max = start_min + len(valid_slots) - 1

        start_var = model.NewIntVar(start_min, start_max, f"start_{task['name']}")
        task_vars[task['name']] = start_var

        for i in range(duration):
            slot_index = model.NewIntVar(0, num_slots - 1, f"slot_{task['name']}_{i}")
            model.Add(slot_index == start_var + i)

            idx = i + start_min
            carbon = int(task['energy_per_block'] * 1000)  # Convert to Wh for granularity

            if idx < len(carbon_values) and not math.isnan(carbon_values[idx]):
                carbon_cost = carbon_values[idx]
            else:
                carbon_cost = 9999  # Penalise unknowns

            weighted_cost = int(carbon * carbon_cost)
            objective_terms.append(weighted_cost)

    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        schedule = []
        for task in tasks:
            start_idx = solver.Value(task_vars[task['name']])
            for i in range(task['duration_blocks']):
                ts = carbon_df.iloc[start_idx + i]["ds"]
                schedule.append({
                    "timestamp": ts.isoformat(),
                    "task": task["name"],
                    "energy_kWh": task["energy_per_block"]
                })
        return pd.DataFrame(schedule)
    else:
        raise Exception("No feasible schedule found.")
