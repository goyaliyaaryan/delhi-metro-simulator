# 🚇 Delhi Metro Simulator & Journey Planner

A **Python-based simulation of the Delhi Metro system** that allows users to:
- Check upcoming trains at any station
- Plan complete journeys with multiple interchanges
- Calculate travel time, stations covered, and fare

This project focuses on **real-world system modeling, algorithmic route planning, and clean software design**.

---

## ✨ Features

- 📍 Next 6 trains at any station (both directions)
- 🧭 End-to-end journey planning
- 🔁 Supports **multiple interchanges**
- ⏱ Accurate time calculation with train frequency
- 💰 Fare calculation based on number of stations
- 🔄 Bidirectional line support
- ❌ Robust input & error handling
- 📊 Uses real Delhi Metro route data

---

## 🧠 How It Works (High-Level)

- Metro lines and stations are stored in a structured data file
- Routes are computed by:
  - Checking direct paths
  - Testing all valid interchange paths
- The system chooses the **shortest-time route**
- A fixed interchange penalty (+5 min) is applied
- Fare is calculated based on station count

---

## ▶️ How to Run

```bash
python3 metro_simulator_2025595.py
