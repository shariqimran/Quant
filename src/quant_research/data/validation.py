"""Data validation helpers."""


def validate_dataframe(df, required_columns):
    """Validate that a DataFrame is non-empty and contains required columns."""
    if df is None or df.empty:
        return False, "DataFrame is empty or None"

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {missing_columns}"

    return True, "DataFrame is valid"


def find_duplicate_timestamps(df, timestamp_column="timestamp"):
    """Return rows with duplicated timestamps, excluding the first occurrence."""
    if df is None or timestamp_column not in df.columns:
        return []

    duplicated = df[df[timestamp_column].duplicated(keep="first")]
    return duplicated[timestamp_column].tolist()
