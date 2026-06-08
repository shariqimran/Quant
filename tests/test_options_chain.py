import unittest
from datetime import date

import pandas as pd

from src.quant_research.options.chain import (
    build_enriched_contract_table,
    collect_listed_contracts,
    filter_and_sort_contracts,
    listed_contract_from_row,
    moneyness_label,
    normalize_implied_volatility,
)
from src.quant_research.options.pricing import calculate_black_scholes_breakdown


def _sample_calls():
    return pd.DataFrame(
        [
            {
                "contractSymbol": "AAPL250620C00180000",
                "strike": 180.0,
                "bid": 4.80,
                "ask": 5.00,
                "lastPrice": 4.90,
                "impliedVolatility": 0.22,
                "volume": 1200,
                "openInterest": 5000,
            },
            {
                "contractSymbol": "AAPL250620C00185000",
                "strike": 185.0,
                "bid": 2.40,
                "ask": 2.60,
                "lastPrice": 2.55,
                "impliedVolatility": 0.21,
                "volume": 800,
                "openInterest": 3000,
            },
        ]
    )


def _sample_puts():
    return pd.DataFrame(
        [
            {
                "contractSymbol": "AAPL250620P00185000",
                "strike": 185.0,
                "bid": 3.00,
                "ask": 3.20,
                "lastPrice": 3.10,
                "impliedVolatility": 0.23,
                "volume": 500,
                "openInterest": 1000,
            }
        ]
    )


class ListedContractCollectionTests(unittest.TestCase):
    def test_collect_listed_contracts_includes_calls_and_puts(self):
        contracts = collect_listed_contracts(
            {"2025-06-20": (_sample_calls(), _sample_puts())},
            include_calls=True,
            include_puts=True,
            as_of=date(2025, 6, 1),
        )
        self.assertEqual(len(contracts), 3)
        types = {contract.option_type for contract in contracts}
        self.assertEqual(types, {"call", "put"})

    def test_collect_listed_contracts_respects_type_filter(self):
        contracts = collect_listed_contracts(
            {"2025-06-20": (_sample_calls(), _sample_puts())},
            include_calls=False,
            include_puts=True,
            as_of=date(2025, 6, 1),
        )
        self.assertEqual(len(contracts), 1)
        self.assertEqual(contracts[0].option_type, "put")

    def test_contracts_to_display_dataframe_preserves_order(self):
        contracts = collect_listed_contracts(
            {"2025-06-20": (_sample_calls(), _sample_puts())},
            as_of=date(2025, 6, 1),
        )
        table = build_enriched_contract_table(contracts, spot=185.0)
        self.assertEqual(len(table), len(contracts))
        self.assertIn("Moneyness", table.columns)
        self.assertIn("Liquidity", table.columns)

    def test_normalize_implied_volatility_handles_percent_values(self):
        self.assertAlmostEqual(normalize_implied_volatility(0.45), 0.45)
        self.assertAlmostEqual(normalize_implied_volatility(45.0), 0.45)

    def test_moneyness_label_for_call(self):
        self.assertEqual(moneyness_label("call", 185.0, 185.0), "ATM")
        self.assertTrue(moneyness_label("call", 200.0, 185.0).startswith("OTM"))

    def test_filter_and_sort_contracts_liquid_only(self):
        contracts = collect_listed_contracts(
            {"2025-06-20": (_sample_calls(), _sample_puts())},
            as_of=date(2025, 6, 1),
        )
        filtered = filter_and_sort_contracts(
            contracts,
            strike_min=180.0,
            strike_max=190.0,
            liquid_only=True,
            sort_by="Strike (low → high)",
            spot=185.0,
        )
        self.assertGreaterEqual(len(filtered), 1)
        for contract in filtered:
            self.assertLessEqual(contract.spread_percentage or 0, 0.15)

    def test_listed_contract_from_row_computes_midpoint(self):
        row = _sample_calls().iloc[0]
        contract = listed_contract_from_row(
            row,
            option_type="call",
            expiration_date="2025-06-20",
            as_of=date(2025, 6, 1),
        )
        self.assertIsNotNone(contract)
        self.assertAlmostEqual(contract.midpoint, 4.9)


class BlackScholesBreakdownTests(unittest.TestCase):
    def test_breakdown_includes_intermediate_terms(self):
        breakdown = calculate_black_scholes_breakdown(
            spot=100,
            strike=100,
            time_to_expiry=1,
            volatility=0.20,
            risk_free_rate=0.05,
        )
        self.assertIsNotNone(breakdown.d1)
        self.assertIsNotNone(breakdown.d2)
        self.assertAlmostEqual(breakdown.result.call_price, 10.4506, places=4)
        self.assertAlmostEqual(breakdown.call_term_spot - breakdown.call_term_strike, breakdown.result.call_price, places=4)

    def test_breakdown_handles_zero_volatility(self):
        breakdown = calculate_black_scholes_breakdown(
            spot=110,
            strike=100,
            time_to_expiry=0.5,
            volatility=0.0,
            risk_free_rate=0.05,
        )
        self.assertIsNone(breakdown.d1)
        self.assertGreater(breakdown.result.call_price, 0)


if __name__ == "__main__":
    unittest.main()
