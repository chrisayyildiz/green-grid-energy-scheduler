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
        window_start_time = pd.to_datetime(task['flex_start']).tz_localize("UTC")
        window_end_time = pd.to_datetime(task['flex_end']).tz_localize("UTC")
        repeat_days = task.get("repeat_days", 1)

        for day_offset in range(repeat_days):
            day_label = f" (Day {day_offset + 1})" if repeat_days > 1 else ""
            task_name = f"{task['name']}{day_label}"

            day_start = window_start_time + timedelta(days=day_offset)
            day_end = window_end_time + timedelta(days=day_offset)

            # Find slot indices for flexibility window
            valid_slots = carbon_df[
                (carbon_df["ds"] >= day_start) &
                (carbon_df["ds"] <= day_end - timedelta(minutes=15 * duration))
            ].reset_index(drop=True)

            if valid_slots.empty:
                raise ValueError(f"No valid time slots for task '{task_name}' in the given window.")

            start_min = carbon_df[carbon_df["ds"] == valid_slots.iloc[0]["ds"]].index[0]
            start_max = start_min + len(valid_slots) - 1

            unique_name = f"{task_name}_{start_min}_{start_max}"
            start_var = model.NewIntVar(start_min, start_max, unique_name)
            task_vars[task_name] = start_var

            for i in range(duration):
                slot_index = model.NewIntVar(0, num_slots - 1, f"slot_{task_name}_{i}")
                model.Add(slot_index == start_var + i)

                idx = start_min + i
                carbon = int(task['energy_per_block'] * 1000)  # Convert to Wh

                if idx < len(carbon_values) and not math.isnan(carbon_values[idx]):
                    carbon_cost = carbon_values[idx]
                else:
                    carbon_cost = 9999  # Penalise unknowns

                weighted_cost = int(carbon * carbon_cost)
                objective_terms.append(weighted_cost)

    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        schedule = []
        for task_name, start_var in task_vars.items():
            start_idx = solver.Value(start_var)
            energy_kWh = next(t["energy_per_block"] for t in tasks if t["name"] in task_name)
            duration = next(t["duration_blocks"] for t in tasks if t["name"] in task_name)

            for i in range(duration):
                ts = carbon_df.iloc[start_idx + i]["ds"]
                schedule.append({
                    "timestamp": ts.isoformat(),
                    "task": task_name,
                    "energy_kWh": energy_kWh
                })

        return pd.DataFrame(schedule)
    else:
        raise Exception("No feasible schedule found.")