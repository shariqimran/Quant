import unittest

import pandas as pd

from src.quant_research.data.validation import (
    find_duplicate_timestamps,
    validate_dataframe,
)


class DataValidationTests(unittest.TestCase):
    def test_validate_dataframe_rejects_empty_dataframe(self):
        valid, message = validate_dataframe(pd.DataFrame(), ["timestamp", "close"])

        self.assertFalse(valid)
        self.assertEqual(message, "DataFrame is empty or None")

    def test_validate_dataframe_rejects_missing_columns(self):
        valid, message = validate_dataframe(
            pd.DataFrame({"timestamp": ["2024-01-01"]}),
            ["timestamp", "close"],
        )

        self.assertFalse(valid)
        self.assertEqual(message, "Missing required columns: ['close']")

    def test_validate_dataframe_accepts_required_columns(self):
        valid, message = validate_dataframe(
            pd.DataFrame({"timestamp": ["2024-01-01"], "close": [100.0]}),
            ["timestamp", "close"],
        )

        self.assertTrue(valid)
        self.assertEqual(message, "DataFrame is valid")

    def test_find_duplicate_timestamps_returns_repeated_values_only(self):
        timestamps = pd.to_datetime(
            ["2024-01-01", "2024-01-02", "2024-01-02"],
            utc=True,
        )
        df = pd.DataFrame({"timestamp": timestamps, "close": [100, 101, 102]})

        duplicates = find_duplicate_timestamps(df)

        self.assertEqual(duplicates, [timestamps[2]])


if __name__ == "__main__":
    unittest.main()
