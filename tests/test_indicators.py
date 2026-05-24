import unittest

import pandas as pd

from src.quant_research.indicators.momentum import calculate_rsi
from src.quant_research.indicators.trend import calculate_moving_averages
from src.quant_research.indicators.volatility import calculate_volatility


class IndicatorTests(unittest.TestCase):
    def test_moving_averages_add_expected_columns(self):
        df = pd.DataFrame({"close": [1, 2, 3, 4, 5]})

        result = calculate_moving_averages(df, short_window=2, long_window=3)

        self.assertIn("ma_short", result.columns)
        self.assertIn("ma_long", result.columns)
        self.assertEqual(result["ma_short"].iloc[-1], 4.5)
        self.assertEqual(result["ma_long"].iloc[-1], 4.0)

    def test_rsi_adds_rsi_column(self):
        df = pd.DataFrame({"close": [1, 2, 3, 2, 4, 5, 4, 6, 7, 8]})

        result = calculate_rsi(df, period=3)

        self.assertIn("RSI", result.columns)
        self.assertEqual(len(result), len(df))

    def test_volatility_adds_window_column(self):
        df = pd.DataFrame({"close": [100, 101, 103, 102, 105, 106]})

        result = calculate_volatility(df, window=2, return_type="log", interval="1d")

        self.assertIn("return_log", result.columns)
        self.assertIn("volatility_2", result.columns)


if __name__ == "__main__":
    unittest.main()

