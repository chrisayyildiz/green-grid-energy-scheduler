from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
from scheduling.ortools_scheduler import schedule_tasks_ortools  # We'll create this
import datetime

app = FastAPI(title="Green Grid Scheduler API")

class Task(BaseModel):
    name: str
    duration_blocks: int  # 1 block = 15 min
    flex_start: str       # ISO 8601 datetime string
    flex_end: str
    energy_per_block: float

class ScheduleResponse(BaseModel):
    timestamp: str
    task: str
    energy_kWh: float

@app.post("/schedule", response_model=List[ScheduleResponse])
def schedule(tasks: List[Task]):
    task_dicts = [task.dict() for task in tasks]
    carbon_df = pd.read_csv("data/carbon_intensity.csv", parse_dates=["timestamp"])
    result_df = schedule_tasks_ortools(task_dicts, carbon_df)
    return result_df.to_dict(orient="records")
