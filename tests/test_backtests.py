import unittest

import pandas as pd

from src.quant_research.backtesting.engine import (
    run_moving_average_backtest,
    run_rsi_backtest,
)
from src.quant_research.backtesting.runners import moving_average_backtest, rsi_backtest


class BacktestBehaviorTests(unittest.TestCase):
    def test_moving_average_backtest_buys_on_golden_cross_and_sells_on_death_cross(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=5, freq="D", tz="UTC"),
                "close": [100.0, 110.0, 120.0, 130.0, 140.0],
                "ma_short": [1.0, 1.0, 3.0, 3.0, 1.0],
                "ma_long": [2.0, 2.0, 2.0, 2.0, 2.0],
            }
        )

        final_value, log_df, fig = moving_average_backtest(
            df,
            initial_capital=12000,
            symbol="TEST",
        )

        self.assertAlmostEqual(final_value, 14000.0)
        self.assertEqual(log_df["action"].tolist(), ["BUY", "SELL"])
        self.assertEqual(log_df["price"].tolist(), [120.0, 140.0])
        self.assertIsNotNone(fig)

    def test_pure_moving_average_engine_returns_dataframe_with_signal_columns(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=4, freq="D", tz="UTC"),
                "close": [100.0, 110.0, 120.0, 130.0],
                "ma_short": [1.0, 1.0, 3.0, 3.0],
                "ma_long": [2.0, 2.0, 2.0, 2.0],
            }
        )

        final_value, log_df, df_bt = run_moving_average_backtest(df, initial_capital=12000)

        self.assertAlmostEqual(final_value, 13000.0)
        self.assertEqual(log_df["action"].tolist(), ["BUY"])
        self.assertIn("ma_cross", df_bt.columns)
        self.assertIn("ma_cross_change", df_bt.columns)

    def test_rsi_backtest_buys_below_oversold_and_sells_above_overbought(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=4, freq="D", tz="UTC"),
                "close": [100.0, 90.0, 110.0, 120.0],
                "RSI": [None, 20.0, 50.0, 80.0],
            }
        )

        final_value, log_df, fig = rsi_backtest(
            df,
            initial_capital=9000,
            symbol="TEST",
            oversold_threshold=30,
            overbought_threshold=70,
        )

        self.assertAlmostEqual(final_value, 12000.0)
        self.assertEqual(log_df["action"].tolist(), ["BUY", "SELL"])
        self.assertEqual(log_df["price"].tolist(), [90.0, 120.0])
        self.assertIsNotNone(fig)

    def test_pure_rsi_engine_skips_nan_rsi_values(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC"),
                "close": [100.0, 90.0, 110.0],
                "RSI": [None, None, 80.0],
            }
        )

        final_value, log_df, _df_bt = run_rsi_backtest(df, initial_capital=9000)

        self.assertEqual(final_value, 9000)
        self.assertTrue(log_df.empty)


if __name__ == "__main__":
    unittest.main()
