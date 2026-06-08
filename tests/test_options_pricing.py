import unittest

from src.quant_research.options.pricing import (
    calculate_binomial_option,
    calculate_black_scholes,
    calculate_monte_carlo_option,
    implied_volatility_from_binomial_price,
    years_from_days,
)


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


class BinomialPricingTests(unittest.TestCase):
    def test_european_crr_converges_to_black_scholes(self):
        bs = calculate_black_scholes(
            spot=100,
            strike=100,
            time_to_expiry=1,
            volatility=0.20,
            risk_free_rate=0.05,
            dividend_yield=0,
        )
        crr = calculate_binomial_option(
            spot=100,
            strike=100,
            time_to_expiry=1,
            volatility=0.20,
            risk_free_rate=0.05,
            dividend_yield=0,
            steps=500,
            option_type="call",
            exercise_style="european",
        )

        self.assertAlmostEqual(crr.price, bs.call_price, places=2)
        self.assertGreater(crr.up_factor, 1)
        self.assertLess(crr.down_factor, 1)
        self.assertGreaterEqual(crr.risk_neutral_probability, 0)
        self.assertLessEqual(crr.risk_neutral_probability, 1)

    def test_american_put_is_worth_at_least_european_put(self):
        european = calculate_binomial_option(
            spot=50,
            strike=55,
            time_to_expiry=0.5,
            volatility=0.30,
            risk_free_rate=0.05,
            dividend_yield=0,
            steps=250,
            option_type="put",
            exercise_style="european",
        )
        american = calculate_binomial_option(
            spot=50,
            strike=55,
            time_to_expiry=0.5,
            volatility=0.30,
            risk_free_rate=0.05,
            dividend_yield=0,
            steps=250,
            option_type="put",
            exercise_style="american",
        )

        self.assertGreaterEqual(american.price, european.price)
        self.assertAlmostEqual(american.early_exercise_premium, american.price - european.price)

    def test_invalid_crr_probability_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_binomial_option(
                spot=100,
                strike=100,
                time_to_expiry=1,
                volatility=0.01,
                risk_free_rate=0,
                dividend_yield=0.50,
                steps=1,
                option_type="call",
                exercise_style="american",
            )

    def test_implied_volatility_solver_recovers_input_volatility(self):
        model = calculate_binomial_option(
            spot=100,
            strike=105,
            time_to_expiry=30 / 365,
            volatility=0.25,
            risk_free_rate=0.05,
            dividend_yield=0,
            steps=250,
            option_type="call",
            exercise_style="european",
        )

        implied_volatility = implied_volatility_from_binomial_price(
            target_price=model.price,
            spot=100,
            strike=105,
            time_to_expiry=30 / 365,
            risk_free_rate=0.05,
            dividend_yield=0,
            steps=250,
            option_type="call",
            exercise_style="european",
        )

        self.assertIsNotNone(implied_volatility)
        self.assertAlmostEqual(implied_volatility, 0.25, places=3)

    def test_monte_carlo_european_price_is_close_to_black_scholes(self):
        bs = calculate_black_scholes(
            spot=100,
            strike=100,
            time_to_expiry=1,
            volatility=0.20,
            risk_free_rate=0.05,
            dividend_yield=0,
        )
        simulation = calculate_monte_carlo_option(
            spot=100,
            strike=100,
            time_to_expiry=1,
            volatility=0.20,
            risk_free_rate=0.05,
            dividend_yield=0,
            paths=100000,
            option_type="call",
            seed=7,
        )

        self.assertLess(abs(simulation.price - bs.call_price), 3 * simulation.standard_error)


if __name__ == "__main__":
    unittest.main()
