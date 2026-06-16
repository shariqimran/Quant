"""Black-Scholes calculator page — contract table first, then row-driven pricing."""

from datetime import date, datetime
from math import isfinite

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.quant_research.apps.streamlit.components.cards import render_kpi_card
from src.quant_research.apps.streamlit.services.options_data import (
    clear_options_cache,
    fetch_expirations,
    fetch_live_quote,
    fetch_option_chain_cached,
    fetch_realized_volatility_profile,
)
from src.quant_research.indicators.realized_volatility import RealizedVolatilitySnapshot
from src.quant_research.options import calculate_black_scholes_breakdown, years_from_days
from src.quant_research.options.chain import (
    ListedOptionContract,
    build_enriched_contract_table,
    collect_listed_contracts,
    contract_midpoint,
    filter_and_sort_contracts,
    normalize_implied_volatility,
    summarize_contract_chain,
)


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
        return f"${value:,.4f}"
    return f"{currency} {value:,.4f}"


def _format_number(value, decimals=2):
    value = _safe_float(value)
    if value is None:
        return "-"
    return f"{value:,.{decimals}f}"


def _format_percent(value, decimals=2):
    value = _safe_float(value)
    if value is None:
        return "-"
    return f"{value * 100:,.{decimals}f}%"


def _fetch_live_quote(symbol):
    return fetch_live_quote(symbol)


def _fetch_expirations(symbol):
    return fetch_expirations(symbol)


def _fetch_option_chain(symbol, expiration):
    return fetch_option_chain_cached(symbol, expiration)


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

    cols = st.columns(4)
    cols[0].metric("Underlying", symbol)
    cols[1].metric("Last price", _format_money(price, currency))
    cols[2].metric("Prev close", _format_money(previous, currency))
    cols[3].metric(
        "Day range",
        f"{_format_money(quote.get('day_low'), currency)} / {_format_money(quote.get('day_high'), currency)}",
    )
    st.caption(
        f"Source: {quote.get('source', 'Yahoo Finance')}. Quotes may be delayed — not for trade execution."
    )
    return currency, price


def _load_contracts(symbol, expiration, include_calls, include_puts):
    calls, puts = fetch_option_chain_cached(symbol, expiration)
    return collect_listed_contracts(
        {expiration: (calls, puts)},
        include_calls=include_calls,
        include_puts=include_puts,
    )


