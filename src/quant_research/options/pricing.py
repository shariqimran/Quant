"""Option pricing models used by the Streamlit calculators.

The Streamlit pages should stay mostly concerned with input/output rendering.
Keeping the pricing formulas in this module makes the math testable without a
browser session and reduces the chance that UI changes silently alter results.
"""

from dataclasses import dataclass
from math import erf, exp, log, pi, sqrt

import numpy as np


TRADING_DAYS_PER_YEAR = 252
CALENDAR_DAYS_PER_YEAR = 365


@dataclass(frozen=True)
class BlackScholesResult:
    """Calculated option values and Greeks."""

    call_price: float
    put_price: float
    call_delta: float
    put_delta: float
    gamma: float
    vega: float
    call_theta: float
    put_theta: float
    call_rho: float
    put_rho: float
    call_intrinsic: float
    put_intrinsic: float
    call_time_value: float
    put_time_value: float
    d1: float | None
    d2: float | None


@dataclass(frozen=True)
class BinomialInputs:
    """Validated inputs used by the Cox-Ross-Rubinstein binomial model."""

    spot: float
    strike: float
    time_to_expiry: float
    volatility: float
    risk_free_rate: float
    dividend_yield: float
    steps: int
    option_type: str
    exercise_style: str


@dataclass(frozen=True)
class BinomialResult:
    """Price, Greeks, and tree diagnostics from the binomial model."""

    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    intrinsic: float
    time_value: float
    early_exercise_premium: float
    up_factor: float
    down_factor: float
    risk_neutral_probability: float
    discount_factor: float
    dt: float
    steps: int
    option_type: str
    exercise_style: str
    stock_tree_preview: list[list[float]]
    option_tree_preview: list[list[float]]


@dataclass(frozen=True)
class MonteCarloResult:
    """European risk-neutral simulation result."""

    price: float
    standard_error: float
    confidence_low: float
    confidence_high: float
    paths: int
    seed: int
    option_type: str


def _norm_cdf(value):
    """Standard normal cumulative distribution function."""
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))


def _norm_pdf(value):
    """Standard normal probability density function."""
    return exp(-0.5 * value * value) / sqrt(2.0 * pi)


def years_from_days(days, basis=CALENDAR_DAYS_PER_YEAR):
    """Convert days to year fraction."""
    if basis <= 0:
        raise ValueError("basis must be positive.")
    return max(float(days), 0.0) / float(basis)


def _validate_inputs(spot, strike, time_to_expiry, volatility):
    if spot <= 0:
        raise ValueError("spot must be positive.")
    if strike <= 0:
        raise ValueError("strike must be positive.")
    if time_to_expiry < 0:
        raise ValueError("time_to_expiry cannot be negative.")
    if volatility < 0:
        raise ValueError("volatility cannot be negative.")


def _validate_binomial_inputs(
    spot,
    strike,
    time_to_expiry,
    volatility,
    risk_free_rate,
    dividend_yield,
    steps,
    option_type,
    exercise_style,
):
    """Normalize and validate user/model inputs before building the tree."""
    spot = float(spot)
    strike = float(strike)
    time_to_expiry = float(time_to_expiry)
    volatility = float(volatility)
    risk_free_rate = float(risk_free_rate)
    dividend_yield = float(dividend_yield)
    steps = int(steps)
    option_type = str(option_type).strip().lower()
    exercise_style = str(exercise_style).strip().lower()

    _validate_inputs(spot, strike, time_to_expiry, volatility)
    if steps < 1:
        raise ValueError("steps must be at least 1.")
    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'.")
    if exercise_style not in {"european", "american"}:
        raise ValueError("exercise_style must be 'european' or 'american'.")

    return BinomialInputs(
        spot=spot,
        strike=strike,
        time_to_expiry=time_to_expiry,
        volatility=volatility,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
        steps=steps,
        option_type=option_type,
        exercise_style=exercise_style,
    )


def _deterministic_value(spot, strike, time_to_expiry, risk_free_rate, dividend_yield):
    discounted_spot = spot * exp(-dividend_yield * time_to_expiry)
    discounted_strike = strike * exp(-risk_free_rate * time_to_expiry)
    call_price = max(discounted_spot - discounted_strike, 0.0)
    put_price = max(discounted_strike - discounted_spot, 0.0)
    call_intrinsic = max(spot - strike, 0.0)
    put_intrinsic = max(strike - spot, 0.0)
    return BlackScholesResult(
        call_price=call_price,
        put_price=put_price,
        call_delta=1.0 if call_price > 0 else 0.0,
        put_delta=-1.0 if put_price > 0 else 0.0,
        gamma=0.0,
        vega=0.0,
        call_theta=0.0,
        put_theta=0.0,
        call_rho=0.0,
        put_rho=0.0,
        call_intrinsic=call_intrinsic,
        put_intrinsic=put_intrinsic,
        call_time_value=call_price - call_intrinsic,
        put_time_value=put_price - put_intrinsic,
        d1=None,
        d2=None,
    )


