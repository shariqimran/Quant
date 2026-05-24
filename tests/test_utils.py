import unittest

import pandas as pd

from src.quant_research.utils.dates import filter_df_utc_date_range


class DateHelperTests(unittest.TestCase):
    def test_filter_df_utc_date_range_filters_inclusive_dates(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    ["2024-01-01", "2024-01-02", "2024-01-03"],
                    utc=True,
                ),
                "close": [100, 101, 102],
            }
        )

        result = filter_df_utc_date_range(df, "2024-01-02", "2024-01-03")

        self.assertEqual(len(result), 2)
        self.assertEqual(result["close"].tolist(), [101, 102])


if __name__ == "__main__":
    unittest.main()

