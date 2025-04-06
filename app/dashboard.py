import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Green Grid Scheduler", layout="wide")

st.title("⚡ Green Grid Energy Scheduler Dashboard")

# Load data
@st.cache_data
def load_data():
    carbon = pd.read_csv("data/carbon_intensity.csv", parse_dates=["timestamp"])
    schedule = pd.read_csv("data/shifted_schedule_ortools.csv", parse_dates=["timestamp"])
    return carbon, schedule

carbon_df, schedule_df = load_data()
schedule_df["hour"] = schedule_df["timestamp"].dt.strftime("%H:%M")
schedule_df["date"] = schedule_df["timestamp"].dt.date

# Merge carbon + schedule
merged = pd.merge(schedule_df, carbon_df, on="timestamp", how="left")

# --- Section 1: Task Instructions ---
st.subheader("📋 Task Instructions")

instructions = merged.groupby("task").agg(
    start_time=("timestamp", "min"),
    duration=("timestamp", "count")
).reset_index()

# Ensure start_time is in the right format
instructions["start_time"] = pd.to_datetime(instructions["start_time"])

instructions["instruction"] = instructions.apply(
    lambda row: f"Run **{row.task}** at **{row.start_time.strftime('%H:%M')}** for **{row.duration * 15} mins**.",
    axis=1
)

# Display the task instructions
for i, row in instructions.iterrows():
    st.markdown(f"- {row['instruction']}")

