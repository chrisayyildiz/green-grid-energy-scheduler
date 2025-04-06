# Green Grid Energy Scheduler

This project forecasts building energy demand and generates optimised schedules for shiftable systems based on real-time UK carbon intensity data.

## Phase 1: Carbon Intensity Data Collection

We collect real carbon intensity data from the UK National Grid Carbon Intensity API:
- 📅 Past 7 days
- ⛽ Emissions measured in gCO2/kWh
- 🧠 Stored as `data/carbon_intensity.csv` for ML model use

### ✅ Phase 5: Streamlit Dashboard (Updated)

- Displays scheduled task energy overlaid on grid carbon intensity
- Human-readable task instructions generated from schedule
- Summary of estimated carbon emissions per schedule
- Built with Streamlit + Matplotlib
