import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ruptures as rpt

def detect_changepoints(
    features_df,
    method="pelt",
    model="l2",
    min_size_hours=2,
    penalty=3,
    merge_tolerance_hours=4,
    n_contributing_features=2,
    window_width=10
):
    """
    Detect changepoints in hourly interval smart meter data using various ruptures algorithms.

    INPUT:
        features_df:                      DataFrame with datetime index or 'datetime' column.
        method:                           Changepoint detection method. Allowed values: 'pelt', 'binseg', 'window', or 'bottomup' (default = 'pelt')
        model:                            Cost model. Allowed values: 'l1', 'l2' (default = 'l2')
        min_size_hours:                   Minimum segment length (default = 2).
        penalty:                          Penalty value for the algorithm: higher penalty reduces number of breakpoints detected (default = 3)
        merge_tolerance_hours:            How close changepoints can be merged. Allowed values: scalars, in hours (default = 4).
        n_contributing_features:          Minimum number of features that need to contribute to a breakpoint (default = 2)
        window_width:                     Window width for changepoint detection in the 'window' method (default = 10 hours)

    OUTPUT:
        aggregated_breakpoints:           List of timestamps with aggregated changepoints.
        contrib_features_dict:            Maps each timestamp to a list of contributing features.
    """

    # Ensure datetime is the index
    if not isinstance(features_df.index, pd.DatetimeIndex):
        if "datetime" in features_df.columns:
            features_df = features_df.set_index("datetime")
        else:
            raise ValueError("DataFrame must have a datetime column or a DatetimeIndex.")

    breakpoints_per_feature = {}

    # Loop over each feature
    for column in features_df.columns:
        signal = features_df[column].dropna().values
        if len(signal) < 2 * min_size_hours:
            continue

        # Select algorithm
        if method == "pelt":
            algo = rpt.Pelt(model=model, min_size=min_size_hours).fit(signal)
            result = algo.predict(pen=penalty)[:-1]
        elif method == "binseg":
            algo = rpt.Binseg(model=model, min_size=min_size_hours).fit(signal)
            result = algo.predict(pen=penalty)[:-1]
        elif method == "window":
            algo = rpt.Window(width=window_width, min_size=min_size_hours, model=model).fit(signal)
            result = algo.predict(pen=penalty)[:-1]
        elif method == "bottomup":
            algo = rpt.BottomUp(model=model, min_size=min_size_hours).fit(signal)
            result = algo.predict(pen=penalty)[:-1]
        else:
            raise ValueError(f"Unknown method: {method}. Choose from 'pelt', 'binseg', 'window', 'bottomup'.")

        breakpoints_per_feature[column] = [features_df.index[bkp] for bkp in result]

    # Merge breakpoints
    bkp_records = [(bkp, feat) for feat, bkps in breakpoints_per_feature.items() for bkp in bkps]
    bkp_records = sorted(bkp_records, key=lambda x: x[0])

    tolerance_merge = pd.Timedelta(hours=merge_tolerance_hours)
    aggregated_groups, used = [], [False] * len(bkp_records) # storage for (bkp, feat)-tuples that belong to the same group (breakpoints close in time)

    for i in range(len(bkp_records)):
        if used[i]: continue
        current_group = [bkp_records[i]]
        used[i] = True # set breakpoint to used
        for j in range(i+1, len(bkp_records)):
            if used[j]: continue
            if abs(bkp_records[j][0] - bkp_records[i][0]) <= tolerance_merge:
                current_group.append(bkp_records[j]) # append breakpoint to group if close in time.
                used[j] = True
        aggregated_groups.append(current_group)

    # Filter and aggregate: store median breakpoint time
    aggregated_breakpoints = []
    contrib_features_dict = {}

    for group in aggregated_groups:
        features_in_group = list({feat for _, feat in group})
        if len(features_in_group) >= n_contributing_features:
            timestamps = [bkp for bkp, _ in group]
            median_bkp = pd.Series(timestamps).median()
            aggregated_breakpoints.append(median_bkp)
            contrib_features_dict[median_bkp] = features_in_group

    return aggregated_breakpoints, contrib_features_dict



# def detect_changepoints(features_df, 
#                         min_size_hours=600, 
#                         penalty=3, 
#                         merge_tolerance_hours=5):
#     """
#     Detect changepoints in a time series DataFrame based on multiple features.
    
#     INPUT:
#         1. features_df (pd.DataFrame): DataFrame with a datetime column and features. 
#         It is verified in the code if 'datetime' is one of the columns or the index.
#         2. min_size_hours: Minimum length in hours individual changepoints
#         3. penalty: Penalty parameter for the PELT algorithm.
#         4. merge_tolerance_hours: Hours within which breakpoints are merged.
        
#     OUTPUT:
#         aggregated_breakpoints: List of changepoint timestamps. The final list aggregates contributions from the different input features into a final decision..
#         contrib_features_dict: Dictionary mapping each aggregated changepoint to the list of contributing features.
#     """
    
#     # Ensure datetime is the index. If not, try to set it.
#     if not isinstance(features_df.index, pd.DatetimeIndex):
#         if "datetime" in features_df.columns:
#             features_df = features_df.set_index("datetime")
#         else:
#             raise ValueError("DataFrame must have a datetime column or a DatetimeIndex.")

#     # Initialize dictionary to hold breakpoints for each feature.
#     breakpoints_per_feature = {}
    
#     # Run changepoint detection per feature.
#     for column in features_df.columns:
#         signal = features_df[column].dropna().values
#         if len(signal) < 2 * min_size_hours:  # Ensure enough data
#             continue
        
#         # Run the PELT algorithm for this feature.
#         algo = rpt.Pelt(model="l2", min_size=min_size_hours).fit(signal)
#         result = algo.predict(pen=penalty)[:-1]  # Exclude the last point (end of series)
#         breakpoints_per_feature[column] = [features_df.index[bkp] for bkp in result]
    
#     # Parameters for merging breakpoints.
#     tolerance_merge = pd.Timedelta(hours=merge_tolerance_hours)
    
#     # Step 1: Collect all breakpoints along with their corresponding feature labels.
#     bkp_records = []
#     for feature, bkps in breakpoints_per_feature.items():
#         for bkp in bkps:
#             bkp_records.append((bkp, feature))
    
#     # Step 2: Sort breakpoints and merge those within the merge tolerance.
#     bkp_records = sorted(bkp_records, key=lambda x: x[0])
#     aggregated_groups = []
#     used = [False] * len(bkp_records)
    
#     for i in range(len(bkp_records)):
#         if used[i]:
#             continue
#         current_group = [bkp_records[i]]
#         used[i] = True
#         for j in range(i + 1, len(bkp_records)):
#             if used[j]:
#                 continue
#             if abs(bkp_records[j][0] - bkp_records[i][0]) <= tolerance_merge:
#                 current_group.append(bkp_records[j])
#                 used[j] = True
#         aggregated_groups.append(current_group)
    
#     # Step 3: Filter groups that have at least 2 unique contributing features.
#     aggregated_breakpoints = []
#     contrib_features_dict = {}
    
#     for group in aggregated_groups:
#         features_in_group = list({feat for _, feat in group})
#         if len(features_in_group) >= 2:
#             timestamps = [bkp for bkp, _ in group]
#             median_bkp = pd.Series(timestamps).median()
#             aggregated_breakpoints.append(median_bkp)
#             contrib_features_dict[median_bkp] = features_in_group
            
#     return aggregated_breakpoints, contrib_features_dict


