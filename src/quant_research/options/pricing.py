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