def _render_strike_chain_chart(contracts: list[ListedOptionContract], spot: float | None, symbol: str):
    """Mini chart: midpoint by strike, split by call/put."""
    if not contracts:
        return

    calls = [contract for contract in contracts if contract.option_type == "call" and contract.midpoint is not None]
    puts = [contract for contract in contracts if contract.option_type == "put" and contract.midpoint is not None]
    if not calls and not puts:
        return

    fig = go.Figure()
    if calls:
        fig.add_trace(
            go.Scatter(
                x=[contract.strike for contract in calls],
                y=[contract.midpoint for contract in calls],
                mode="markers+lines",
                name="Calls",
                line={"color": "rgba(47, 255, 178, 0.35)", "width": 1.5},
                marker={"color": "#2fffb2", "size": 7, "line": {"width": 1, "color": "#14532d"}},
                hovertemplate="Call K=%{x:.2f}<br>Mid=$%{y:.2f}<extra></extra>",
            )
        )
    if puts:
        fig.add_trace(
            go.Scatter(
                x=[contract.strike for contract in puts],
                y=[contract.midpoint for contract in puts],
                mode="markers+lines",
                name="Puts",
                line={"color": "rgba(255, 111, 145, 0.35)", "width": 1.5},
                marker={"color": "#ff6f91", "size": 7, "line": {"width": 1, "color": "#7f1d1d"}},
                hovertemplate="Put K=%{x:.2f}<br>Mid=$%{y:.2f}<extra></extra>",
            )
        )
    if spot is not None and spot > 0:
        fig.add_vline(
            x=spot,
            line_dash="dot",
            line_color="#51d7ff",
            annotation_text=f"Spot {spot:.2f}",
            annotation_position="top left",
        )

    fig.update_layout(
        title=f"{symbol} option midpoints by strike",
        height=260,
        margin={"l": 8, "r": 8, "t": 42, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={"orientation": "h", "y": 1.12},
        xaxis={"title": "Strike", "gridcolor": "rgba(148,163,184,0.12)"},
        yaxis={"title": "Midpoint ($)", "gridcolor": "rgba(148,163,184,0.12)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_contract_table(
    contracts: list[ListedOptionContract],
    *,
    spot: float | None,
    symbol: str,
    expiration: str,
    dte: int,
):
    if not contracts:
        st.warning("No contracts returned for this expiration and filter.")
        return None

    summary = summarize_contract_chain(contracts, spot)
    strikes = [contract.strike for contract in contracts]
    strike_min_default = float(min(strikes))
    strike_max_default = float(max(strikes))

    st.markdown(
        """
        <div class="options-chain-panel">
            <div class="options-chain-header">
                <div>
                    <h3>Option chain explorer</h3>
                    <p>
                        Each row is a live quote from Yahoo Finance. Pick a strike to load it into the
                        Black-Scholes calculator — compare the model price to the <strong>midpoint</strong>,
                        not last trade.
                    </p>
                </div>
                <span class="status-pill">Delayed market data</span>
            </div>
            <div class="options-chain-hint">
                Tip: start near <strong>ATM</strong> strikes with <strong>Tight spread</strong> or
                <strong>Tradeable</strong> liquidity for cleaner model comparisons.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        render_kpi_card("Contracts", str(summary["count"]), f"Exp {expiration}")
    with kpi2:
        render_kpi_card("Quoted", str(summary["quoted"]), "Valid bid / ask")
    with kpi3:
        spread_note = (
            f"{summary['median_spread_pct'] * 100:.1f}% median"
            if summary["median_spread_pct"] is not None
            else "—"
        )
        render_kpi_card("Liquid", str(summary["liquid"]), spread_note)
    with kpi4:
        atm_note = f"${summary['atm_strike']:,.2f}" if summary["atm_strike"] is not None else "—"
        render_kpi_card("Near spot", atm_note, f"{dte} DTE")

    _render_strike_chain_chart(contracts, spot, symbol)

    filter1, filter2, filter3 = st.columns([1.4, 0.8, 1])
    with filter1:
        strike_range = st.slider(
            "Strike range",
            min_value=strike_min_default,
            max_value=strike_max_default,
            value=(strike_min_default, strike_max_default),
            format="$%.0f",
            key="bs_strike_range",
        )
    with filter2:
        liquid_only = st.checkbox("Liquid only", value=False, help="Hide spreads wider than 15%.")
    with filter3:
        sort_by = st.selectbox(
            "Sort by",
            [
                "Nearest to spot",
                "Strike (low → high)",
                "Strike (high → low)",
                "Tightest spread",
                "Highest volume",
                "Highest open interest",
            ],
            key="bs_sort_by",
        )

    visible_contracts = filter_and_sort_contracts(
        contracts,
        strike_min=strike_range[0],
        strike_max=strike_range[1],
        liquid_only=liquid_only,
        sort_by=sort_by,
        spot=spot,
    )

    if not visible_contracts:
        st.warning("No contracts match the current filters.")
        return None

    table_df = build_enriched_contract_table(visible_contracts, spot=spot)
    st.caption(f"Showing **{len(visible_contracts)}** of **{len(contracts)}** contracts · click one row to select")

    selection = st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="bs_contract_table",
        height=min(560, 48 + len(table_df) * 36),
        column_config={
            "Strike": st.column_config.NumberColumn(
                "Strike",
                format="$%.2f",
                help="Exercise price for this contract.",
            ),
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Moneyness": st.column_config.TextColumn(
                "Moneyness",
                help="ITM / ATM / OTM relative to the current underlying price.",
                width="medium",
            ),
            "Bid": st.column_config.NumberColumn(format="$%.2f"),
            "Ask": st.column_config.NumberColumn(format="$%.2f"),
            "Mid": st.column_config.NumberColumn(
                "Mid",
                format="$%.2f",
                help="Bid-ask midpoint — primary market reference for model comparison.",
            ),
            "IV %": st.column_config.NumberColumn(
                "IV %",
                format="%.1f",
                help="Implied volatility from the chain (annualized %).",
            ),
            "Spread %": st.column_config.ProgressColumn(
                "Spread %",
                format="%.1f%%",
                min_value=0,
                max_value=100,
                help="Bid-ask spread as % of midpoint. Lower is better.",
            ),
            "Volume": st.column_config.NumberColumn(format="%d"),
            "Open Int.": st.column_config.NumberColumn(format="%d"),
            "Liquidity": st.column_config.TextColumn(
                "Liquidity",
                width="medium",
                help="Quick read on quote quality and activity.",
            ),
            "Contract": st.column_config.TextColumn(
                "Contract",
                width="large",
                help="OCC-style symbol from Yahoo Finance.",
            ),
        },
    )

    if not selection.selection.rows:
        return None
    return visible_contracts[selection.selection.rows[0]]


def _render_selected_contract_summary(contract: ListedOptionContract, currency: str):
    st.markdown("#### Selected contract")
    cols = st.columns(6)
    cols[0].metric("Symbol", contract.contract_symbol)
    cols[1].metric("Type", contract.option_type.upper())
    cols[2].metric("Strike", _format_money(contract.strike, currency))
    cols[3].metric("Expiration", contract.expiration_date)
    cols[4].metric("DTE", contract.days_to_expiration)
    cols[5].metric("Chain IV", _format_percent(contract.implied_volatility))

    cols = st.columns(5)
    cols[0].metric("Bid", _format_money(contract.bid, currency))
    cols[1].metric("Ask", _format_money(contract.ask, currency))
    cols[2].metric("Midpoint", _format_money(contract.midpoint, currency))
    cols[3].metric("Last", _format_money(contract.last_price, currency))
    cols[4].metric("Open interest", contract.open_interest or 0)


def _n(value, decimals=6):
    """Format a numeric value for LaTeX."""
    if value is None:
        return r"\text{---}"
    return f"{value:.{decimals}f}"


def _render_pricing_math(
    breakdown,
    *,
    days_to_expiry: int,
    basis_value: int,
) -> None:
    """Render the Black-Scholes pricing walkthrough as LaTeX formulas."""
    b = breakdown

    st.markdown("#### Step-by-step calculation")
    st.caption(
        "Symbolic Black-Scholes formulas with your inputs substituted. "
        "σ, r, and q are annualized; T is converted from days to years."
    )

    st.latex(
        r"C = S e^{-qT} N(d_1) - K e^{-rT} N(d_2) \qquad"
        r"P = K e^{-rT} N(-d_2) - S e^{-qT} N(-d_1)"
    )
    st.latex(
        r"d_1 = \frac{\ln(S/K) + (r - q + \frac{\sigma^2}{2})T}{\sigma\sqrt{T}} "
        r"\qquad d_2 = d_1 - \sigma\sqrt{T}"
    )

    st.markdown("**Inputs**")
    st.latex(
        rf"T = \frac{{\text{{days}}}}{{\text{{basis}}}} = "
        rf"\frac{{{days_to_expiry}}}{{{basis_value}}} = {_n(b.time_to_expiry)}"
    )
    st.latex(
        rf"S = {_n(b.spot, 4)} \qquad K = {_n(b.strike, 4)} \qquad "
        rf"\sigma = {_n(b.volatility * 100, 4)}\% = {_n(b.volatility)}"
    )
    st.latex(
        rf"r = {_n(b.risk_free_rate * 100, 4)}\% = {_n(b.risk_free_rate)} \qquad "
        rf"q = {_n(b.dividend_yield * 100, 4)}\% = {_n(b.dividend_yield)}"
    )

    st.markdown("**Discount factors**")
    st.latex(
        rf"e^{{-qT}} = e^{{-{_n(b.dividend_yield)} \times {_n(b.time_to_expiry)}}} "
        rf"= {_n(b.discount_spot)}"
    )
    st.latex(
        rf"e^{{-rT}} = e^{{-{_n(b.risk_free_rate)} \times {_n(b.time_to_expiry)}}} "
        rf"= {_n(b.discount_strike)}"
    )
    st.latex(
        rf"S e^{{-qT}} = {_n(b.spot, 4)} \times {_n(b.discount_spot)} "
        rf"= {_n(b.spot_discounted, 4)}"
    )
    st.latex(
        rf"K e^{{-rT}} = {_n(b.strike, 4)} \times {_n(b.discount_strike)} "
        rf"= {_n(b.strike_discounted, 4)}"
    )

    if b.d1 is None:
        st.markdown("**Expiry / zero-volatility limit**")
        st.latex(
            rf"C = {_n(b.result.call_price, 4)} \qquad P = {_n(b.result.put_price, 4)}"
        )
        return

    st.markdown("**d₁ and d₂**")
    st.latex(
        rf"\ln\!\left(\frac{{S}}{{K}}\right) = "
        rf"\ln\!\left(\frac{{{_n(b.spot, 4)}}}{{{_n(b.strike, 4)}}}\right) = {_n(b.log_sk)}"
    )
    st.latex(
        rf"\frac{{\sigma^2}}{{2}} = \frac{{{_n(b.volatility)}^2}}{{2}} = {_n(b.variance_half)}"
    )
    st.latex(
        rf"r - q + \frac{{\sigma^2}}{{2}} = "
        rf"{_n(b.risk_free_rate)} - {_n(b.dividend_yield)} + {_n(b.variance_half)} "
        rf"= {_n(b.rate_adjustment)}"
    )
    st.latex(
        rf"(r - q + \frac{{\sigma^2}}{{2}})T = "
        rf"{_n(b.rate_adjustment)} \times {_n(b.time_to_expiry)} = {_n(b.drift_term)}"
    )
    st.latex(
        rf"\sqrt{{T}} = \sqrt{{{_n(b.time_to_expiry)}}} = {_n(b.sqrt_time)} \qquad "
        rf"\sigma\sqrt{{T}} = {_n(b.volatility)} \times {_n(b.sqrt_time)} = {_n(b.vol_sqrt_time)}"
    )
    st.latex(
        rf"d_1 = \frac{{{_n(b.log_sk)} + {_n(b.drift_term)}}}{{{_n(b.vol_sqrt_time)}}} "
        rf"= {_n(b.d1)}"
    )
    st.latex(rf"d_2 = d_1 - \sigma\sqrt{{T}} = {_n(b.d1)} - {_n(b.vol_sqrt_time)} = {_n(b.d2)}")

    st.markdown("**Normal CDF terms**")
    st.latex(rf"N(d_1) = \Phi({_n(b.d1)}) = {_n(b.nd1)}")
    st.latex(rf"N(d_2) = \Phi({_n(b.d2)}) = {_n(b.nd2)}")
    st.latex(rf"N(-d_1) = \Phi({_n(-b.d1)}) = {_n(b.n_neg_d1)}")
    st.latex(rf"N(-d_2) = \Phi({_n(-b.d2)}) = {_n(b.n_neg_d2)}")

    st.markdown("**Call price**")
    st.latex(
        rf"S e^{{-qT}} N(d_1) = {_n(b.spot_discounted, 4)} \times {_n(b.nd1)} "
        rf"= {_n(b.call_term_spot, 4)}"
    )
    st.latex(
        rf"K e^{{-rT}} N(d_2) = {_n(b.strike_discounted, 4)} \times {_n(b.nd2)} "
        rf"= {_n(b.call_term_strike, 4)}"
    )
    st.latex(
        rf"C = {_n(b.call_term_spot, 4)} - {_n(b.call_term_strike, 4)} "
        rf"= \mathbf{{{_n(b.result.call_price, 4)}}}"
    )

    st.markdown("**Put price**")
    st.latex(
        rf"K e^{{-rT}} N(-d_2) = {_n(b.strike_discounted, 4)} \times {_n(b.n_neg_d2)} "
        rf"= {_n(b.put_term_strike, 4)}"
    )
    st.latex(
        rf"S e^{{-qT}} N(-d_1) = {_n(b.spot_discounted, 4)} \times {_n(b.n_neg_d1)} "
        rf"= {_n(b.put_term_spot, 4)}"
    )
    st.latex(
        rf"P = {_n(b.put_term_strike, 4)} - {_n(b.put_term_spot, 4)} "
        rf"= \mathbf{{{_n(b.result.put_price, 4)}}}"
    )


def _render_greeks_math(breakdown) -> None:
    """Render Greek derivations as LaTeX formulas."""
    if breakdown.d1 is None or breakdown.pdf_d1 is None:
        return

    b = breakdown
    result = b.result
    common_theta = (
        -(b.spot * b.discount_spot * b.pdf_d1 * b.volatility) / (2.0 * b.sqrt_time)
    )
    call_theta_inner = (
        common_theta
        - b.risk_free_rate * b.strike * b.discount_strike * b.nd2
        + b.dividend_yield * b.spot * b.discount_spot * b.nd1
    )
    put_theta_inner = (
        common_theta
        + b.risk_free_rate * b.strike * b.discount_strike * b.n_neg_d2
        - b.dividend_yield * b.spot * b.discount_spot * b.n_neg_d1
    )

    st.markdown("#### Greek calculation")
    st.latex(rf"\phi(d_1) = \frac{{1}}{{\sqrt{{2\pi}}}} e^{{-d_1^2/2}} = {_n(b.pdf_d1)}")
    st.latex(
        rf"\Delta_{{\text{{call}}}} = e^{{-qT}} N(d_1) = "
        rf"{_n(b.discount_spot)} \times {_n(b.nd1)} = {_n(result.call_delta)}"
    )
    st.latex(
        rf"\Delta_{{\text{{put}}}} = e^{{-qT}} (N(d_1) - 1) = "
        rf"{_n(b.discount_spot)} \times ({_n(b.nd1)} - 1) = {_n(result.put_delta)}"
    )
    st.latex(
        rf"\Gamma = \frac{{e^{{-qT}} \phi(d_1)}}{{S \sigma \sqrt{{T}}}} = "
        rf"\frac{{{_n(b.discount_spot)} \times {_n(b.pdf_d1)}}}"
        rf"{{{_n(b.spot, 4)} \times {_n(b.volatility)} \times {_n(b.sqrt_time)}}} "
        rf"= {_n(result.gamma)}"
    )
    st.latex(
        rf"\mathcal{{V}} = \frac{{S e^{{-qT}} \phi(d_1) \sqrt{{T}}}}{{100}} = "
        rf"\frac{{{_n(b.spot, 4)} \times {_n(b.discount_spot)} \times {_n(b.pdf_d1)} "
        rf"\times {_n(b.sqrt_time)}}}{{100}} = {_n(result.vega)}"
    )
    st.latex(
        rf"\Theta_{{\text{{call}}}} = \frac{{1}}{{365}}\left[ "
        rf"-\frac{{S e^{{-qT}} \phi(d_1) \sigma}}{{2\sqrt{{T}}}} "
        rf"- r K e^{{-rT}} N(d_2) + q S e^{{-qT}} N(d_1) \right] "
        rf"= \frac{{{_n(call_theta_inner)}}}{{365}} = {_n(result.call_theta)}"
    )
    st.latex(
        rf"\Theta_{{\text{{put}}}} = \frac{{1}}{{365}}\left[ "
        rf"-\frac{{S e^{{-qT}} \phi(d_1) \sigma}}{{2\sqrt{{T}}}} "
        rf"+ r K e^{{-rT}} N(-d_2) - q S e^{{-qT}} N(-d_1) \right] "
        rf"= \frac{{{_n(put_theta_inner)}}}{{365}} = {_n(result.put_theta)}"
    )
    st.latex(
        rf"\rho_{{\text{{call}}}} = \frac{{K T e^{{-rT}} N(d_2)}}{{100}} = "
        rf"\frac{{{_n(b.strike, 4)} \times {_n(b.time_to_expiry)} \times {_n(b.discount_strike)} "
        rf"\times {_n(b.nd2)}}}{{100}} = {_n(result.call_rho)}"
    )
    st.latex(
        rf"\rho_{{\text{{put}}}} = \frac{{-K T e^{{-rT}} N(-d_2)}}{{100}} = "
        rf"\frac{{-{_n(b.strike, 4)} \times {_n(b.time_to_expiry)} \times {_n(b.discount_strike)} "
        rf"\times {_n(b.n_neg_d2)}}}{{100}} = {_n(result.put_rho)}"
    )


def _render_calculation_breakdown(
    breakdown,
    contract: ListedOptionContract,
    currency: str,
    basis_value: int,
    days_to_expiry: int,
):
    result = breakdown.result
    is_call = contract.option_type == "call"
    model_price = result.call_price if is_call else result.put_price
    intrinsic = result.call_intrinsic if is_call else result.put_intrinsic
    time_value = result.call_time_value if is_call else result.put_time_value
    market_mid = contract.midpoint

    st.markdown("#### Black-Scholes result")
    cols = st.columns(4)
    cols[0].metric(f"Model {contract.option_type.upper()} price", _format_money(model_price, currency))
    cols[1].metric("Intrinsic value", _format_money(intrinsic, currency))
    cols[2].metric("Time value", _format_money(time_value, currency))
    cols[3].metric(
        "Model − midpoint",
        _format_money(model_price - market_mid if market_mid is not None else None, currency),
    )

    if market_mid is not None and market_mid > 0:
        pct_diff = abs(model_price - market_mid) / market_mid
        st.caption(
            f"Market midpoint: {_format_money(market_mid, currency)} · "
            f"Absolute diff: {_format_money(abs(model_price - market_mid), currency)} · "
            f"Pct diff: {_format_percent(pct_diff)}"
        )
    if contract.ask is not None:
        model_edge = model_price - contract.ask
        st.caption(
            f"Model edge (theoretical − ask): {_format_money(model_edge, currency)} — "
            "research metric only, not a trade recommendation."
        )

    _render_pricing_math(
        breakdown,
        days_to_expiry=days_to_expiry,
        basis_value=basis_value,
    )
    _render_greeks_math(breakdown)

    st.markdown("#### Option Greeks (summary)")
    greeks = pd.DataFrame(
        [
            {
                "Measure": "Delta",
                "Call": result.call_delta,
                "Put": result.put_delta,
                "Selected": result.call_delta if is_call else result.put_delta,
            },
            {
                "Measure": "Gamma",
                "Call": result.gamma,
                "Put": result.gamma,
                "Selected": result.gamma,
            },
            {
                "Measure": "Vega (per 1 vol pt)",
                "Call": result.vega,
                "Put": result.vega,
                "Selected": result.vega,
            },
            {
                "Measure": "Theta / day",
                "Call": result.call_theta,
                "Put": result.put_theta,
                "Selected": result.call_theta if is_call else result.put_theta,
            },
            {
                "Measure": "Rho (per 1 rate pt)",
                "Call": result.call_rho,
                "Put": result.put_rho,
                "Selected": result.call_rho if is_call else result.put_rho,
            },
        ]
    )
    st.dataframe(
        greeks,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Call": st.column_config.NumberColumn(format="%.6f"),
            "Put": st.column_config.NumberColumn(format="%.6f"),
            "Selected": st.column_config.NumberColumn(format="%.6f"),
        },
    )


def _build_payoff_chart(spot, strike, premium, option_side):
    low = max(0.01, spot * 0.55)
    high = max(strike * 1.35, spot * 1.45, low + 1)
    prices = [low + (high - low) * index / 100 for index in range(101)]

    if option_side == "Call":
        long_pnl = [max(price - strike, 0) - premium for price in prices]
    else:
        long_pnl = [max(strike - price, 0) - premium for price in prices]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=prices,
            y=long_pnl,
            name=f"Long {option_side}",
            line={"color": "#2fffb2", "width": 3},
        )
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
    fig.add_vline(x=strike, line_dash="dash", line_color="#fbbf24", annotation_text="Strike")
    fig.add_vline(x=spot, line_dash="dot", line_color="#51d7ff", annotation_text="Spot")
    fig.update_layout(
        height=380,
        margin={"l": 8, "r": 8, "t": 20, "b": 8},
        xaxis_title="Underlying at expiration",
        yaxis_title="P&L",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _render_volatility_sources(
    symbol: str,
    contract: ListedOptionContract,
    hist_profile: dict[int, RealizedVolatilitySnapshot],
) -> None:
    """Show chain IV vs realized vol and one-click apply buttons."""
    chain_iv = normalize_implied_volatility(contract.implied_volatility)

    st.markdown("##### Volatility context")
    st.caption(
        "Compare the model to the market **mid** using **historical realized vol** (recent price swings). "
        "Chain IV is the σ that reproduces the mid — Black-Scholes will match mid if you use it."
    )

    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric(
            "Chain IV",
            f"{chain_iv * 100:.1f}%" if chain_iv else "—",
            help="Implied volatility from the selected contract.",
        )

    for idx, window in enumerate(sorted(hist_profile.keys()), start=1):
        if idx >= len(metric_cols):
            break
        snap = hist_profile[window]
        with metric_cols[idx]:
            st.metric(
                f"{window}d realized σ",
                f"{snap.annualized_vol * 100:.1f}%",
                help=(
                    f"Annualized log-return vol over the last {window} trading days "
                    f"({snap.sample_size} daily bars, ~{snap.lookback_days} calendar days fetched)."
                ),
            )

    if hist_profile:
        sample = next(iter(hist_profile.values()))
        st.caption(
            f"Historical σ from {sample.start_date} → {sample.end_date} daily closes ({symbol})."
        )

    apply_cols = st.columns(max(len(hist_profile), 1) + 1)
    with apply_cols[0]:
        if st.button("Use chain IV", key=f"bs_vol_src_chain_{contract.contract_symbol}"):
            if chain_iv:
                st.session_state.bs_vol_pct = chain_iv * 100
                st.rerun()
    for idx, window in enumerate(sorted(hist_profile.keys()), start=1):
        snap = hist_profile[window]
        with apply_cols[idx]:
            if st.button(
                f"Use {window}d hist σ",
                key=f"bs_vol_src_{window}_{contract.contract_symbol}",
            ):
                st.session_state.bs_vol_pct = snap.annualized_vol * 100
                st.rerun()

    if chain_iv and 30 in hist_profile:
        hist30 = hist_profile[30].annualized_vol
        diff_pts = (chain_iv - hist30) * 100
        if chain_iv > hist30 * 1.15:
            st.info(
                f"Chain IV ({chain_iv * 100:.1f}%) is **{diff_pts:.1f} pts** above "
                f"30-day realized ({hist30 * 100:.1f}%) — the market may be pricing elevated vol."
            )
        elif chain_iv < hist30 * 0.85:
            st.info(
                f"Chain IV ({chain_iv * 100:.1f}%) is **{abs(diff_pts):.1f} pts** below "
                f"30-day realized ({hist30 * 100:.1f}%) — options may look cheap vs recent history."
            )


def _render_pricing_panel(
    contract: ListedOptionContract,
    spot_from_quote: float | None,
    currency: str,
    symbol: str,
    hist_profile: dict[int, RealizedVolatilitySnapshot],
):
    """Editable assumptions pre-filled from the selected contract; run Black-Scholes."""
    st.markdown("#### Pricing assumptions")
    st.caption("Values below are pre-filled from the selected row. Adjust any input before running the model.")

    iv_default = normalize_implied_volatility(contract.implied_volatility)
    if iv_default is None or iv_default <= 0:
        iv_default = DEFAULT_VOLATILITY

    contract_key = contract.contract_symbol
    if st.session_state.get("bs_active_contract") != contract_key:
        st.session_state.bs_active_contract = contract_key
        st.session_state.bs_vol_pct = float(iv_default * 100)

    if hist_profile:
        _render_volatility_sources(symbol, contract, hist_profile)
    else:
        st.caption("Historical volatility unavailable — enter σ manually or use chain IV below.")

    left, right = st.columns(2)
    with left:
        use_live_spot = st.checkbox(
            "Use live underlying price",
            value=spot_from_quote is not None,
            key="bs_use_live_spot",
        )
        if use_live_spot and spot_from_quote is not None:
            spot = spot_from_quote
            st.metric("Underlying (S)", _format_money(spot, currency))
        else:
            spot = st.number_input(
                "Underlying (S)",
                min_value=0.01,
                value=float(spot_from_quote or 100.0),
                step=0.5,
                key="bs_spot",
            )

        strike = st.number_input(
            "Strike (K)",
            min_value=0.01,
            value=float(contract.strike),
            step=0.5,
            key="bs_strike",
        )
        days_to_expiry = st.number_input(
            "Days to expiration",
            min_value=0,
            value=int(contract.days_to_expiration),
            step=1,
            key="bs_dte",
        )

    with right:
        volatility_pct = st.number_input(
            "Volatility σ (%)",
            min_value=0.0,
            step=0.5,
            help="Defaults to chain IV. Use a historical σ above for meaningful model vs mid comparison.",
            key="bs_vol_pct",
        )
        rate_pct = st.number_input(
            "Risk-free rate r (%)",
            value=float(DEFAULT_RATE * 100),
            step=0.25,
            key="bs_rate",
        )
        dividend_pct = st.number_input(
            "Dividend yield q (%)",
            value=0.0,
            step=0.25,
            key="bs_div",
        )
        basis = st.radio(
            "Day-count basis",
            ["Calendar (365)", "Trading (252)"],
            horizontal=True,
            key="bs_basis",
        )
        basis_value = 252 if "252" in basis else 365

    run_calculation = st.button("Run Black-Scholes", type="primary", width="stretch")

    if not run_calculation:
        st.info("Adjust assumptions if needed, then click **Run Black-Scholes**.")
        return

    time_to_expiry = years_from_days(days_to_expiry, basis=basis_value)
    breakdown = calculate_black_scholes_breakdown(
        spot=spot,
        strike=strike,
        time_to_expiry=time_to_expiry,
        volatility=volatility_pct / 100,
        risk_free_rate=rate_pct / 100,
        dividend_yield=dividend_pct / 100,
    )

    _render_calculation_breakdown(
        breakdown,
        contract,
        currency,
        basis_value,
        days_to_expiry=int(days_to_expiry),
    )

    option_side = "Call" if contract.option_type == "call" else "Put"
    premium = breakdown.result.call_price if contract.option_type == "call" else breakdown.result.put_price
    with st.expander("Payoff at expiration", expanded=False):
        st.plotly_chart(
            _build_payoff_chart(spot, strike, premium, option_side),
            use_container_width=True,
        )
        breakeven = strike + premium if contract.option_type == "call" else strike - premium
        st.caption(f"Model breakeven: {_format_money(breakeven, currency)}")


def render_black_scholes_page(inputs):
    """Render the redesigned Black-Scholes page."""
    st.subheader("Black-Scholes Calculator")
    st.caption(
        "Browse listed option contracts, select a row, then run a full Black-Scholes breakdown "
        "with assumptions pulled from the chain."
    )

    top_left, top_right = st.columns([3, 1])
    with top_left:
        symbol = st.text_input(
            "Ticker",
            value=inputs.get("symbol", "AAPL"),
            help="Yahoo Finance symbol, e.g. AAPL, SPY, MSFT.",
        ).strip().upper()
    with top_right:
        st.write("")
        st.write("")
        if st.button("Refresh market data", width="stretch"):
            clear_options_cache()
            st.rerun()

    if not symbol:
        st.error("Enter a ticker symbol.")
        return

    try:
        quote = fetch_live_quote(symbol)
        expirations = fetch_expirations(symbol)
    except Exception as exc:
        st.error(f"Unable to load Yahoo Finance data for {symbol}: {exc}")
        return

    currency, spot_from_quote = _render_quote_strip(quote, symbol)

    if not expirations:
        st.warning("No option expirations listed for this symbol.")
        return

    filter_col1, filter_col2 = st.columns([1.2, 1])
    with filter_col1:
        selected_expiration = st.selectbox("Expiration", expirations, key="bs_expiration")
    with filter_col2:
        type_filter = st.radio(
            "Contract type",
            ["All", "Calls", "Puts"],
            horizontal=True,
            key="bs_type_filter",
        )

    include_calls = type_filter in ("All", "Calls")
    include_puts = type_filter in ("All", "Puts")

    st.markdown('<div class="section-label">Option chain</div>', unsafe_allow_html=True)
    try:
        with st.spinner("Loading option chain..."):
            contracts = _load_contracts(symbol, selected_expiration, include_calls, include_puts)
    except Exception as exc:
        st.error(f"Could not load option chain: {exc}")
        return

    dte = max((datetime.strptime(selected_expiration, "%Y-%m-%d").date() - date.today()).days, 0)
    selected_contract = _render_contract_table(
        contracts,
        spot=spot_from_quote,
        symbol=symbol,
        expiration=selected_expiration,
        dte=dte,
    )

    st.divider()

    if selected_contract is None:
        st.info("Select a contract in the table above to configure pricing and view the calculation breakdown.")
        return

    _render_selected_contract_summary(selected_contract, currency)

    try:
        with st.spinner("Loading historical volatility..."):
            hist_profile = fetch_realized_volatility_profile(symbol)
    except Exception as exc:
        hist_profile = {}
        st.warning(f"Could not load historical volatility for {symbol}: {exc}")

    _render_pricing_panel(
        selected_contract,
        spot_from_quote,
        currency,
        symbol=symbol,
        hist_profile=hist_profile,
    )