def calculate_black_scholes(
    spot,
    strike,
    time_to_expiry,
    volatility,
    risk_free_rate=0.0,
    dividend_yield=0.0,
):
    """
    Price European call and put options with continuous rates/yields.

    Volatility, risk-free rate, dividend yield, and time are annualized decimals.
    Vega and rho are returned per 1 percentage-point move. Theta is per calendar day.
    """
    spot = float(spot)
    strike = float(strike)
    time_to_expiry = float(time_to_expiry)
    volatility = float(volatility)
    risk_free_rate = float(risk_free_rate)
    dividend_yield = float(dividend_yield)
    _validate_inputs(spot, strike, time_to_expiry, volatility)

    if time_to_expiry == 0 or volatility == 0:
        return _deterministic_value(
            spot,
            strike,
            time_to_expiry,
            risk_free_rate,
            dividend_yield,
        )

    sqrt_time = sqrt(time_to_expiry)
    discount_spot = exp(-dividend_yield * time_to_expiry)
    discount_strike = exp(-risk_free_rate * time_to_expiry)
    d1 = (
        log(spot / strike)
        + (risk_free_rate - dividend_yield + 0.5 * volatility * volatility) * time_to_expiry
    ) / (volatility * sqrt_time)
    d2 = d1 - volatility * sqrt_time

    call_price = spot * discount_spot * _norm_cdf(d1) - strike * discount_strike * _norm_cdf(d2)
    put_price = strike * discount_strike * _norm_cdf(-d2) - spot * discount_spot * _norm_cdf(-d1)

    common_gamma = discount_spot * _norm_pdf(d1) / (spot * volatility * sqrt_time)
    common_theta = -(spot * discount_spot * _norm_pdf(d1) * volatility) / (2.0 * sqrt_time)

    call_theta = (
        common_theta
        - risk_free_rate * strike * discount_strike * _norm_cdf(d2)
        + dividend_yield * spot * discount_spot * _norm_cdf(d1)
    ) / CALENDAR_DAYS_PER_YEAR
    put_theta = (
        common_theta
        + risk_free_rate * strike * discount_strike * _norm_cdf(-d2)
        - dividend_yield * spot * discount_spot * _norm_cdf(-d1)
    ) / CALENDAR_DAYS_PER_YEAR

    call_intrinsic = max(spot - strike, 0.0)
    put_intrinsic = max(strike - spot, 0.0)

    return BlackScholesResult(
        call_price=call_price,
        put_price=put_price,
        call_delta=discount_spot * _norm_cdf(d1),
        put_delta=discount_spot * (_norm_cdf(d1) - 1.0),
        gamma=common_gamma,
        vega=spot * discount_spot * _norm_pdf(d1) * sqrt_time / 100.0,
        call_theta=call_theta,
        put_theta=put_theta,
        call_rho=strike * time_to_expiry * discount_strike * _norm_cdf(d2) / 100.0,
        put_rho=-strike * time_to_expiry * discount_strike * _norm_cdf(-d2) / 100.0,
        call_intrinsic=call_intrinsic,
        put_intrinsic=put_intrinsic,
        call_time_value=call_price - call_intrinsic,
        put_time_value=put_price - put_intrinsic,
        d1=d1,
        d2=d2,
    )


def _payoff(stock_price, strike, option_type):
    """Return intrinsic value at a tree node."""
    if option_type == "call":
        return max(stock_price - strike, 0.0)
    return max(strike - stock_price, 0.0)


def _preview_tree(levels, max_levels=6):
    """Keep only the first levels needed for readable UI diagnostics."""
    return [level[:] for level in levels[:max_levels]]


def _build_stock_tree(spot, up_factor, down_factor, steps):
    """Build a recombining stock-price tree.

    Level i contains i + 1 prices. Node j in level i has j up moves and
    i - j down moves, so S(i,j) = S0 * u^j * d^(i-j).
    """
    return [
        [spot * (up_factor**up_moves) * (down_factor ** (step - up_moves)) for up_moves in range(step + 1)]
        for step in range(steps + 1)
    ]


