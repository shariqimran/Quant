import unittest

from streamlit.testing.v1 import AppTest


def render_mocked_binomial_page():
    """Render the Binomial page with deterministic market data."""
    from datetime import date, timedelta
    from unittest.mock import patch

    import pandas as pd

    from src.quant_research.apps.streamlit.pages.binomial import render_binomial_page

    expiration = (date.today() + timedelta(days=45)).strftime("%Y-%m-%d")
    calls = pd.DataFrame(
        [
            {
                "strike": 100.0,
                "bid": 4.0,
                "ask": 4.4,
                "lastPrice": 4.2,
                "impliedVolatility": 0.25,
                "openInterest": 100,
            }
        ]
    )
    puts = pd.DataFrame(
        [
            {
                "strike": 100.0,
                "bid": 3.0,
                "ask": 3.4,
                "lastPrice": 3.2,
                "impliedVolatility": 0.25,
                "openInterest": 80,
            }
        ]
    )
    quote = {
        "price": 100.0,
        "previous_close": 99.0,
        "day_high": 101.0,
        "day_low": 98.0,
        "currency": "USD",
        "source": "test quote",
    }
    with (
        patch(
            "src.quant_research.apps.streamlit.pages.binomial.fetch_live_quote",
            return_value=quote,
        ),
        patch(
            "src.quant_research.apps.streamlit.pages.binomial.fetch_expirations",
            return_value=[expiration],
        ),
        patch(
            "src.quant_research.apps.streamlit.pages.binomial.fetch_option_chain_cached",
            return_value=(calls, puts),
        ),
    ):
        render_binomial_page({"symbol": "AAPL"})


class BinomialPageSmokeTests(unittest.TestCase):
    def test_binomial_page_renders_without_exceptions_or_raw_html_cards(self):
        app = AppTest.from_function(render_mocked_binomial_page, default_timeout=15)
        app.run()

        self.assertEqual(app.exception, [])
        rendered_text = "\n".join(
            str(item.value) for item in [*app.markdown, *app.caption, *app.subheader]
        )
        self.assertIn("Binomial Option Pricing Model", rendered_text)
        self.assertIn("CRR tree output", rendered_text)
        self.assertNotIn("<article", rendered_text)
        self.assertNotIn("</article>", rendered_text)
        self.assertNotIn("binomial-card", rendered_text)


if __name__ == "__main__":
    unittest.main()
