from datetime import timedelta
import json

def lookup_from_db_load(df, product_code, target_time, is_pente, tolerance_minutes=1):
    time_window = timedelta(minutes=tolerance_minutes)
    mask = (
        (df["ProductCode"] == product_code) &
        (df["Timestamp"] >= target_time - time_window) &
        (df["Timestamp"] <= target_time + time_window)
    )
    subset = df[mask].copy()
    if subset.empty:
        return (None, None, None, None, None, None)

    # Find the closest by absolute time difference
    subset["time_diff"] = subset["Timestamp"].apply(lambda x: abs((x - target_time).total_seconds()))
    best_row = subset.loc[subset["time_diff"].idxmin()]

    # Process thickness samples
    try:
        samples = json.loads(best_row["ThicknessSamples"])
        if len(samples) >= 4:
            thickness_T3_DB = samples[3] if not is_pente else (samples[0]+samples[1])/2
            thickness_T1_DB = samples[-4] if not is_pente else (samples[-1]+samples[-2])/2
    except Exception:
        thickness_T1_DB = None
        thickness_T3_DB = None

    # Format timestamp as 'YYYY-MM-DD HH:MM:SS'
    timestamp_str = best_row["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    return (
        timestamp_str,
        best_row["InsulatorDensity"],
        thickness_T1_DB,
        thickness_T3_DB,
        best_row["TotalThickness"],
        best_row["ProductCode"]
    )