def _calculate_binomial_price_only(
    inputs,
    return_tree=False,
):
    """Calculate the CRR price and optionally return tree diagnostics.

    This internal function is intentionally side-effect free. The public
    function calls it several times for finite-difference Greeks, so it must
    not depend on Streamlit state, network data, or global mutable values.
    """
    spot = inputs.spot
    strike = inputs.strike
    time_to_expiry = inputs.time_to_expiry
    volatility = inputs.volatility
    risk_free_rate = inputs.risk_free_rate
    dividend_yield = inputs.dividend_yield
    steps = inputs.steps
    option_type = inputs.option_type
    exercise_style = inputs.exercise_style

    if time_to_expiry == 0:
        price = _payoff(spot, strike, option_type)
        tree = [[spot]], [[price]]
        return (price, tree) if return_tree else price

    dt = time_to_expiry / steps
    discount_factor = exp(-risk_free_rate * dt)

    # If volatility is zero, the CRR up/down factors collapse to the same
    # value and the usual probability formula divides by zero. The underlying
    # still has a deterministic risk-neutral path under continuous dividend
    # yield, so we roll back one branch per step and still check American
    # exercise at each deterministic node.
    if volatility == 0:
        growth = exp((risk_free_rate - dividend_yield) * dt)
        stock_levels = [[spot * (growth**step)] for step in range(steps + 1)]
        option_values = [_payoff(stock_levels[-1][0], strike, option_type)]
        option_levels = [None for _ in range(steps + 1)]
        option_levels[-1] = option_values[:]

        for step in range(steps - 1, -1, -1):
            continuation = discount_factor * option_values[0]
            exercise = _payoff(stock_levels[step][0], strike, option_type)
            node_value = max(exercise, continuation) if exercise_style == "american" else continuation
            option_values = [node_value]
            option_levels[step] = option_values[:]

        tree = stock_levels, option_levels
        return (option_values[0], tree) if return_tree else option_values[0]

    up_factor = exp(volatility * sqrt(dt))
    down_factor = 1.0 / up_factor
    growth_factor = exp((risk_free_rate - dividend_yield) * dt)
    risk_neutral_probability = (growth_factor - down_factor) / (up_factor - down_factor)

    # CRR requires d < exp((r-q)dt) < u. If this is violated, the model no
    # longer has a valid risk-neutral probability and the result is not a valid
    # arbitrage-free binomial price.
    if not 0.0 <= risk_neutral_probability <= 1.0:
        raise ValueError(
            "Invalid CRR risk-neutral probability. Increase steps, lower dividend yield, "
            "or review rate/volatility assumptions."
        )

    stock_tree = _build_stock_tree(spot, up_factor, down_factor, steps)
    option_values = [_payoff(stock_price, strike, option_type) for stock_price in stock_tree[-1]]
    option_tree = [None for _ in range(steps + 1)]
    option_tree[-1] = option_values[:]

    # Backward induction: each node is the discounted risk-neutral expected
    # value of its two child nodes. American options add an early-exercise check
    # at every node before moving to the previous level.
    for step in range(steps - 1, -1, -1):
        next_values = []
        for node in range(step + 1):
            continuation = discount_factor * (
                risk_neutral_probability * option_values[node + 1]
                + (1.0 - risk_neutral_probability) * option_values[node]
            )
            exercise = _payoff(stock_tree[step][node], strike, option_type)
            next_values.append(max(exercise, continuation) if exercise_style == "american" else continuation)
        option_values = next_values
        option_tree[step] = option_values[:]

    tree = stock_tree, option_tree
    return (option_values[0], tree) if return_tree else option_values[0]


def _finite_difference_greek(inputs, field, bump):
    """Central finite difference for Greeks that are not directly available."""
    base_value = getattr(inputs, field)
    down_value = max(base_value - bump, 0.0) if field in {"spot", "volatility", "time_to_expiry"} else base_value - bump
    up_inputs = inputs.__class__(**{**inputs.__dict__, field: base_value + bump})
    down_inputs = inputs.__class__(**{**inputs.__dict__, field: down_value})
    up_price = _calculate_binomial_price_only(up_inputs)
    down_price = _calculate_binomial_price_only(down_inputs)
    denominator = (base_value + bump) - down_value
    return (up_price - down_price) / denominator if denominator else 0.0


