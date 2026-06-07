"""Black-Scholes calculator page."""

from datetime import date, datetime
from math import isfinite

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

from src.quant_research.options import calculate_black_scholes, years_from_days


DEFAULT_RATE = 0.045
DEFAULT_VOLATILITY = 0.25


def _safe_float(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(number):
        return None
    return number


def _format_money(value, currency="USD"):
    value = _safe_float(value)
    if value is None:
        return "-"
    if currency == "USD":
        return f"${value:,.2f}"
    return f"{currency} {value:,.2f}"


def _format_number(value, decimals=4):
    value = _safe_float(value)
    if value is None:
        return "-"
    return f"{value:,.{decimals}f}"


def _format_percent(value):
    value = _safe_float(value)
    if value is None:
        return "-"
    return f"{value * 100:,.2f}%"


def _get_fast_info_value(fast_info, *names):
    for name in names:
        try:
            value = fast_info.get(name)
        except AttributeError:
            value = getattr(fast_info, name, None)
        if _safe_float(value) is not None or isinstance(value, str):
            return value
    return None


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_live_quote(symbol):
    """Fetch a short-lived quote snapshot from Yahoo Finance."""
    ticker = yf.Ticker(symbol)
    fast_info = {}
    try:
        fast_info = ticker.fast_info
    except Exception:
        fast_info = {}

    quote = {
        "price": _get_fast_info_value(fast_info, "last_price", "lastPrice"),
        "previous_close": _get_fast_info_value(
            fast_info,
            "previous_close",
            "previousClose",
            "regular_market_previous_close",
            "regularMarketPreviousClose",
        ),
        "day_high": _get_fast_info_value(fast_info, "day_high", "dayHigh"),
        "day_low": _get_fast_info_value(fast_info, "day_low", "dayLow"),
        "currency": _get_fast_info_value(fast_info, "currency") or "USD",
        "quote_time": None,
        "source": "Yahoo Finance fast_info",
    }

    if _safe_float(quote["price"]) is None:
        history = ticker.history(period="1d", interval="1m")
        clean_history = history.dropna(subset=["Close"]) if not history.empty else history
        if not clean_history.empty:
            latest = clean_history.iloc[-1]
            quote["price"] = latest["Close"]
            quote["day_high"] = history["High"].max()
            quote["day_low"] = history["Low"].min()
            quote["quote_time"] = str(clean_history.index[-1])
            quote["source"] = "Yahoo Finance 1m history"

    return quote


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_expirations(symbol):
    """Fetch available option expirations."""
    return list(yf.Ticker(symbol).options)


@st.cache_data(ttl=120, show_spinner=False)
def _fetch_option_chain(symbol, expiration):
    """Fetch a Yahoo option chain for one expiration."""
    chain = yf.Ticker(symbol).option_chain(expiration)
    return chain.calls.copy(), chain.puts.copy()


def _days_to_expiration(expiration):
    expiry_date = datetime.strptime(expiration, "%Y-%m-%d").date()
    return max((expiry_date - date.today()).days, 0)


def _nearest_index(values, target):
    if not values:
        return 0
    target = _safe_float(target) or values[0]
    distances = [abs(value - target) for value in values]
    return distances.index(min(distances))


def _selected_contract_row(chain_df, strike):
    if chain_df is None or chain_df.empty or "strike" not in chain_df.columns:
        return None
    distances = (chain_df["strike"] - strike).abs()
    return chain_df.loc[distances.idxmin()]


def _market_mid(row):
    if row is None:
        return None
    bid = _safe_float(row.get("bid"))
    ask = _safe_float(row.get("ask"))
    last = _safe_float(row.get("lastPrice"))
    if bid is not None and ask is not None and bid > 0 and ask > 0:
        return (bid + ask) / 2
    return last


def _render_quote_strip(quote, symbol):
    currency = quote.get("currency") or "USD"
    price = _safe_float(quote.get("price"))
    previous = _safe_float(quote.get("previous_close"))
    change = None
    if price is not None and previous not in (None, 0):
        change = (price - previous) / previous

    cols = st.columns(4)
    cols[0].metric("Underlying", symbol)
    cols[1].metric("Last price", _format_money(price, currency))
    cols[2].metric("Prev close", _format_money(previous, currency))
    cols[3].metric("Day range", f"{_format_money(quote.get('day_low'), currency)} / {_format_money(quote.get('day_high'), currency)}")

    caption = f"Source: {quote.get('source', 'Yahoo Finance')}. Cache TTL: 30 seconds."
    if quote.get("quote_time"):
        caption += f" Last bar: {quote['quote_time']}."
    if change is not None:
        caption += f" Move vs prev close: {change * 100:.2f}%."
    st.caption(caption)


def _render_contract_snapshot(row, currency):
    if row is None:
        st.info("No matching option-chain quote is available for this contract.")
        return

    cols = st.columns(6)
    cols[0].metric("Bid", _format_money(row.get("bid"), currency))
    cols[1].metric("Ask", _format_money(row.get("ask"), currency))
    cols[2].metric("Last", _format_money(row.get("lastPrice"), currency))
    cols[3].metric("Mid", _format_money(_market_mid(row), currency))
    cols[4].metric("IV", _format_percent(row.get("impliedVolatility")))
    cols[5].metric("Open interest", _format_number(row.get("openInterest"), 0))


def _build_payoff_chart(spot, strike, premium, option_side):
    low = max(0.01, spot * 0.55)
    high = max(strike * 1.35, spot * 1.45, low + 1)
    prices = [low + (high - low) * index / 100 for index in range(101)]

    if option_side == "Call":
        long_pnl = [max(price - strike, 0) - premium for price in prices]
    else:
        long_pnl = [max(strike - price, 0) - premium for price in prices]
    short_pnl = [-value for value in long_pnl]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prices, y=long_pnl, name=f"Long {option_side}", line={"color": "#2fffb2", "width": 3}))
    fig.add_trace(go.Scatter(x=prices, y=short_pnl, name=f"Short {option_side}", line={"color": "#ff6f91", "width": 2}))
    fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
    fig.add_vline(x=strike, line_dash="dash", line_color="#fbbf24", annotation_text="Strike")
    fig.add_vline(x=spot, line_dash="dot", line_color="#51d7ff", annotation_text="Spot")
    fig.update_layout(
        height=420,
        margin={"l": 8, "r": 8, "t": 20, "b": 8},
        xaxis_title="Underlying price at expiration",
        yaxis_title="P&L",
        template="plotly_dark",
        legend={"orientation": "h", "y": 1.08},
    )
    return fig


