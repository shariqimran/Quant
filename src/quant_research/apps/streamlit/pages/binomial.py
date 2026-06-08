"""Binomial option pricing page.

This page intentionally keeps the pricing math in
``src.quant_research.options.pricing`` and focuses on Streamlit inputs,
market-data snapshots, and comparison displays. The separation matters because
pricing formulas should be unit-tested independently from UI behavior.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.quant_research.apps.streamlit.pages.black_scholes import (
    _days_to_expiration,
    _fetch_expirations,
    _fetch_live_quote,
    _fetch_option_chain,
    _format_money,
    _format_number,
    _format_percent,
    _market_mid,
    _nearest_index,
    _render_quote_strip,
    _safe_float,
    _selected_contract_row,
)
from src.quant_research.options import (
    calculate_binomial_option,
    calculate_black_scholes,
    calculate_monte_carlo_option,
    implied_volatility_from_binomial_price,
    years_from_days,
)


DEFAULT_RATE = 0.045
DEFAULT_VOLATILITY = 0.25
DEFAULT_STEPS = 250
DEFAULT_SIMULATION_PATHS = 20000


def _load_binomial_css():
    """Reserved hook for future page-scoped styling.

    The Binomial page intentionally avoids custom dynamic HTML because Streamlit
    can render markdown-indented HTML as visible source text. Native components
    are less fragile and keep the UI readable across app versions.
    """
    return None


def _render_cards(cards, cards_per_row=3):
    """Render readable metric cards using only native Streamlit components."""
    for start in range(0, len(cards), cards_per_row):
        row_cards = cards[start : start + cards_per_row]
        columns = st.columns(len(row_cards))
        for column, card in zip(columns, row_cards):
            with column:
                with st.container(border=True):
                    st.caption(card["label"])
                    st.markdown(f"### {card['value']}")
                    if card.get("note"):
                        st.caption(card["note"])


def _option_label(value):
    """Convert internal option type labels into UI labels."""
    return "Call" if value == "call" else "Put"


def _style_label(value):
    """Convert internal exercise style labels into UI labels."""
    return "American" if value == "american" else "European"


def _selected_black_scholes_price(result, option_type):
    """Black-Scholes prices both sides; this selects the requested side."""
    return result.call_price if option_type == "call" else result.put_price


def _build_tree_preview(stock_tree, option_tree):
    """Flatten the first few tree levels into a readable table.

    The full tree can be very large, for example 500 steps creates more than
    125,000 nodes. The preview shows the first levels needed to verify that the
    tree is recombining and that option values are rolled backward correctly.
    """
    rows = []
    for step, stock_level in enumerate(stock_tree):
        option_level = option_tree[step]
        for node, stock_price in enumerate(stock_level):
            rows.append(
                {
                    "Step": step,
                    "Node": node,
                    "Stock Price": stock_price,
                    "Option Value": option_level[node],
                }
            )
    return pd.DataFrame(rows)


def _build_tree_graph(stock_tree, option_tree):
    """Create a node-link graph for the first tree levels.

    Each node is positioned by step on the x-axis and node index on the y-axis.
    Edges connect each node to its down and up children. The hover text shows
    both the underlying node price and the rolled option value.
    """
    edge_x = []
    edge_y = []
    node_x = []
    node_y = []
    node_text = []
    node_color = []

    levels = len(stock_tree)
    for step in range(levels):
        center = (len(stock_tree[step]) - 1) / 2.0
        for node, stock_price in enumerate(stock_tree[step]):
            y = node - center
            node_x.append(step)
            node_y.append(y)
            option_value = option_tree[step][node]
            node_text.append(f"Step {step}, Node {node}<br>S={stock_price:.2f}<br>V={option_value:.4f}")
            node_color.append(option_value)

            if step < levels - 1:
                child_center = (len(stock_tree[step + 1]) - 1) / 2.0
                down_y = node - child_center
                up_y = (node + 1) - child_center
                edge_x.extend([step, step + 1, None, step, step + 1, None])
                edge_y.extend([y, down_y, None, y, up_y, None])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line={"color": "rgba(148, 163, 184, 0.34)", "width": 1.4},
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            marker={
                "size": 18,
                "color": node_color,
                "colorscale": [[0, "#0f172a"], [0.5, "#51d7ff"], [1, "#2fffb2"]],
                "line": {"color": "rgba(248, 250, 252, 0.85)", "width": 1},
                "colorbar": {"title": "Option"},
            },
            text=node_text,
            hovertemplate="%{text}<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_layout(
        height=460,
        margin={"l": 10, "r": 10, "t": 18, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5, 12, 24, 0.45)",
        xaxis={"title": "Step", "gridcolor": "rgba(148, 163, 184, 0.12)", "dtick": 1},
        yaxis={"title": "Branch", "gridcolor": "rgba(148, 163, 184, 0.08)", "zeroline": False, "showticklabels": False},
    )
    return fig


def _render_formula_reference():
    """Show the formulas used by the CRR binomial tree."""
    with st.expander("Formula reference and validation logic", expanded=False):
        st.markdown(
            """
            **Cox-Ross-Rubinstein tree**

            The model splits the time to expiration `T` into `N` equal steps:

            ```text
            dt = T / N
            u  = exp(sigma * sqrt(dt))
            d  = 1 / u
            p  = (exp((r - q) * dt) - d) / (u - d)
            discount = exp(-r * dt)
            ```

            `S`, `K`, `sigma`, `r`, `q`, `T`, and `N` are spot, strike,
            volatility, risk-free rate, dividend yield, years to expiry, and
            steps. Inputs are annualized decimals internally.

            Terminal payoff:

            ```text
            call payoff = max(S - K, 0)
            put payoff  = max(K - S, 0)
            ```

            Backward induction:

            ```text
            continuation = discount * (p * option_up + (1 - p) * option_down)
            european    = continuation
            american    = max(intrinsic_now, continuation)
            ```

            Validation rule: `p` must be between `0` and `1`. If not, the CRR
            tree is not a valid risk-neutral model for the selected assumptions.
            """
        )


def _render_result_metrics(result, currency, market_mid, bs_price, external_price):
    """Render model price, market comparison, and benchmark comparison."""
    market_edge = result.price - market_mid if market_mid is not None else None
    bs_diff = result.price - bs_price if bs_price is not None else None
    external_diff = result.price - external_price if external_price is not None else None

    _render_cards(
        [
            {"label": "Binomial value", "value": _format_money(result.price, currency), "note": "CRR tree output"},
            {"label": "Market mid", "value": _format_money(market_mid, currency), "note": "Bid/ask midpoint or last"},
            {"label": "Model - mid", "value": _format_money(market_edge, currency), "note": "Positive means model above market"},
            {"label": "Black-Scholes", "value": _format_money(bs_price, currency), "note": "European benchmark"},
            {"label": "Model - external", "value": _format_money(external_diff, currency), "note": "Manual calculator compare"},
        ]
    )

    st.markdown("#### Greeks and Value Breakdown")
    rows = pd.DataFrame(
        [
            {"Metric": "Delta", "Value": result.delta, "Meaning": "Price sensitivity to a $1 spot move"},
            {"Metric": "Gamma", "Value": result.gamma, "Meaning": "Delta sensitivity to spot"},
            {"Metric": "Vega", "Value": result.vega, "Meaning": "Price sensitivity to +1 volatility point"},
            {"Metric": "Theta / day", "Value": result.theta, "Meaning": "One calendar day time decay estimate"},
            {"Metric": "Rho", "Value": result.rho, "Meaning": "Price sensitivity to +1 rate point"},
            {"Metric": "Intrinsic", "Value": result.intrinsic, "Meaning": "Immediate exercise value"},
            {"Metric": "Time value", "Value": result.time_value, "Meaning": "Model price less intrinsic value"},
            {
                "Metric": "Early exercise premium",
                "Value": result.early_exercise_premium,
                "Meaning": "American value less European value",
            },
        ]
    )
    st.dataframe(
        rows,
        width="stretch",
        hide_index=True,
        column_config={"Value": st.column_config.NumberColumn(format="%.6f")},
    )

    if bs_diff is not None:
        st.caption(
            "Black-Scholes is a European closed-form benchmark. A European CRR tree should converge "
            f"toward it as steps increase. Current difference: {_format_money(bs_diff, currency)}."
        )
    if external_price is not None:
        st.caption(
            "External comparison is only as reliable as matching every input exactly: spot, strike, "
            "volatility, rate, dividend yield, days, day-count basis, steps, option type, and style."
        )


def _render_tree_diagnostics(result):
    """Render model internals so formula/data validation is visible."""
    st.markdown("#### Tree Diagnostics")
    _render_cards(
        [
            {"label": "Up factor", "value": _format_number(result.up_factor, 6), "note": "u = exp(sigma sqrt(dt))"},
            {"label": "Down factor", "value": _format_number(result.down_factor, 6), "note": "d = 1 / u"},
            {"label": "Risk-neutral p", "value": _format_number(result.risk_neutral_probability, 6), "note": "Must be inside [0, 1]"},
            {"label": "Discount", "value": _format_number(result.discount_factor, 6), "note": "exp(-r dt)"},
            {"label": "dt", "value": _format_number(result.dt, 6), "note": "T / steps"},
        ]
    )

    if 0 <= result.risk_neutral_probability <= 1:
        st.success("Risk-neutral probability is valid: 0 <= p <= 1.")
    else:
        st.error("Risk-neutral probability is invalid for these assumptions.")

    graph_tab, table_tab = st.tabs(["Visual Tree", "Node Table"])
    with graph_tab:
        st.plotly_chart(_build_tree_graph(result.stock_tree_preview, result.option_tree_preview), width="stretch")
    with table_tab:
        preview = _build_tree_preview(result.stock_tree_preview, result.option_tree_preview)
        st.dataframe(
            preview,
            width="stretch",
            hide_index=True,
            column_config={
                "Stock Price": st.column_config.NumberColumn(format="$%.4f"),
                "Option Value": st.column_config.NumberColumn(format="$%.4f"),
            },
        )


def _render_market_contract_snapshot(row, currency):
    """Render selected live contract data in responsive cards."""
    if row is None:
        st.info("No matching option-chain quote is available for this contract.")
        return

    _render_cards(
        [
            {"label": "Bid", "value": _format_money(row.get("bid"), currency)},
            {"label": "Ask", "value": _format_money(row.get("ask"), currency)},
            {"label": "Last", "value": _format_money(row.get("lastPrice"), currency)},
            {"label": "Mid", "value": _format_money(_market_mid(row), currency)},
            {"label": "Chain IV", "value": _format_percent(row.get("impliedVolatility"))},
            {"label": "Open Int.", "value": _format_number(row.get("openInterest"), 0)},
        ]
    )


def _render_model_iv_cards(model_iv, chain_iv, selected_iv):
    """Show whether market-calibrated IV agrees with chain/user IV."""
    model_iv_note = "Solved from market mid" if model_iv is not None else "Target outside feasible model range"
    chain_note = "Yahoo chain IV" if chain_iv is not None else "Unavailable"
    selected_note = "Used by model"
    chain_diff = model_iv - chain_iv if model_iv is not None and chain_iv is not None else None
    selected_diff = model_iv - selected_iv if model_iv is not None else None
    _render_cards(
        [
            {"label": "Model-implied IV", "value": _format_percent(model_iv), "note": model_iv_note},
            {"label": "Chain IV", "value": _format_percent(chain_iv), "note": chain_note},
            {"label": "Selected IV", "value": _format_percent(selected_iv), "note": selected_note},
            {"label": "Model IV - chain IV", "value": _format_percent(chain_diff), "note": "Calibration gap"},
            {"label": "Model IV - selected IV", "value": _format_percent(selected_diff), "note": "Input gap"},
        ]
    )


def _render_simulation(simulation, bs_price, crr_price, currency):
    """Render Monte Carlo validation output."""
    simulation_diff = simulation.price - bs_price
    crr_diff = crr_price - bs_price
    _render_cards(
        [
            {"label": "Monte Carlo", "value": _format_money(simulation.price, currency), "note": f"{simulation.paths:,} paths"},
            {"label": "95% CI low", "value": _format_money(simulation.confidence_low, currency)},
            {"label": "95% CI high", "value": _format_money(simulation.confidence_high, currency)},
            {"label": "MC - Black-Scholes", "value": _format_money(simulation_diff, currency)},
            {"label": "CRR - Black-Scholes", "value": _format_money(crr_diff, currency)},
        ]
    )
    st.caption(
        "Monte Carlo here simulates European terminal payoff under risk-neutral GBM. "
        "It is a sanity check for European valuation, not an American early-exercise engine."
    )


def _render_external_comparison_inputs(currency):
    """Render external calculator links and manual comparison input.

    Most public calculators do not expose a stable API, so the reliable
    workflow is to open a calculator, copy the exact same inputs, and paste its
    theoretical value here. This avoids fragile HTML scraping and keeps the
    validation path auditable.
    """
    with st.expander("External calculator comparison", expanded=True):
        st.markdown(
            """
            Use these as third-party references, then paste the theoretical value below:

            - [Cboe Options Calculator](https://www.cboe.com/options/tools/options_calculator/)
            - [Pineify Option Pricing Calculator](https://pineify.app/option-pricing-calculator)

            Match all assumptions exactly before comparing. Small differences are normal if the
            external site uses a different day count, dividend convention, tree type, or rounding.
            """
        )
        external_price = st.number_input(
            f"External theoretical price ({currency})",
            min_value=0.0,
            value=0.0,
            step=0.01,
            help="Leave at 0 if you do not want to compare against an external calculator.",
        )
    return external_price if external_price > 0 else None


def render_binomial_page(inputs):
    """Render the binomial option pricing calculator."""
    _load_binomial_css()
    with st.container(border=True):
        st.subheader("Binomial Option Pricing Model")
        st.caption(
            "Cox-Ross-Rubinstein lattice pricing for American or European calls and puts, "
            "calibrated from Yahoo Finance quote and option-chain snapshots with model, "
            "market, Black-Scholes, external-calculator, and Monte Carlo cross-checks."
        )
    st.caption(
        "Market data can be delayed or cached. The model validates assumptions and comparisons; "
        "it does not guarantee exchange-tick real-time quotes."
    )
    _render_formula_reference()

    top_left, top_right = st.columns([3, 1])
    with top_left:
        symbol = st.text_input(
            "Ticker",
            value=inputs.get("symbol", "AAPL"),
            help="Use Yahoo Finance symbols, for example AAPL, SPY, MSFT.",
            key="binomial_symbol",
        ).strip().upper()
    with top_right:
        st.write("")
        st.write("")
        if st.button("Refresh market data", width="stretch", key="binomial_refresh"):
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
    use_live_spot = st.checkbox(
        "Use latest underlying price",
        value=spot_from_quote is not None,
        key="binomial_use_live_spot",
    )

    left, right = st.columns([0.92, 1.08], gap="large")

    with left:
        with st.container(border=True):
            st.markdown("#### Contract")
            option_side = st.radio("Option type", ["Call", "Put"], horizontal=True, key="binomial_side")
            option_type = option_side.lower()
            exercise_style_label = st.radio(
                "Exercise style",
                ["American", "European"],
                horizontal=True,
                help="American options can exercise before expiration; European options exercise only at expiration.",
            )
            exercise_style = exercise_style_label.lower()

            calls = pd.DataFrame()
            puts = pd.DataFrame()
            selected_row = None
            selected_expiration = None
            selected_iv = None

            if expirations:
                selected_expiration = st.selectbox("Expiration", expirations, key="binomial_expiration")
                try:
                    calls, puts = _fetch_option_chain(symbol, selected_expiration)
                except Exception as exc:
                    st.warning(f"Unable to load option chain for {selected_expiration}: {exc}")

            chain_df = calls if option_type == "call" else puts
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
                    key="binomial_chain_strike",
                )
                selected_row = _selected_contract_row(chain_df, selected_strike)
                strike = st.number_input(
                    "Strike price",
                    min_value=0.01,
                    value=float(selected_strike),
                    step=1.0,
                    key="binomial_strike",
                )
            else:
                selected_strike = spot_from_quote or 100.0
                strike = st.number_input(
                    "Strike price",
                    min_value=0.01,
                    value=float(selected_strike),
                    step=1.0,
                    key="binomial_manual_strike",
                )

            days_default = _days_to_expiration(selected_expiration) if selected_expiration else 30
            days_to_expiry = st.number_input(
                "Days until expiration",
                min_value=0,
                value=int(days_default),
                step=1,
                key="binomial_days",
            )

            if selected_row is not None:
                selected_iv = _safe_float(selected_row.get("impliedVolatility"))
                _render_market_contract_snapshot(selected_row, currency)
            elif expirations:
                st.info("No usable strikes were returned for this option chain.")
            else:
                st.info("No listed option expirations were returned. Use manual assumptions below.")

    with right:
        with st.container(border=True):
            st.markdown("#### Model Assumptions")
            if use_live_spot and spot_from_quote is not None:
                spot = spot_from_quote
                _render_cards(
                    [{"label": "Underlying input", "value": _format_money(spot, currency), "note": "Live quote snapshot"}]
                )
            else:
                spot = st.number_input(
                    "Underlying price",
                    min_value=0.01,
                    value=float(spot_from_quote or 100.0),
                    step=1.0,
                    key="binomial_spot",
                )

            vol_default = selected_iv if selected_iv and selected_iv > 0 else DEFAULT_VOLATILITY
            volatility_pct = st.number_input(
                "Volatility",
                min_value=0.0,
                value=float(vol_default * 100),
                step=1.0,
                help="Annualized volatility. Option-chain IV is used as default when available.",
                key="binomial_vol",
            )
            rate_pct = st.number_input("Risk-free rate", value=float(DEFAULT_RATE * 100), step=0.25, key="binomial_rate")
            dividend_pct = st.number_input("Dividend yield", value=0.0, step=0.25, key="binomial_dividend")
            steps = st.number_input(
                "Tree steps",
                min_value=1,
                max_value=2000,
                value=DEFAULT_STEPS,
                step=25,
                help="Higher steps usually improve convergence but increase compute cost.",
                key="binomial_steps",
            )
            simulation_paths = st.number_input(
                "Simulation paths",
                min_value=1000,
                max_value=200000,
                value=DEFAULT_SIMULATION_PATHS,
                step=1000,
                help="Used only for the Monte Carlo validation tab.",
                key="binomial_simulation_paths",
            )
            basis = st.radio(
                "Day count basis",
                ["Calendar days (365)", "Trading days (252)"],
                horizontal=True,
                key="binomial_basis",
            )
            basis_value = 252 if "252" in basis else 365

    external_price = _render_external_comparison_inputs(currency)

    time_to_expiry = years_from_days(days_to_expiry, basis=basis_value)
    try:
        result = calculate_binomial_option(
            spot=spot,
            strike=strike,
            time_to_expiry=time_to_expiry,
            volatility=volatility_pct / 100,
            risk_free_rate=rate_pct / 100,
            dividend_yield=dividend_pct / 100,
            steps=steps,
            option_type=option_type,
            exercise_style=exercise_style,
        )
    except ValueError as exc:
        st.error(f"Invalid binomial model inputs: {exc}")
        st.stop()

    bs_result = calculate_black_scholes(
        spot=spot,
        strike=strike,
        time_to_expiry=time_to_expiry,
        volatility=volatility_pct / 100,
        risk_free_rate=rate_pct / 100,
        dividend_yield=dividend_pct / 100,
    )
    bs_price = _selected_black_scholes_price(bs_result, option_type)
    market_mid = _market_mid(selected_row)
    chain_iv = _safe_float(selected_row.get("impliedVolatility")) if selected_row is not None else None
    selected_iv = volatility_pct / 100
    model_iv = None
    if market_mid is not None:
        try:
            model_iv = implied_volatility_from_binomial_price(
                target_price=market_mid,
                spot=spot,
                strike=strike,
                time_to_expiry=time_to_expiry,
                risk_free_rate=rate_pct / 100,
                dividend_yield=dividend_pct / 100,
                steps=steps,
                option_type=option_type,
                exercise_style=exercise_style,
            )
        except ValueError:
            model_iv = None
    simulation = calculate_monte_carlo_option(
        spot=spot,
        strike=strike,
        time_to_expiry=time_to_expiry,
        volatility=volatility_pct / 100,
        risk_free_rate=rate_pct / 100,
        dividend_yield=dividend_pct / 100,
        paths=simulation_paths,
        option_type=option_type,
        seed=42,
    )

    st.caption(
        f"Inputs: {_style_label(result.exercise_style)} {_option_label(result.option_type)}, "
        f"T={time_to_expiry:.4f} years, steps={result.steps}, vol={volatility_pct:.2f}%, "
        f"rate={rate_pct:.2f}%, dividend={dividend_pct:.2f}%."
    )

    results_tab, diagnostics_tab, simulation_tab, validation_tab = st.tabs(
        ["Results", "Tree Visualizer", "Simulation", "Validation Notes"]
    )
    with results_tab:
        _render_result_metrics(result, currency, market_mid, bs_price, external_price)
        st.markdown("#### Market Calibration")
        _render_model_iv_cards(model_iv, chain_iv, selected_iv)

    with diagnostics_tab:
        _render_tree_diagnostics(result)

    with simulation_tab:
        _render_simulation(simulation, bs_price, result.price, currency)

    with validation_tab:
        st.markdown(
            """
            #### Validation Checklist

            - Spot price comes from the same Yahoo Finance snapshot shown at the top when live spot is enabled.
            - Listed strike, expiration, bid, ask, last, and IV come from the selected Yahoo option chain.
            - Volatility, rate, dividend yield, and day-count basis are editable because different sites use different assumptions.
            - The CRR probability `p` must satisfy `0 <= p <= 1`; otherwise the model refuses to price.
            - European binomial prices should approach Black-Scholes as `steps` increases.
            - American value should be greater than or equal to the matching European value because it has all European exercise rights plus early exercise.
            - External calculator comparisons are meaningful only when every assumption matches exactly.
            """
        )
