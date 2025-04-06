# Green Grid Energy Scheduler

This project forecasts building energy demand and generates optimised schedules for shiftable systems based on real-time UK carbon intensity data.

## Phase 1: Carbon Intensity Data Collection

We collect real carbon intensity data from the UK National Grid Carbon Intensity API:
- 📅 Past 7 days
- ⛽ Emissions measured in gCO2/kWh
- 🧠 Stored as `data/carbon_intensity.csv` for ML model use