def _render_model_outputs(result, currency, selected_side, market_mid):
    call_edge = result.call_price - market_mid if selected_side == "Call" and market_mid is not None else None
    put_edge = result.put_price - market_mid if selected_side == "Put" and market_mid is not None else None

    st.markdown("#### Theoretical Value")
    cols = st.columns(4)
    cols[0].metric("Call option", _format_money(result.call_price, currency))
    cols[1].metric("Put option", _format_money(result.put_price, currency))
    cols[2].metric("Selected mid", _format_money(market_mid, currency))
    cols[3].metric("Model - mid", _format_money(call_edge if selected_side == "Call" else put_edge, currency))

    value_rows = pd.DataFrame(
        [
            {
                "Option": "Call",
                "Theoretical": result.call_price,
                "Intrinsic": result.call_intrinsic,
                "Time Value": result.call_time_value,
            },
            {
                "Option": "Put",
                "Theoretical": result.put_price,
                "Intrinsic": result.put_intrinsic,
                "Time Value": result.put_time_value,
            },
        ]
    )
    st.dataframe(
        value_rows,
        width="stretch",
        hide_index=True,
        column_config={
            "Theoretical": st.column_config.NumberColumn(format="$%.4f"),
            "Intrinsic": st.column_config.NumberColumn(format="$%.4f"),
            "Time Value": st.column_config.NumberColumn(format="$%.4f"),
        },
    )

    st.markdown("#### Option Greeks")
    greeks = pd.DataFrame(
        [
            {"Greek": "Delta", "Call": result.call_delta, "Put": result.put_delta},
            {"Greek": "Gamma", "Call": result.gamma, "Put": result.gamma},
            {"Greek": "Vega", "Call": result.vega, "Put": result.vega},
            {"Greek": "Theta / day", "Call": result.call_theta, "Put": result.put_theta},
            {"Greek": "Rho", "Call": result.call_rho, "Put": result.put_rho},
        ]
    )
    st.dataframe(
        greeks,
        width="stretch",
        hide_index=True,
        column_config={
            "Call": st.column_config.NumberColumn(format="%.6f"),
            "Put": st.column_config.NumberColumn(format="%.6f"),
        },
    )


