import matplotlib.pyplot as plt
import pandas as pd
import numpy as np 
import os

def preprocessing(df):
    
    """
    INPUT
    1. a DataFrame for a single EAN_ID containing at least the columns
    'EAN_ID', 'datetime' and 'afname_kw'. 

    We will assume no 'productie_kw' is available, such as to force the algorithm to decide based on grid withdrawals. 
    
    THROUGHPUT
    1. Preprocess the given DataFrame with metering data:  
    Convert 'datetime' to datetime format and sort by meter ('ean_id') and time ('datetime')
    2. Convert the consumption from 15-min kWh values to instantaneous kW (kW = kWh * 4).
    3. Resample the data to hourly blocks (each block aggregating 4 intervals).
    4. For each hour, compute general statistics on the kWh/kW values: total, mean, min, max, range (max - min)

    OUTPUT
    A new DataFrame with one row per hour and a 'datetime' column representing the hour.
    
    """
    
    # Ensure datetime is in proper format
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)
    df["year"] = df["datetime"].dt.year
    df["moy"] = df["datetime"].dt.month
    df["day"] = df["datetime"].dt.day
    df["hour"] = df["datetime"].dt.hour

    # Sort by datetime
    df = df.sort_values(by=["EAN_ID", "datetime"])
    
    # Set index
    df = df.set_index('datetime')
    
    df['afname_kwh'] = df['afname_kwh']
    df['afname_kw'] = df['afname_kwh'] * 4

    # Resample to hourly groups (each hour aggregates 4 15-min intervals)
    hourly_groups = df.resample('h')
    
    features_list = []
    
    for hour_dt, group in hourly_groups:
        if group.empty:
            continue

        # Consumption values (kWh) within the hour
        kwh = group['afname_kwh']
        kw = group['afname_kw']

        # --- General hourly statistics ---
        total_kwh   = kwh.sum()
        min_kw      = kw.min()
        max_kw      = kw.max()
        range_kw    = max_kw - min_kw
        max_kw      = kw.max()

        # --- DataFrame construction ---
        features = {
            'datetime': hour_dt,
            'total_kwh': total_kwh,
            'max_kw': max_kw,
            'range_kw': range_kw
        }
        
        features_list.append(features)
    
    features_df = pd.DataFrame(features_list)
    
    return features_df
