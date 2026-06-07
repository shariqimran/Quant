"""Date and timestamp helpers."""

import pandas as pd


def filter_df_utc_date_range(df, start, end):
    """Filter rows to [start, end] inclusive using UTC-aware timestamps."""
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)
    if start_dt.tzinfo is None:
        start_dt = start_dt.tz_localize("UTC")
    else:
        start_dt = start_dt.tz_convert("UTC")
    if end_dt.tzinfo is None:
        end_dt = end_dt.tz_localize("UTC")
    else:
        end_dt = end_dt.tz_convert("UTC")
    mask = (out["timestamp"] >= start_dt) & (out["timestamp"] <= end_dt)
    return out.loc[mask].reset_index(drop=True)