def _calculate_binomial_delta_gamma(inputs, stock_tree, option_tree):
    """Calculate root delta and gamma from the first two tree levels."""
    if inputs.time_to_expiry == 0 or inputs.volatility == 0 or inputs.steps < 2:
        stock_bump = max(inputs.spot * 0.01, 0.01)
        delta = _finite_difference_greek(inputs, "spot", stock_bump)
        up_inputs = inputs.__class__(**{**inputs.__dict__, "spot": inputs.spot + stock_bump})
        down_inputs = inputs.__class__(**{**inputs.__dict__, "spot": max(inputs.spot - stock_bump, 0.01)})
        up_delta = _finite_difference_greek(up_inputs, "spot", stock_bump)
        down_delta = _finite_difference_greek(down_inputs, "spot", stock_bump)
        return delta, (up_delta - down_delta) / (2 * stock_bump)

    delta = (option_tree[1][1] - option_tree[1][0]) / (stock_tree[1][1] - stock_tree[1][0])

    delta_up = (option_tree[2][2] - option_tree[2][1]) / (stock_tree[2][2] - stock_tree[2][1])
    delta_down = (option_tree[2][1] - option_tree[2][0]) / (stock_tree[2][1] - stock_tree[2][0])
    average_stock_gap = 0.5 * (stock_tree[2][2] - stock_tree[2][0])
    gamma = (delta_up - delta_down) / average_stock_gap if average_stock_gap else 0.0
    return delta, gamma


def calculate_binomial_option(
    spot,
    strike,
    time_to_expiry,
    volatility,
    risk_free_rate=0.0,
    dividend_yield=0.0,
    steps=200,
    option_type="call",
    exercise_style="american",
):
    """Price an option with the Cox-Ross-Rubinstein binomial tree model.

    Inputs are annualized decimals: 25% volatility is 0.25, 4.5% rate is 0.045.
    The returned vega and rho are per 1 percentage-point input move. Theta is a
    one-calendar-day time decay estimate, matching the Black-Scholes page.
    """
    inputs = _validate_binomial_inputs(
        spot,
        strike,
        time_to_expiry,
        volatility,
        risk_free_rate,
        dividend_yield,
        steps,
        option_type,
        exercise_style,
    )

    price, (stock_tree, option_tree) = _calculate_binomial_price_only(inputs, return_tree=True)
    intrinsic = _payoff(inputs.spot, inputs.strike, inputs.option_type)

    if inputs.time_to_expiry > 0 and inputs.volatility > 0:
        dt = inputs.time_to_expiry / inputs.steps
        up_factor = exp(inputs.volatility * sqrt(dt))
        down_factor = 1.0 / up_factor
        risk_neutral_probability = (
            exp((inputs.risk_free_rate - inputs.dividend_yield) * dt) - down_factor
        ) / (up_factor - down_factor)
    else:
        dt = inputs.time_to_expiry / inputs.steps
        up_factor = exp((inputs.risk_free_rate - inputs.dividend_yield) * dt)
        down_factor = up_factor
        risk_neutral_probability = 1.0
    discount_factor = exp(-inputs.risk_free_rate * dt) if inputs.time_to_expiry > 0 else 1.0

    delta, gamma = _calculate_binomial_delta_gamma(inputs, stock_tree, option_tree)
    vol_bump = max(0.0001, inputs.volatility * 0.01)
    rate_bump = 0.0001
    day_bump = 1.0 / CALENDAR_DAYS_PER_YEAR

    # Vega and rho use finite differences because binomial trees do not provide
    # closed-form Greeks. Divide by 100 so the result means "per 1 percentage
    # point", e.g. vol 25% -> 26%, not vol 25% -> 125%.
    vega = _finite_difference_greek(inputs, "volatility", vol_bump) / 100.0
    rho = _finite_difference_greek(inputs, "risk_free_rate", rate_bump) / 100.0

    if inputs.time_to_expiry > day_bump:
        shorter_inputs = inputs.__class__(**{**inputs.__dict__, "time_to_expiry": inputs.time_to_expiry - day_bump})
        theta = _calculate_binomial_price_only(shorter_inputs) - price
    else:
        theta = intrinsic - price

    european_price = price
    if inputs.exercise_style == "american":
        european_inputs = inputs.__class__(**{**inputs.__dict__, "exercise_style": "european"})
        european_price = _calculate_binomial_price_only(european_inputs)

    return BinomialResult(
        price=price,
        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
        rho=rho,
        intrinsic=intrinsic,
        time_value=price - intrinsic,
        early_exercise_premium=max(price - european_price, 0.0),
        up_factor=up_factor,
        down_factor=down_factor,
        risk_neutral_probability=risk_neutral_probability,
        discount_factor=discount_factor,
        dt=dt,
        steps=inputs.steps,
        option_type=inputs.option_type,
        exercise_style=inputs.exercise_style,
        stock_tree_preview=_preview_tree(stock_tree),
        option_tree_preview=_preview_tree(option_tree),
    )


