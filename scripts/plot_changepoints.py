import matplotlib.pyplot as plt
import pandas as pd
import numpy as np 
import os


def plot_changepoints(aggregated_breakpoints, contrib_features_dict, features_df):
    """
    Plot time series data for all contributing features and overlay aggregated changepoints.
    
    INPUT:
    - aggregated_breakpoints: List of timestamps corresponding to aggregated changepoints.
    - contrib_features_dict: Dictionary mapping each changepoint to a list of contributing feature names.
    - features_df: Original DataFrame with datetime index and feature columns.
    
    OUTPUT:
    - Time series plot with all contributing features and overlaid aggregated changepoints
        
    """
    plt.figure(figsize=(16, 10))
    
    
    # Initialize colours
    line_styles = ['solid', 'dashed', 'dotted', 'dashdot']
    colors = ['black', 'dimgray', 'gray', 'darkgray']

    # Ensure datetime is the index. If not, try to set it.
    if not isinstance(features_df.index, pd.DatetimeIndex):
        if "datetime" in features_df.columns:
            features_df = features_df.set_index("datetime")
        else:
            raise ValueError("DataFrame must have a datetime column or a DatetimeIndex.")

    # Collect all contributing features across all aggregated breakpoints
    # INPUT: dictionary mapping each changepoint to a list of contributing features.
    # OUTPUT: alphabetically sorted list containing all unique contributing features, duplicates removed
    all_contrib_features = sorted(set(f for lst in contrib_features_dict.values() for f in lst))

    # Plot each contributing feature
    for i, feature in enumerate(all_contrib_features):
        style = line_styles[i % len(line_styles)]
        color = colors[i % len(colors)]
        plt.plot(features_df.index, features_df[feature], linestyle=style, color=color,
                 label=feature, linewidth=1.5)

    # Plot vertical lines for each aggregated breakpoint
    for agg_bkp in aggregated_breakpoints:
        plt.axvline(x=agg_bkp, color="red", linestyle="--", linewidth=2,
                    label="Aggregated Breakpoint" if agg_bkp == aggregated_breakpoints[0] else "")
    
    # Plot
    plt.xlabel("Datetime", fontsize=14)
    plt.ylabel("Feature Value", fontsize=14)
    plt.title("Aggregated Breakpoints with Contributing Features", fontsize=16)
    plt.legend(fontsize=12, loc="upper right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()