def render_black_scholes_page(inputs):
    """Render the Black-Scholes calculator page."""
    st.subheader("Black-Scholes Calculator")
    st.caption(
        "European option pricing with editable assumptions and Yahoo Finance quote/chain data. "
        "Market data can be delayed and is intended for research, not trade execution."
    )

    top_left, top_right = st.columns([3, 1])
    with top_left:
        symbol = st.text_input(
            "Ticker",
            value=inputs.get("symbol", "AAPL"),
            help="Use Yahoo Finance symbols, for example AAPL, SPY, MSFT.",
        ).strip().upper()
    with top_right:
        st.write("")
        st.write("")
        if st.button("Refresh market data", width="stretch"):
            _fetch_live_quote.clear()
            _fetch_expirations.clear()
            _fetch_option_chain.clear()
            st.rerun()

    if not symbol:
        st.error("Enter a ticker symbol.")
        return

    try:
        quote = _fetch_live_quote(symbol)
        expirations = _fetch_expirations(symbol)
    except Exception as exc:
        st.error(f"Unable to load Yahoo Finance data for {symbol}: {exc}")
        quote = {"price": None, "currency": "USD"}
        expirations = []

    _render_quote_strip(quote, symbol)

    currency = quote.get("currency") or "USD"
    spot_from_quote = _safe_float(quote.get("price"))
    use_live_spot = st.checkbox("Use latest underlying price", value=spot_from_quote is not None)

    left, right = st.columns([0.92, 1.08], gap="large")

    with left:
        st.markdown("#### Contract")
        option_side = st.radio("Selected side", ["Call", "Put"], horizontal=True)

        calls = pd.DataFrame()
        puts = pd.DataFrame()
        selected_row = None
        selected_expiration = None
        selected_iv = None

        if expirations:
            selected_expiration = st.selectbox("Expiration", expirations)
            try:
                calls, puts = _fetch_option_chain(symbol, selected_expiration)
            except Exception as exc:
                st.warning(f"Unable to load option chain for {selected_expiration}: {exc}")

        chain_df = calls if option_side == "Call" else puts
        chain_strikes = []
        if not chain_df.empty and "strike" in chain_df.columns:
            chain_strikes = [_safe_float(value) for value in chain_df["strike"].dropna().unique()]
            chain_strikes = sorted(value for value in chain_strikes if value is not None)

        if chain_strikes:
            default_strike_index = _nearest_index(chain_strikes, spot_from_quote)
            selected_strike = st.selectbox(
                "Strike from option chain",
                chain_strikes,
                index=default_strike_index,
                format_func=lambda value: f"{value:,.2f}",
            )
            selected_row = _selected_contract_row(chain_df, selected_strike)
            strike = st.number_input("Strike price", min_value=0.01, value=float(selected_strike), step=1.0)
        else:
            selected_strike = spot_from_quote or 100.0
            strike = st.number_input("Strike price", min_value=0.01, value=float(selected_strike), step=1.0)

        if selected_expiration:
            days_default = _days_to_expiration(selected_expiration)
        else:
            days_default = 30
        days_to_expiry = st.number_input("Days until expiration", min_value=0, value=int(days_default), step=1)

        if selected_row is not None:
            selected_iv = _safe_float(selected_row.get("impliedVolatility"))
            _render_contract_snapshot(selected_row, currency)
        elif expirations:
            st.info("No usable strikes were returned for this option chain.")
        else:
            st.info("No listed option expirations were returned. Use manual assumptions below.")

    with right:
        st.markdown("#### Pricing Assumptions")
        if use_live_spot and spot_from_quote is not None:
            spot = spot_from_quote
            st.metric("Underlying price input", _format_money(spot, currency))
        else:
            spot = st.number_input(
                "Underlying price",
                min_value=0.01,
                value=float(spot_from_quote or 100.0),
                step=1.0,
            )

        vol_default = selected_iv if selected_iv and selected_iv > 0 else DEFAULT_VOLATILITY
        volatility_pct = st.number_input(
            "Volatility",
            min_value=0.0,
            value=float(vol_default * 100),
            step=1.0,
            help="Annualized volatility. Option-chain IV is used as the default when available.",
        )
        rate_pct = st.number_input("Risk-free rate", value=float(DEFAULT_RATE * 100), step=0.25)
        dividend_pct = st.number_input("Dividend yield", value=0.0, step=0.25)
        basis = st.radio("Day count basis", ["Calendar days (365)", "Trading days (252)"], horizontal=True)
        basis_value = 252 if "252" in basis else 365

        time_to_expiry = years_from_days(days_to_expiry, basis=basis_value)
        result = calculate_black_scholes(
            spot=spot,
            strike=strike,
            time_to_expiry=time_to_expiry,
            volatility=volatility_pct / 100,
            risk_free_rate=rate_pct / 100,
            dividend_yield=dividend_pct / 100,
        )

        st.caption(
            f"Inputs: T={time_to_expiry:.4f} years, vol={volatility_pct:.2f}%, "
            f"rate={rate_pct:.2f}%, dividend={dividend_pct:.2f}%."
        )

    market_mid = _market_mid(selected_row)
    calculator_tab, payoff_tab = st.tabs(["Calculator", "Payoff & P&L"])
    with calculator_tab:
        _render_model_outputs(result, currency, option_side, market_mid)

    with payoff_tab:
        premium = result.call_price if option_side == "Call" else result.put_price
        st.plotly_chart(_build_payoff_chart(spot, strike, premium, option_side), width="stretch")
        if option_side == "Call":
            breakeven = strike + premium
        else:
            breakeven = strike - premium
        st.caption(
            f"Payoff uses the model premium for a {option_side.lower()} contract. "
            f"Breakeven at expiration: {_format_money(breakeven, currency)}."
        )