def implied_volatility_from_binomial_price(
    target_price,
    spot,
    strike,
    time_to_expiry,
    risk_free_rate=0.0,
    dividend_yield=0.0,
    steps=200,
    option_type="call",
    exercise_style="american",
    lower_volatility=0.0001,
    upper_volatility=5.0,
    tolerance=0.0001,
    max_iterations=100,
):
    """Solve for the volatility that makes the binomial model match a price.

    The solver uses bisection because option value is monotonic with volatility
    for standard vanilla calls and puts. If the target price is outside the
    model's feasible range, ``None`` is returned instead of forcing a misleading
    volatility.
    """
    target_price = float(target_price)
    if target_price <= 0:
        return None

    def price_at(volatility):
        try:
            return calculate_binomial_option(
                spot,
                strike,
                time_to_expiry,
                volatility,
                risk_free_rate,
                dividend_yield,
                steps,
                option_type,
                exercise_style,
            ).price
        except ValueError:
            return None

    # For finite CRR trees, extremely low volatility can violate d < exp((r-q)dt) < u.
    # Move the lower bracket upward until the tree is valid rather than failing
    # the entire implied-volatility solve.
    low = lower_volatility
    low_price = price_at(low)
    while low_price is None and low < upper_volatility:
        low *= 2.0
        low_price = price_at(low)

    high = upper_volatility
    high_price = price_at(high)

    if low_price is None or high_price is None:
        return None

    if target_price < low_price - tolerance or target_price > high_price + tolerance:
        return None

    for _ in range(max_iterations):
        mid = (low + high) / 2.0
        price = price_at(mid)
        if price is None:
            low = mid
            continue
        if abs(price - target_price) <= tolerance:
            return mid
        if price < target_price:
            low = mid
        else:
            high = mid

    return (low + high) / 2.0


def calculate_monte_carlo_option(
    spot,
    strike,
    time_to_expiry,
    volatility,
    risk_free_rate=0.0,
    dividend_yield=0.0,
    paths=20000,
    option_type="call",
    seed=42,
):
    """Price a European option with risk-neutral geometric Brownian simulation.

    This is a cross-check, not a replacement for the binomial tree. Plain Monte
    Carlo prices European terminal payoff well, but American exercise requires
    a different method such as Longstaff-Schwartz regression.
    """
    inputs = _validate_binomial_inputs(
        spot,
        strike,
        time_to_expiry,
        volatility,
        risk_free_rate,
        dividend_yield,
        steps=1,
        option_type=option_type,
        exercise_style="european",
    )
    paths = int(paths)
    seed = int(seed)
    if paths < 100:
        raise ValueError("paths must be at least 100.")

    if inputs.time_to_expiry == 0:
        price = _payoff(inputs.spot, inputs.strike, inputs.option_type)
        return MonteCarloResult(
            price=price,
            standard_error=0.0,
            confidence_low=price,
            confidence_high=price,
            paths=paths,
            seed=seed,
            option_type=inputs.option_type,
        )

    rng = np.random.default_rng(seed)
    shocks = rng.standard_normal(paths)
    drift = (inputs.risk_free_rate - inputs.dividend_yield - 0.5 * inputs.volatility**2) * inputs.time_to_expiry
    diffusion = inputs.volatility * sqrt(inputs.time_to_expiry) * shocks
    terminal_spot = inputs.spot * np.exp(drift + diffusion)

    if inputs.option_type == "call":
        payoffs = np.maximum(terminal_spot - inputs.strike, 0.0)
    else:
        payoffs = np.maximum(inputs.strike - terminal_spot, 0.0)

    discounted = np.exp(-inputs.risk_free_rate * inputs.time_to_expiry) * payoffs
    price = float(np.mean(discounted))
    standard_error = float(np.std(discounted, ddof=1) / sqrt(paths))
    confidence_half_width = 1.96 * standard_error

    return MonteCarloResult(
        price=price,
        standard_error=standard_error,
        confidence_low=price - confidence_half_width,
        confidence_high=price + confidence_half_width,
        paths=paths,
        seed=seed,
        option_type=inputs.option_type,
    )
