import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import timedelta

def plot_changepoints_sessions_multiple(results, month, eans_to_plot=None):
    """
    Plot charging sessions over time for multiple EANs, showing 1 plot per week in the selected month.
    
    INPUT:
    - results: dictionary with EAN / month and of tuples representing charging sessions, each containing a start and end timestamp.
    - month: the month to plot.
    - eans_to_plot: list of EANs to include. If None, all available EANs in the dictionary will be used.
    
    OUTPUT
    - Graphical representation for identified changepoints over multiple EANs
    """
    
    # Filter EANs with available data for the selected month
    available_eans = [ean for ean in results if month in results[ean]]
    if eans_to_plot is None:
        eans_to_plot = available_eans
    else:
        eans_to_plot = [ean for ean in eans_to_plot if ean in available_eans]

    if not eans_to_plot:
        print(f"No data found for the specified EANs in month {month}.")
        return

    # Collect all week start dates across selected EANs
    all_week_starts = set()
    for ean in eans_to_plot:
        all_week_starts.update(results[ean][month].keys())
    week_starts_sorted = sorted(all_week_starts)

    if not week_starts_sorted:
        print(f"No week-level data found for selected EANs in month {month}.")
        return

    # Generate one plot per week
    for week_start in week_starts_sorted:
        fig, ax = plt.subplots(figsize=(14, 0.6 * len(eans_to_plot) + 2))
        week_start = pd.to_datetime(week_start)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59)

        for i, ean in enumerate(sorted(eans_to_plot)):
            y_pos = len(eans_to_plot) - 1 - i
            week_data = results[ean][month].get(week_start.date(), {})
            for session in week_data.get("sessions", []):
                start, end = pd.to_datetime(session[0]), pd.to_datetime(session[1])
                duration = (end - start).total_seconds() / 3600
                norm_duration = min(1, duration / 8)
                color = plt.cm.Blues(0.3 + 0.7 * norm_duration)  # short = light, long = dark
                ax.plot([start, end], [y_pos, y_pos], lw=6, solid_capstyle='round', color=color, alpha=0.8)

        # Y-axis
        ax.set_yticks(range(len(eans_to_plot)))
        ax.set_yticklabels(sorted(eans_to_plot))
        ax.set_ylabel("EAN ID")

        # X-axis
        ax.set_xlim(week_start, week_end)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%H:%M'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45)

        # Title and grid
        ax.set_title(f"Charging Sessions – Week of {week_start.strftime('%Y-%m-%d')}", fontsize=14)
        ax.set_xlabel("Date and Time")
        ax.grid(True, axis='x', linestyle='--', alpha=0.3)

        plt.tight_layout()
        plt.show()
