"""Black-Scholes pricing for European options."""

from dataclasses import dataclass
from math import erf, exp, log, pi, sqrt


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
<<<<<<< Updated upstream
=======


@dataclass(frozen=True)
class BlackScholesBreakdown:
    """Inputs, intermediate terms, and outputs for UI display."""

    spot: float
    strike: float
    time_to_expiry: float
    volatility: float
    risk_free_rate: float
    dividend_yield: float
    discount_spot: float
    discount_strike: float
    sqrt_time: float
    log_sk: float | None
    variance_half: float | None
    rate_adjustment: float | None
    drift_term: float | None
    vol_sqrt_time: float | None
    d1_numerator: float | None
    d1: float | None
    d2: float | None
    nd1: float | None
    nd2: float | None
    n_neg_d1: float | None
    n_neg_d2: float | None
    pdf_d1: float | None
    spot_discounted: float | None
    strike_discounted: float | None
    call_term_spot: float | None
    call_term_strike: float | None
    put_term_strike: float | None
    put_term_spot: float | None
    result: BlackScholesResult


def calculate_black_scholes_breakdown(
    spot,
    strike,
    time_to_expiry,
    volatility,
    risk_free_rate=0.0,
    dividend_yield=0.0,
):
    """Return Black-Scholes outputs plus intermediate calculation terms."""
    result = calculate_black_scholes(
        spot=spot,
        strike=strike,
        time_to_expiry=time_to_expiry,
        volatility=volatility,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
    )

    spot = float(spot)
    strike = float(strike)
    time_to_expiry = float(time_to_expiry)
    volatility = float(volatility)
    risk_free_rate = float(risk_free_rate)
    dividend_yield = float(dividend_yield)

    discount_spot = exp(-dividend_yield * time_to_expiry)
    discount_strike = exp(-risk_free_rate * time_to_expiry)

    if time_to_expiry == 0 or volatility == 0:
        spot_discounted = spot * discount_spot
        strike_discounted = strike * discount_strike
        return BlackScholesBreakdown(
            spot=spot,
            strike=strike,
            time_to_expiry=time_to_expiry,
            volatility=volatility,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            discount_spot=discount_spot,
            discount_strike=discount_strike,
            sqrt_time=0.0,
            log_sk=None,
            variance_half=None,
            rate_adjustment=None,
            drift_term=None,
            vol_sqrt_time=None,
            d1_numerator=None,
            d1=result.d1,
            d2=result.d2,
            nd1=None,
            nd2=None,
            n_neg_d1=None,
            n_neg_d2=None,
            pdf_d1=None,
            spot_discounted=spot_discounted,
            strike_discounted=strike_discounted,
            call_term_spot=None,
            call_term_strike=None,
            put_term_strike=None,
            put_term_spot=None,
            result=result,
        )

    sqrt_time = sqrt(time_to_expiry)
    d1 = result.d1
    d2 = result.d2
    log_sk = log(spot / strike)
    variance_half = 0.5 * volatility * volatility
    rate_adjustment = risk_free_rate - dividend_yield + variance_half
    drift_term = rate_adjustment * time_to_expiry
    vol_sqrt_time = volatility * sqrt_time
    d1_numerator = log_sk + drift_term
    nd1 = _norm_cdf(d1)
    nd2 = _norm_cdf(d2)
    n_neg_d2 = _norm_cdf(-d2)
    n_neg_d1 = _norm_cdf(-d1)
    pdf_d1 = _norm_pdf(d1)

    spot_discounted = spot * discount_spot
    strike_discounted = strike * discount_strike
    call_term_spot = spot_discounted * nd1
    call_term_strike = strike_discounted * nd2
    put_term_strike = strike_discounted * n_neg_d2
    put_term_spot = spot_discounted * n_neg_d1

    return BlackScholesBreakdown(
        spot=spot,
        strike=strike,
        time_to_expiry=time_to_expiry,
        volatility=volatility,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
        discount_spot=discount_spot,
        discount_strike=discount_strike,
        sqrt_time=sqrt_time,
        log_sk=log_sk,
        variance_half=variance_half,
        rate_adjustment=rate_adjustment,
        drift_term=drift_term,
        vol_sqrt_time=vol_sqrt_time,
        d1_numerator=d1_numerator,
        d1=d1,
        d2=d2,
        nd1=nd1,
        nd2=nd2,
        n_neg_d1=n_neg_d1,
        n_neg_d2=n_neg_d2,
        pdf_d1=pdf_d1,
        spot_discounted=spot_discounted,
        strike_discounted=strike_discounted,
        call_term_spot=call_term_spot,
        call_term_strike=call_term_strike,
        put_term_strike=put_term_strike,
        put_term_spot=put_term_spot,
        result=result,
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
    """Build a recombining stock-price tree."""
    return [
        [
            spot * (up_factor**up_moves) * (down_factor ** (step - up_moves))
            for up_moves in range(step + 1)
        ]
        for step in range(steps + 1)
    ]


def _calculate_binomial_price_only(inputs, return_tree=False):
    """Calculate the CRR price and optionally return tree diagnostics."""
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

    if not 0.0 <= risk_neutral_probability <= 1.0:
        raise ValueError(
            "Invalid CRR risk-neutral probability. Increase steps, lower dividend yield, "
            "or review rate/volatility assumptions."
        )

    stock_tree = _build_stock_tree(spot, up_factor, down_factor, steps)
    option_values = [_payoff(stock_price, strike, option_type) for stock_price in stock_tree[-1]]
    option_tree = [None for _ in range(steps + 1)]
    option_tree[-1] = option_values[:]

    for step in range(steps - 1, -1, -1):
        next_values = []
        for node in range(step + 1):
            continuation = discount_factor * (
                risk_neutral_probability * option_values[node + 1]
                + (1.0 - risk_neutral_probability) * option_values[node]
            )
            exercise = _payoff(stock_tree[step][node], strike, option_type)
            next_values.append(
                max(exercise, continuation) if exercise_style == "american" else continuation
            )
        option_values = next_values
        option_tree[step] = option_values[:]

    tree = stock_tree, option_tree
    return (option_values[0], tree) if return_tree else option_values[0]


def _finite_difference_greek(inputs, field, bump):
    """Central finite difference for Greeks that are not directly available."""
    base_value = getattr(inputs, field)
    down_value = (
        max(base_value - bump, 0.0)
        if field in {"spot", "volatility", "time_to_expiry"}
        else base_value - bump
    )
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
        down_inputs = inputs.__class__(
            **{**inputs.__dict__, "spot": max(inputs.spot - stock_bump, 0.01)}
        )
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
    """Price an option with the Cox-Ross-Rubinstein binomial tree model."""
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

    vega = _finite_difference_greek(inputs, "volatility", vol_bump) / 100.0
    rho = _finite_difference_greek(inputs, "risk_free_rate", rate_bump) / 100.0

    if inputs.time_to_expiry > day_bump:
        shorter_inputs = inputs.__class__(
            **{**inputs.__dict__, "time_to_expiry": inputs.time_to_expiry - day_bump}
        )
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
    """Solve for the volatility that makes the binomial model match a price."""
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
    """Price a European option with risk-neutral geometric Brownian simulation."""
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
>>>>>>> Stashed changes
