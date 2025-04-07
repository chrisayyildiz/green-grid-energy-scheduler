import streamlit as st
import pandas as pd
import httpx

# 🔗 Update with your actual FastAPI Codespace URL
API_URL = "http://127.0.0.1:8000/schedule"

st.set_page_config(page_title="Green Grid Scheduler", layout="centered")
st.title("⚡ Green Grid Energy Scheduler")

# 💾 Initialise session state to hold multiple tasks
if "task_list" not in st.session_state:
    st.session_state.task_list = []

st.subheader("📋 Add Task to Schedule")

# Task input form
with st.form("task_form"):
    name = st.text_input("Task Name", "EV Charger")
    duration_blocks = st.slider("Duration (15-min blocks)", 1, 12, 4)
    repeat_days = st.slider("Repeat for how many days?", 1, 7, 3)
    flex_start_time = st.time_input("Flexible start time", value=pd.to_datetime("06:00").time())
    flex_end_time = st.time_input("Flexible end time", value=pd.to_datetime("08:00").time())
    start_date = st.date_input("Start date", pd.to_datetime("2025-04-08").date())
    energy_per_block = st.number_input("Energy per block (kWh)", min_value=0.1, value=5.0)

    col1, col2 = st.columns(2)
    with col1:
        add_task = st.form_submit_button("➕ Add Task")
    with col2:
        clear_tasks = st.form_submit_button("🗑️ Clear All")

# Add task to session state
if add_task:
    new_task = {
        "name": name,
        "duration_blocks": duration_blocks,
        "repeat_days": repeat_days,
        "flex_start_time": flex_start_time.strftime("%H:%M"),
        "flex_end_time": flex_end_time.strftime("%H:%M"),
        "start_date": str(start_date),
        "energy_per_block": energy_per_block
    }
    st.session_state.task_list.append(new_task)
    st.success(f"✅ Added task: {name}")

# Clear all tasks
if clear_tasks:
    st.session_state.task_list = []
    st.info("🧹 Cleared all tasks")

# Show current task queue
if st.session_state.task_list:
    st.subheader("🧾 Task List")
    st.dataframe(pd.DataFrame(st.session_state.task_list))

    if st.button("🚀 Generate Optimised Schedule"):
        with st.spinner("Contacting API..."):
            try:
                tasks = st.session_state.task_list
                response = httpx.post(API_URL, json=tasks)
                response.raise_for_status()
                schedule = response.json()
                df = pd.DataFrame(schedule)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                st.success("✅ Optimised schedule created!")
                st.dataframe(df)
                st.line_chart(df.set_index("timestamp")["energy_kWh"])
            except httpx.RequestError as e:
                st.error(f"❌ API connection error: {e}")
            except httpx.HTTPStatusError as e:
                st.error(f"❌ Server error: {e.response.text}")
else:
    st.warning("⚠️ No tasks added yet")
