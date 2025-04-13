# 🔌 Smart EV Charging Session Detection using Change Point Detection
**NOTE: this repository is currently work-in-progress. Not all functionality may yet be present**

This repository provides tools to detect, classify, and visualize electric vehicle (EV) charging sessions based on high-frequency household electricity load data. The analysis combines changepoint detection with heuristics to identify charging behavior and allows scaleability across thousands of smart meter profiles.

## 🚀 Overview
With the increasing penetration of EVs and smart meters, understanding when and how charging occurs is key to enabling demand-side flexibility and optimizing grid usage. This project helps:

- **Detect EV charging sessions** from noisy load profiles using changepoint detection and load thresholds.
- **Visualize sessions** by week (or month) and household, as well as across households
- **Handle multiple households** in a scalable and customizable way.

## 📦 Features
- ⚡ Changepoint detection using [`ruptures`](https://github.com/deepcharles/ruptures)
- 🔍 Heuristics to classify load spikes as charging start or end events
- 🗓️ Weekly visualization of sessions for multiple households
- 🎨 Smart colormaps for session duration
- 📊 Modular plotting per household, per week, or monthly overview

## 🧰 Project Structure
| Directory/File                        | Description                                              |
|---------------------------------------|----------------------------------------------------------|
| `data/`                               | Input data                    |
| `notebooks/`                          | Jupyter notebooks for exploration                        |
| `scripts/`                            | Python scripts for processing & plotting                 |
| `scripts/preprocessing_df.py`         | Preprocessing functions for high dimensional load profiles |
| `scripts/detect_changepoints.py`      | Core logic to detect changepoints                         |
| `scripts/detect_sessions.py`          | Core logic to detect charging sessions                   |
| `scripts/plot_changepoints.py`        | Plotting functionality for changepoints                  |
| `scripts/plot_changepoints_sessions.py`| Plotting functionality for changepoints and sessions     |
| `results/`                            | Output session detections                                |
| `README.md`                           | This file       
