# Green Grid Energy Scheduler

A machine learning-powered optimiser that helps commercial buildings schedule their non-critical energy tasks during periods of low grid carbon intensity.  
Built with FastAPI, Streamlit, Prophet, and Google OR-Tools.

---

## What’s it for?

This system answers a simple but important question:

> _"When should I run high-energy systems (like AC or Fleet EV charging) to reduce my carbon footprint?"_

It uses:
- **Prophet** to forecast future grid carbon intensity (7 days ahead)
- **OR-Tools** to optimise task schedules across time and constraints
- **FastAPI** as a backend service
- **Streamlit** to give users a clean, interactive dashboard

---

## Tech Stack

| Component       | Technology                          |
|----------------|--------------------------------------|
| Forecasting     | Prophet (carbon intensity prediction) |
| Scheduling      | Google OR-Tools (CP-SAT)            |
| Backend API     | FastAPI                             |
| User Interface  | Streamlit                           |
| Dev Environment | GitHub Codespaces / Docker-ready    |

---

## Key Features

- **Machine Learning Forecasting**  
  Uses Prophet to forecast 7 days of grid carbon intensity using real UK National Grid data.

- **Multi-task, multi-day scheduling**  
  Optimise multiple systems with different energy requirements and windows.

- **Interactive Dashboard**  
  Define tasks, run the optimiser, and visualise results in seconds.

- **Modular Design**  
  Clean separation between ML, API, optimiser, and UI — easy to build on.
