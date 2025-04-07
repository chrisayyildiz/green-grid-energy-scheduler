from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
from scheduling.ortools_scheduler import schedule_tasks_ortools  # We'll create this
import datetime
from fastapi import HTTPException
import traceback

app = FastAPI(title="Green Grid Scheduler API")

from datetime import datetime, timedelta

def expand_recurring_tasks(task):
    """Expands a recurring task into individual day-based tasks."""
    expanded = []
    start_date = datetime.strptime(task["start_date"], "%Y-%m-%d")
    for i in range(task["repeat_days"]):
        day = start_date + timedelta(days=i)
        flex_start = datetime.combine(day, datetime.strptime(task["flex_start_time"], "%H:%M").time())
        flex_end = datetime.combine(day, datetime.strptime(task["flex_end_time"], "%H:%M").time())

        expanded.append({
            "name": f"{task['name']} (Day {i+1})",
            "duration_blocks": task["duration_blocks"],
            "flex_start": flex_start.isoformat(),
            "flex_end": flex_end.isoformat(),
            "energy_per_block": task["energy_per_block"]
        })
    return expanded

class Task(BaseModel):
    name: str
    duration_blocks: int
    repeat_days: int
    flex_start_time: str  # "HH:MM"
    flex_end_time: str    # "HH:MM"
    start_date: str       # "YYYY-MM-DD"
    energy_per_block: float


class ScheduleResponse(BaseModel):
    timestamp: str
    task: str
    energy_kWh: float

@app.post("/schedule", response_model=List[ScheduleResponse])
def schedule(tasks: List[Task]):
    try:
        all_tasks = []
        for task in tasks:
            expanded = expand_recurring_tasks(task.dict())
            all_tasks.extend(expanded)

        carbon_df = pd.read_csv("data/carbon_intensity.csv", parse_dates=["timestamp"])
        result_df = schedule_tasks_ortools(all_tasks, carbon_df)
        return result_df.to_dict(orient="records")
    
    except Exception as e:
        print("🔥 Internal Server Error:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
