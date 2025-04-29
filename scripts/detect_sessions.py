import numpy as np
import ruptures as rpt
import matplotlib.pyplot as plt
import pandas as pd

def detect_sessions(df, aggregated_breakpoints, contrib_features_dict, max_kw_column="max_kw", threshold=1):
    """
    Identify charging sessions by classifying aggregated changepoints into start or end.
    
    Parameters:
    - df: DataFrame with datetime index and columns representing the load profile.
    - aggregated_breakpoints: List of aggregated changepoints (from the `filter groups` function).
    - contrib_features_dict: Dictionary with breakpoints as keys and their contributing features as values.
    - max_kw_column: The column representing the maximum load per timestamp (default is "max_kw").
    - threshold: The threshold for determining a significant change in load.
    
    Returns:
    - sessions: List of tuples where each tuple represents a charging session (start, end).
    """
    
    sessions = []

    if not isinstance(df.index, pd.DatetimeIndex):
        if "datetime" in df.columns:
            df = df.set_index("datetime")
        else:
            raise ValueError("DataFrame must have a datetime column or a DatetimeIndex.")
    
    # Loop through the aggregated breakpoints
    for i, bkp in enumerate(aggregated_breakpoints):
        # Get the surrounding window (1 hour before and after the changepoint)
        start_time = bkp - pd.Timedelta(hours=2)
        end_time = bkp + pd.Timedelta(hours=2)
        
        # Get the max load values before and after the changepoint
        before_load = df.loc[start_time:bkp, max_kw_column].min()
        after_load = df.loc[bkp:end_time, max_kw_column].max()
   
        # Heuristic to classify changepoint as start based on load change
        if after_load - before_load > threshold:
            
            # Define start of charging session:
            session_start = bkp # breakpoint start charging
            before_load = after_load # update before_load, because we are now in the charging session
            
            # Find the end changepoint (look ahead)
            if i + 1 < len(aggregated_breakpoints):
                next_bkp = aggregated_breakpoints[i + 1] # breakpoint end charging
                end_time = next_bkp + pd.Timedelta(hours=2) # 2 hours after end charging
                after_end_load = df.loc[next_bkp:end_time, max_kw_column].min() # kW use after end charging

                if before_load - after_end_load > threshold:  # condition for charging session
                    session_end = next_bkp 
                    session_duration = session_end - session_start
            
                    if session_duration <= pd.Timedelta(hours=24):
                        sessions.append((session_start, session_end))
                    
    return sessions


