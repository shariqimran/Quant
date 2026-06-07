import unittest

from src.quant_research.options.pricing import calculate_black_scholes, years_from_days


class BlackScholesPricingTests(unittest.TestCase):
    def test_calculate_black_scholes_matches_reference_values(self):
        result = calculate_black_scholes(
            spot=100,
            strike=100,
            time_to_expiry=1,
            volatility=0.20,
            risk_free_rate=0.05,
            dividend_yield=0,
        )

        self.assertAlmostEqual(result.call_price, 10.4506, places=4)
        self.assertAlmostEqual(result.put_price, 5.5735, places=4)
        self.assertAlmostEqual(result.call_delta, 0.6368, places=4)
        self.assertAlmostEqual(result.put_delta, -0.3632, places=4)
        self.assertAlmostEqual(result.gamma, 0.0188, places=4)
        self.assertAlmostEqual(result.vega, 0.3752, places=4)
        self.assertAlmostEqual(result.call_theta, -0.0176, places=4)
        self.assertAlmostEqual(result.put_theta, -0.0045, places=4)
        self.assertAlmostEqual(result.call_rho, 0.5323, places=4)
        self.assertAlmostEqual(result.put_rho, -0.4189, places=4)

    def test_calculate_black_scholes_handles_expiry_intrinsic_value(self):
        result = calculate_black_scholes(
            spot=125,
            strike=100,
            time_to_expiry=0,
            volatility=0.20,
            risk_free_rate=0.05,
        )

        self.assertEqual(result.call_price, 25)
        self.assertEqual(result.put_price, 0)
        self.assertEqual(result.call_intrinsic, 25)
        self.assertEqual(result.put_intrinsic, 0)
        self.assertIsNone(result.d1)
        self.assertIsNone(result.d2)

    def test_years_from_days_uses_selected_basis(self):
        self.assertAlmostEqual(years_from_days(30), 30 / 365)
        self.assertAlmostEqual(years_from_days(30, basis=252), 30 / 252)


if __name__ == "__main__":
    unittest.main()
