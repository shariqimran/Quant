import unittest

import pandas as pd

from src.quant_research.data.loaders import calculate_returns
from src.quant_research.metrics.performance import get_return_statistics


class MetricTests(unittest.TestCase):
    def test_get_return_statistics_returns_expected_keys(self):
        df = pd.DataFrame({"close": [100, 102, 101, 105, 107]})
        df = calculate_returns(df)

        stats = get_return_statistics(df, interval="1d")

        self.assertEqual(
            set(stats.keys()),
            {"mean_return", "volatility", "sharpe_ratio", "max_drawdown"},
        )
        self.assertLessEqual(stats["max_drawdown"], 0)


if __name__ == "__main__":
    unittest.main()

